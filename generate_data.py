# generate_data.py
import pandas as pd
import numpy as np

def generate_synthetic_loans(num_records=500, filename="data/synthetic_loan_locks.csv"):
    np.random.seed(42)
    
    base_rates = np.random.choice([6.0, 6.25, 6.50, 6.75, 7.0], size=num_records)
    upbs = np.random.choice([250000, 350000, 450000, 550000, 650000], size=num_records)
    llpas = np.random.choice([0.0, 0.25, 0.50, 0.75, 1.0], size=num_records)
    
    # Intentionally inject rate leakage into ~15% of records
    locked_rates = base_rates + (llpas * 0.25)
    leak_indices = np.random.choice(num_records, size=int(num_records * 0.15), replace=False)
    locked_rates[leak_indices] -= np.random.choice([0.25, 0.375, 0.50], size=len(leak_indices))

    df = pd.DataFrame({
        "loan_id": [f"LN{10000 + i}" for i in range(num_records)],
        "upb": upbs,
        "base_rate": base_rates,
        "total_llpas": llpas,
        "locked_rate": locked_rates
    })

    df.to_csv(filename, index=False)
    print(f"Generated {num_records} synthetic loan records at: {filename}")

if __name__ == "__main__":
    generate_synthetic_loans()
