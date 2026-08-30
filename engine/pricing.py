import pandas as pd
import numpy as np


def audit_loan_data(input_csv_path: str, output_csv_path: str = None, concession_threshold: float = 25.0):
    """
    Audits loan lock data by calculating target rates, rate variances, 
    dollar leakage, and checking against CFPB concession thresholds.
    """
    df = pd.read_csv(input_csv_path)

    # 1. Ensure required columns exist with defaults if missing
    if "base_rate" not in df.columns:
        df["base_rate"] = 6.50
    if "llpa_bps" not in df.columns:
        df["llpa_bps"] = 0.0

    # 2. Calculate Target Rate and Rate Variance
    # LLPA (Loan-Level Price Adjustment) in bps converted to percentage (100 bps = 1.0%)
    df["target_rate"] = df["base_rate"] + (df["llpa_bps"] / 100.0)
    
    # Rate variance in percentage points and basis points
    df["rate_variance"] = df["locked_rate"] - df["target_rate"]
    df["rate_variance_bps"] = (df["rate_variance"] * 100).round(2)

    # 3. Calculate Financial Leakage (Dollar Leakage)
    # Leakage occurs when locked_rate < target_rate (concession/unearned discount given)
    df["dollar_leakage"] = np.where(
        df["rate_variance"] < 0,
        (abs(df["rate_variance"]) / 100.0) * df["loan_amount"],
        0.0
    )

    # 4. CFPB Concession / Compliance Flag (> threshold bps discount)
    # Negative variance beyond threshold indicates non-compliance
    df["compliance_flag"] = df["rate_variance_bps"] < -concession_threshold

    # 5. Save output if destination path is specified
    if output_csv_path:
        df.to_csv(output_csv_path, index=False)

    # 6. Aggregate Summary Metrics
    metrics = {
        "total_loans": int(len(df)),
        "total_leakage": float(df["dollar_leakage"].sum()),
        "avg_rate_variance": float(df["rate_variance_bps"].mean()),
        "flagged_loans_count": int(df["compliance_flag"].sum()),
    }

    return df, metrics


# Backwards compatibility alias if referenced as audit_pricing
audit_pricing = audit_loan_data
