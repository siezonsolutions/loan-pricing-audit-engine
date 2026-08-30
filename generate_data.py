import pandas as pd
import numpy as np

def create_synthetic_dataset(num_records=500):
    """Generates synthetic loan lock data for testing the audit engine."""
    np.random.seed(42)  # For reproducible sample data
    
    regions = ['North', 'South', 'East', 'West']
    product_types = ['Conventional', 'FHA', 'VA']
    loan_officers = [f"LO_{i:02d}" for i in range(1, 16)]
    
    data = {
        'loan_id': [f"LN{100000 + i}" for i in range(num_records)],
        'region': np.random.choice(regions, size=num_records),
        'product_type': np.random.choice(product_types, size=num_records, p=[0.6, 0.25, 0.15]),
        'loan_officer': np.random.choice(loan_officers, size=num_records),
        'loan_amount': np.random.choice(np.arange(150000, 750000, 25000), size=num_records),
        'base_rate': np.random.uniform(5.5, 6.25, size=num_records).round(3),
        'llpa_credit_score': np.random.choice([0.0, 0.125, 0.25, 0.375, 0.5], size=num_records),
        'llpa_ltv': np.random.choice([0.0, 0.125, 0.25, 0.5], size=num_records),
        'llpa_property_type': np.random.choice([0.0, 0.125, 0.25], size=num_records, p=[0.7, 0.2, 0.1]),
    }
    
    df = pd.DataFrame(data)
    
    # Calculate required target rate (Base Rate + Total LLPAs)
    llpa_sum = df['llpa_credit_score'] + df['llpa_ltv'] + df['llpa_property_type']
    target_rate = df['base_rate'] + llpa_sum
    
    # Simulate realistic rate locks (including concessions/variances)
    concessions = np.random.choice(
        [0.0, 0.125, 0.25, 0.375, 0.5], 
        size=num_records, 
        p=[0.5, 0.25, 0.15, 0.07, 0.03]
    )
    df['locked_rate'] = (target_rate - concessions).round(3)
    
    return df

# Helper alias so running `python generate_data.py` directly still creates the CSV file
def generate_synthetic_loans():
    df = create_synthetic_dataset()
    df.to_csv("data/synthetic_loan_locks.csv", index=False)
    print("Generated 500 synthetic loan records at: data/synthetic_loan_locks.csv")

if __name__ == "__main__":
    generate_synthetic_loans()
