# engine/pricing.py
import pandas as pd

def run_pricing_audit(df: pd.DataFrame) -> dict:
    """
    Evaluates loan lock records against expected rates and LLPAs to identify 
    unbacked rate cuts, calculation drift, and margin leakage.
    """
    # 1. Ensure numeric types for calculations
    df['base_rate'] = pd.to_numeric(df['base_rate'], errors='coerce')
    df['total_llpas'] = pd.to_numeric(df['total_llpas'], errors='coerce')
    df['locked_rate'] = pd.to_numeric(df['locked_rate'], errors='coerce')
    df['upb'] = pd.to_numeric(df['upb'], errors='coerce')

    # 2. Expected Rate Calculation = Base Rate + Total LLPAs (expressed as rate equivalent)
    # Note: 100 bps in fee = roughly 0.250% in interest rate equivalent depending on sheet
    df['expected_rate'] = df['base_rate'] + (df['total_llpas'] * 0.25)
    
    # 3. Rate Variance (in Basis Points)
    df['rate_variance_bps'] = (df['locked_rate'] - df['expected_rate']) * 100
    
    # 4. Leakage Dollars Calculation (Unbacked concession/drift over 1 year or upfront price)
    # Bps variance * Loan Amount / 10,000
    df['leakage_dollars'] = df.apply(
        lambda row: abs(row['rate_variance_bps'] * row['upb'] / 10000) 
        if row['rate_variance_bps'] < 0 else 0.0, 
        axis=1
    )

    # 5. CFPB / Fair Lending Disparity Risk Flag (> 25 bps unbacked cut)
    df['cfpb_flag'] = df['rate_variance_bps'] < -25.0

    # 6. Aggregate Summary Output
    summary = {
        "total_loans_audited": len(df),
        "total_leaked_margin_dollars": float(df['leakage_dollars'].sum()),
        "total_leaked_loans": int((df['leakage_dollars'] > 0).sum()),
        "cfpb_disparity_flags": int(df['cfpb_flag'].sum())
    }

    return {
        "summary": summary,
        "audited_dataframe": df
    }
