import streamlit as st
import plotly.graph_objects as go
import math


# ==============================
# Business Logic Class
# ==============================
class WirelessTCOModel:
    def __init__(self, facility_sqft, years, device_density=0.0001):
        self.facility_sqft = facility_sqft
        self.years = years
        self.device_density = device_density

        # Assumptions
        self.wifi_ap_cost = 1200
        self.p5g_small_cell_cost = 5000
        self.annual_wifi_maintenance = 0.18
        self.annual_p5g_maintenance = 0.15

    def calculate_wifi_ap_count(self):
        return math.ceil(self.facility_sqft / 2500)

    def calculate_p5g_cell_count(self):
        return math.ceil(self.facility_sqft / 10000)

    def calculate_wifi_tco(self):
        ap_count = self.calculate_wifi_ap_count()
        capex = ap_count * self.wifi_ap_cost
        opex = capex * self.annual_wifi_maintenance * self.years
        return capex + opex

    def calculate_p5g_tco(self):
        cell_count = self.calculate_p5g_cell_count()
        capex = cell_count * self.p5g_small_cell_cost + 80000
        opex = capex * self.annual_p5g_maintenance * self.years
        return capex + opex


# ==============================
# Streamlit UI
# ==============================
st.set_page_config(
    page_title="Enterprise Wireless TCO Model",
    layout="wide"
)

st.title("📊 Wireless Strategy Optimizer: Private 5G vs Wi-Fi 6E")
st.markdown("Compare Total Cost of Ownership (TCO) across architectures.")

# Sidebar
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

# Model Execution
model = WirelessTCOModel(sqft, years)

wifi_tco = model.calculate_wifi_tco()
p5g_tco = model.calculate_p5g_tco()

# Metrics
col1, col2 = st.columns(2)

col1.metric("Wi-Fi 6E Total Cost", f"${wifi_tco:,.0f}")
col2.metric("Private 5G Total Cost", f"${p5g_tco:,.0f}")

# Chart
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