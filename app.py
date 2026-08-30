import os
import io
import tempfile
import pandas as pd
import streamlit as st

# Import core modules
import generate_data
from engine.pricing import audit_loan_data
from engine.report_generator import generate_pdf_report


st.set_page_config(
    page_title="Mortgage Loan Pricing Audit Engine",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def run_pipeline(input_df: pd.DataFrame, concession_threshold: float):
    """Executes audit calculations and generates PDF report bytes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        input_csv_path = os.path.join(temp_dir, "input_locks.csv")
        audited_csv_path = os.path.join(temp_dir, "audited_locks.csv")
        pdf_report_path = os.path.join(temp_dir, "Audit_Summary.pdf")

        # Save uploaded dataframe to temporary CSV
        input_df.to_csv(input_csv_path, index=False)

        # Run core audit logic
        audited_df, metrics = audit_loan_data(
            input_csv_path=input_csv_path,
            output_csv_path=audited_csv_path,
            concession_threshold=concession_threshold,
        )

        # Generate PDF Report
        generate_pdf_report(audited_df, metrics, output_pdf_path=pdf_report_path)

        # Read generated PDF bytes for download
        with open(pdf_report_path, "rb") as f:
            pdf_bytes = f.read()

    return audited_df, metrics, pdf_bytes


# Sidebar Configuration
st.sidebar.title("Configuration")
st.sidebar.subheader("Audit Parameters")

concession_threshold = st.sidebar.number_input(
    "CFPB Concession Threshold (bps)",
    min_value=0.0,
    max_value=100.0,
    value=25.0,
    step=5.0,
    help="Flags loans exceeding this pricing concession threshold.",
)

st.sidebar.markdown("---")
st.sidebar.subheader("Data Input Options")

generate_mock_btn = st.sidebar.button("Generate Synthetic Data (500 Loans)")

# Main Layout
st.title("🏦 Mortgage Loan Pricing Audit Engine")
st.markdown(
    "Upload a loan lock dataset to evaluate interest rate variances, calculate financial leakage, "
    "and identify regulatory compliance risks."
)

uploaded_file = st.file_uploader(
    "Choose a Loan Lock CSV file", type=["csv"], help="Upload CSV containing loan lock details."
)

# Handle synthetic data trigger
if generate_mock_btn:
    os.makedirs("data", exist_ok=True)
    mock_path = os.path.join("data", "synthetic_loan_locks.csv")
    generate_data.create_synthetic_dataset(output_path=mock_path)
    st.sidebar.success("Synthetic dataset generated in `data/synthetic_loan_locks.csv`")
    uploaded_file = mock_path

if uploaded_file is not None:
    try:
        if isinstance(uploaded_file, str):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_csv(uploaded_file)

        # Execute processing pipeline
        audited_df, metrics, pdf_bytes = run_pipeline(df_raw, concession_threshold)

        # Display Top KPI Metrics
        st.subheader("Executive Audit Summary")
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Loans Audited", f"{metrics['total_loans']:,}")
        col2.metric("Total Financial Leakage", f"${metrics['total_leakage']:,.2f}")
        col3.metric("Avg Rate Variance (bps)", f"{metrics['avg_rate_variance']:.2f}")
        col4.metric(
            "Non-Compliant Flags",
            f"{metrics['flagged_loans_count']:,}",
            delta=f"{(metrics['flagged_loans_count'] / metrics['total_loans']) * 100:.1f}% of total",
            delta_color="inverse",
        )

        st.markdown("---")

        # Visual Analytics Section
        st.subheader("Financial Leakage & Compliance Analysis")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("**Rate Variance Distribution (bps)**")
            if "rate_variance_bps" in audited_df.columns:
                st.bar_chart(audited_df["rate_variance_bps"].value_counts().sort_index())
            else:
                st.line_chart(audited_df[["locked_rate", "target_rate"]])

        with chart_col2:
            st.markdown("**Leakage Amount by Compliance Status**")
            leakage_by_status = audited_df.groupby("compliance_flag")["dollar_leakage"].sum()
            st.bar_chart(leakage_by_status)

        st.markdown("---")

        # Detailed Data Table
        st.subheader("Audited Loan Records")

        show_flagged_only = st.checkbox("Show Non-Compliant Loans Only")
        display_df = audited_df[audited_df["compliance_flag"] == True] if show_flagged_only else audited_df

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        # Export Section
        st.markdown("---")
        st.subheader("Export Audit Reports")
        dl_col1, dl_col2 = st.columns(2)

        with dl_col1:
            st.download_button(
                label="📄 Download Executive Summary (PDF)",
                data=pdf_bytes,
                file_name="Executive_Audit_Summary.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        with dl_col2:
            csv_buffer = io.StringIO()
            audited_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📊 Download Audited Dataset (CSV)",
                data=csv_buffer.getvalue(),
                file_name="audited_loan_locks.csv",
                mime="text/csv",
                use_container_width=True,
            )

    except Exception as e:
        st.error(f"Error processing audit pipeline: {str(e)}")
else:
    st.info("💡 Upload a CSV file using the sidebar or click **Generate Synthetic Data** to run a test audit.")
