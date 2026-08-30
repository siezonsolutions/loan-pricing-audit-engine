import pandas as pd
import numpy as np

def run_audit(df: pd.DataFrame, cfpb_threshold_bps: float = 25.0) -> dict:
    """
    Audits loan lock records against target pricing, calculates dollar leakage,
    flags fair-lending risk based on a dynamic threshold, and aggregates metrics
    across Loan Officers, Regions, and Product Types.
    """
    audited_df = df.copy()

    # Calculate total required LLPAs
    audited_df['llpa_total'] = (
        audited_df['llpa_credit_score'] + 
        audited_df['llpa_ltv'] + 
        audited_df['llpa_property_type']
    )
    
    # Calculate target rate (Base Market Rate + total LLPAs)
    audited_df['target_rate'] = audited_df['base_rate'] + audited_df['llpa_total']
    
    # Calculate rate variance in basis points (Target Rate minus Locked Rate)
    # Positive variance indicates a concession given to the borrower (leakage)
    audited_df['rate_variance_bps'] = (audited_df['target_rate'] - audited_df['locked_rate']) * 100
    
    # Calculate dollar leakage for positive concessions
    audited_df['dollar_leakage'] = np.where(
        audited_df['rate_variance_bps'] > 0,
        (audited_df['rate_variance_bps'] / 10000) * audited_df['loan_amount'],
        0.0
    )
    
    # Flag regulatory risk based on the configurable threshold
    audited_df['cfpb_risk_flag'] = audited_df['rate_variance_bps'] > cfpb_threshold_bps

    # --- Group Aggregations ---

    # 1. Loan Officer Breakdown
    lo_breakdown = audited_df.groupby('loan_officer').agg(
        total_loans=('loan_id', 'count'),
        total_volume=('loan_amount', 'sum'),
        total_leakage=('dollar_leakage', 'sum'),
        avg_concession_bps=('rate_variance_bps', 'mean'),
        cfpb_flag_count=('cfpb_risk_flag', 'sum')
    ).reset_index().sort_values(by='total_leakage', ascending=False)

    # 2. Region / Branch Breakdown
    region_breakdown = audited_df.groupby('region').agg(
        total_loans=('loan_id', 'count'),
        total_volume=('loan_amount', 'sum'),
        total_leakage=('dollar_leakage', 'sum'),
        avg_concession_bps=('rate_variance_bps', 'mean'),
        cfpb_flag_count=('cfpb_risk_flag', 'sum')
    ).reset_index().sort_values(by='total_leakage', ascending=False)

    # 3. Product Type Breakdown
    product_breakdown = audited_df.groupby('product_type').agg(
        total_loans=('loan_id', 'count'),
        total_volume=('loan_amount', 'sum'),
        total_leakage=('dollar_leakage', 'sum'),
        avg_concession_bps=('rate_variance_bps', 'mean'),
        cfpb_flag_count=('cfpb_risk_flag', 'sum')
    ).reset_index().sort_values(by='total_leakage', ascending=False)

    return {
        "audited_df": audited_df,
        "lo_breakdown": lo_breakdown,
        "region_breakdown": region_breakdown,
        "product_breakdown": product_breakdown,
        "total_leakage": audited_df['dollar_leakage'].sum(),
        "total_cfpb_flags": audited_df['cfpb_risk_flag'].sum(),
        "cfpb_threshold_bps": cfpb_threshold_bps
    }
