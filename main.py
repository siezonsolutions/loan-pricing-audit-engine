# main.py
import os
import pandas as pd
from engine.pricing import run_pricing_audit
from engine.report_generator import generate_pdf_report

def run_pipeline():
    # 1. Ensure output folders exist
    os.makedirs("reports", exist_ok=True)
    
    # 2. Load batch loan data
    input_file = "data/synthetic_loan_locks.csv"
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Run dataset generator first.")
        return

    df = pd.read_csv(input_file)

    # 3. Execute Audit Logic
    print("Running pricing verification engine...")
    audit_results = run_pricing_audit(df)

    # 4. Generate Executive PDF
    output_pdf = "reports/Executive_Audit_Summary.pdf"
    generate_pdf_report(audit_results, output_filename=output_pdf)
    print(f"Pipeline complete! Output generated: {output_pdf}")

if __name__ == "__main__":
    run_pipeline()
