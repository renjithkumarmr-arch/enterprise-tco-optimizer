import sys
import os

# 🔹 Ensure current directory is in Python path (fix for Streamlit Cloud import issue)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import plotly.graph_objects as go
from logic import WirelessTCOModel


# ------------------------------
# Page Configuration
# ------------------------------
st.set_page_config(
    page_title="Enterprise Wireless TCO Model",
    layout="wide"
)

st.title("📊 Wireless Strategy Optimizer: Private 5G vs Wi-Fi 6E")
st.markdown("Compare Total Cost of Ownership (TCO) across architectures.")

# ------------------------------
# Sidebar Inputs
# ------------------------------
st.sidebar.header("Facility Parameters")

sqft = st.sidebar.number_input(
    "Facility Square Footage",
    min_value=1000,
    max_value=10000000,
    value=500000,
    step=10000
)

years = st.sidebar.slider(
    "Analysis Horizon (Years)",
    min_value=1,
    max_value=10,
    value=5
)

# ------------------------------
# Model Execution (Safe Block)
# ------------------------------
try:
    model = WirelessTCOModel(
        facility_sqft=sqft,
        years=years
    )

    wifi_tco = model.calculate_wifi_tco()
    p5g_tco = model.calculate_p5g_tco()

    # ------------------------------
    # KPI Display
    # ------------------------------
    col1, col2 = st.columns(2)

    col1.metric(
        label="Wi-Fi 6E Total Cost",
        value=f"${wifi_tco:,.0f}"
    )

    col2.metric(
        label="Private 5G Total Cost",
        value=f"${p5g_tco:,.0f}"
    )

    # ------------------------------
    # Visualization
    # ------------------------------
    st.subheader(f"Total Cost Comparison over {years} Years")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Wi-Fi 6E",
        x=["TCO"],
        y=[wifi_tco]
    ))

    fig.add_trace(go.Bar(
        name="Private 5G",
        x=["TCO"],
        y=[p5g_tco]
    ))

    fig.update_layout(
        barmode="group",
        xaxis_title="Architecture",
        yaxis_title="Total Cost (USD)",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("An error occurred while running the model.")
    st.exception(e)