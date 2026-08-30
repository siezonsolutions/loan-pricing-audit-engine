import streamlit as st
import pandas as pd
import plotly.express as px
from engine.pricing import run_audit
from generate_data import create_synthetic_dataset # Generates sample data on the fly

# Page Layout Config
st.set_page_config(
    page_title="Mortgage Pricing & Concession Audit Engine",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Mortgage Pricing & Concession Audit Engine")
st.caption("Identify secondary market revenue leakage, unbacked loan officer concessions, and CFPB fair-lending risks.")

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ Audit Controls")

# Threshold Adjustment Slider
cfpb_threshold = st.sidebar.slider(
    "CFPB Risk Threshold (bps)",
    min_value=5.0,
    max_value=50.0,
    value=25.0,
    step=2.5,
    help="Flags any loan concession exceeding this basis point threshold for fair-lending review."
)

st.sidebar.markdown("---")
st.sidebar.header("📁 Data Input")

uploaded_file = st.sidebar.file_uploader("Upload Loan Locks (CSV)", type=["csv"])
use_sample_data = st.sidebar.button("⚡ Load Demo Sample Dataset (500 Loans)")

raw_df = None

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
elif use_sample_data:
    raw_df = create_synthetic_dataset(num_records=500)
    st.sidebar.success("Loaded 500 sample loan locks.")

# --- Main Dashboard Rendering ---
if raw_df is not None:
    # Run Audit Calculation Engine
    results = run_audit(raw_df, cfpb_threshold_bps=cfpb_threshold)
    
    df = results["audited_df"]
    lo_df = results["lo_breakdown"]
    region_df = results["region_breakdown"]
    product_df = results["product_breakdown"]

    # Region Sidebar Multi-select Filter
    st.sidebar.markdown("---")
    available_regions = df['region'].unique().tolist()
    selected_regions = st.sidebar.multiselect(
        "Filter Dashboard by Region",
        options=available_regions,
        default=available_regions
    )
    
    # Filter dataset based on selected regions
    filtered_df = df[df['region'].isin(selected_regions)]
    filtered_results = run_audit(filtered_df, cfpb_threshold_bps=cfpb_threshold)

    # --- Top Metric Cards ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Loans Audited", f"{len(filtered_df):,}")
    col2.metric("Total Lock Volume", f"${filtered_df['loan_amount'].sum():,.2f}")
    col3.metric("Revenue Leakage", f"${filtered_results['total_leakage']:,.2f}", delta_color="inverse")
    col4.metric(f"CFPB Risk Flags (>{cfpb_threshold:.0f}bps)", f"{filtered_results['total_cfpb_flags']}", delta_color="inverse")

    st.markdown("---")

    # --- Multi-Tab View ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📍 Regional Analysis", 
        "👤 Loan Officer Breakdown", 
        "🏠 Product Type Analysis", 
        "📄 Raw Audit Records"
    ])

    # TAB 1: REGIONAL BREAKDOWN
    with tab1:
        st.subheader("Margin Leakage & Compliance Risk by Region")
        fig_region = px.bar(
            filtered_results["region_breakdown"], 
            x="region", 
            y="total_leakage", 
            color="cfpb_flag_count",
            title="Total Dollar Leakage vs High Concession Flags by Region",
            labels={
                "total_leakage": "Leakage ($)", 
                "region": "Region", 
                "cfpb_flag_count": f"Flags (>{cfpb_threshold:.0f}bps)"
            },
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_region, use_container_width=True)
        st.dataframe(filtered_results["region_breakdown"], use_container_width=True)

    # TAB 2: LOAN OFFICER BREAKDOWN
    with tab2:
        st.subheader("Top Concession Officers")
        fig_lo = px.bar(
            filtered_results["lo_breakdown"].head(10), 
            x="total_leakage", 
            y="loan_officer", 
            orientation="h",
            color="avg_concession_bps",
            title="Top 10 Loan Officers by Total Revenue Leakage ($)",
            labels={
                "total_leakage": "Total Leakage ($)", 
                "loan_officer": "Loan Officer", 
                "avg_concession_bps": "Avg Concession (bps)"
            },
            color_continuous_scale="Oranges"
        )
        fig_lo.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_lo, use_container_width=True)
        st.dataframe(filtered_results["lo_breakdown"], use_container_width=True)

    # TAB 3: PRODUCT TYPE BREAKDOWN
    with tab3:
        st.subheader("Leakage Distribution Across Product Types")
        col_pie, col_table = st.columns([1, 1])
        with col_pie:
            fig_prod = px.pie(
                filtered_results["product_breakdown"], 
                names="product_type", 
                values="total_leakage", 
                title="Revenue Leakage Share by Product",
                hole=0.4
            )
            st.plotly_chart(fig_prod, use_container_width=True)
        with col_table:
            st.dataframe(filtered_results["product_breakdown"], use_container_width=True)

    # TAB 4: RAW AUDIT DATA TABLE
    with tab4:
        st.subheader("Detailed Audit Ledger")
        st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("👈 Upload a loan lock CSV in the sidebar or click 'Load Demo Sample Dataset' to launch the audit engine.")
