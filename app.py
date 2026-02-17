import streamlit as st
import plotly.graph_objects as go
import numpy as np
import math
import random

# ============================================================
# Vendor Pricing Simulation
# ============================================================

VENDOR_PRICING = {
    "Cisco": {
        "wifi_ap_cost": 1300,
        "p5g_small_cell_cost": 5200,
        "core_cost": 85000,
        "maintenance_wifi": 0.18,
        "maintenance_p5g": 0.16
    },
    "Nokia": {
        "wifi_ap_cost": 1200,
        "p5g_small_cell_cost": 5000,
        "core_cost": 80000,
        "maintenance_wifi": 0.17,
        "maintenance_p5g": 0.15
    },
    "Ericsson": {
        "wifi_ap_cost": 1250,
        "p5g_small_cell_cost": 5500,
        "core_cost": 90000,
        "maintenance_wifi": 0.19,
        "maintenance_p5g": 0.17
    }
}

# ============================================================
# Business Logic
# ============================================================

class WirelessTCOModel:
    def __init__(self, sqft, years, vendor):
        self.sqft = sqft
        self.years = years
        self.vendor = VENDOR_PRICING[vendor]

    def wifi_ap_count(self):
        return math.ceil(self.sqft / 2500)

    def p5g_cell_count(self):
        return math.ceil(self.sqft / 10000)

    def calculate_wifi(self):
        ap_count = self.wifi_ap_count()
        capex = ap_count * self.vendor["wifi_ap_cost"]
        opex = capex * self.vendor["maintenance_wifi"] * self.years
        return capex, opex

    def calculate_p5g(self):
        cell_count = self.p5g_cell_count()
        capex = cell_count * self.vendor["p5g_small_cell_cost"] + self.vendor["core_cost"]
        opex = capex * self.vendor["maintenance_p5g"] * self.years
        return capex, opex

    def calculate_hybrid(self):
        wifi_capex, wifi_opex = self.calculate_wifi()
        p5g_capex, p5g_opex = self.calculate_p5g()

        capex = (wifi_capex * 0.6) + (p5g_capex * 0.6)
        opex = (wifi_opex * 0.6) + (p5g_opex * 0.6)
        return capex, opex


# ============================================================
# Streamlit UI
# ============================================================

st.set_page_config(page_title="Enterprise Wireless TCO Optimizer", layout="wide")
st.title("🌐 Enterprise Wireless Economic Engine")

st.sidebar.header("🏢 Facility Parameters")

sqft = st.sidebar.number_input("Facility Size (sqft)", 1000, 10000000, 500000, 10000)
years = st.sidebar.slider("Analysis Horizon (Years)", 1, 10, 5)
vendor = st.sidebar.selectbox("Select Vendor", ["Cisco", "Nokia", "Ericsson"])
architecture = st.sidebar.selectbox("Architecture", ["Wi-Fi 6E", "Private 5G", "Hybrid"])

model = WirelessTCOModel(sqft, years, vendor)

# ============================================================
# Calculate Costs
# ============================================================

wifi_capex, wifi_opex = model.calculate_wifi()
p5g_capex, p5g_opex = model.calculate_p5g()
hyb_capex, hyb_opex = model.calculate_hybrid()

wifi_total = wifi_capex + wifi_opex
p5g_total = p5g_capex + p5g_opex
hyb_total = hyb_capex + hyb_opex

# ============================================================
# KPI Section
# ============================================================

col1, col2, col3 = st.columns(3)
col1.metric("Wi-Fi 6E TCO", f"${wifi_total:,.0f}")
col2.metric("Private 5G TCO", f"${p5g_total:,.0f}")
col3.metric("Hybrid TCO", f"${hyb_total:,.0f}")

# ============================================================
# CAPEX vs OPEX Chart
# ============================================================

st.subheader("💰 CAPEX vs OPEX Breakdown")

fig1 = go.Figure()
fig1.add_trace(go.Bar(name="Wi-Fi CAPEX", x=["Wi-Fi"], y=[wifi_capex]))
fig1.add_trace(go.Bar(name="Wi-Fi OPEX", x=["Wi-Fi"], y=[wifi_opex]))
fig1.add_trace(go.Bar(name="5G CAPEX", x=["Private 5G"], y=[p5g_capex]))
fig1.add_trace(go.Bar(name="5G OPEX", x=["Private 5G"], y=[p5g_opex]))
fig1.add_trace(go.Bar(name="Hybrid CAPEX", x=["Hybrid"], y=[hyb_capex]))
fig1.add_trace(go.Bar(name="Hybrid OPEX", x=["Hybrid"], y=[hyb_opex]))

fig1.update_layout(barmode="stack", template="plotly_white")
st.plotly_chart(fig1, use_container_width=True)

# ============================================================
# Radar Chart (Qualitative Comparison)
# ============================================================

st.subheader("📊 Qualitative Comparison")

categories = ["Scalability", "Security", "Latency", "Mobility", "Cost Efficiency"]

wifi_scores = [6, 7, 6, 5, 8]
p5g_scores = [9, 9, 9, 9, 6]
hyb_scores = [8, 8, 8, 8, 7]

fig2 = go.Figure()

fig2.add_trace(go.Scatterpolar(r=wifi_scores, theta=categories, fill='toself', name='Wi-Fi'))
fig2.add_trace(go.Scatterpolar(r=p5g_scores, theta=categories, fill='toself', name='Private 5G'))
fig2.add_trace(go.Scatterpolar(r=hyb_scores, theta=categories, fill='toself', name='Hybrid'))

fig2.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,10])), showlegend=True)
st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# Monte Carlo Risk Simulation
# ============================================================

st.subheader("🎲 Monte Carlo Risk Simulation (Cost Variability)")

simulations = 1000
wifi_sim = []
p5g_sim = []

for _ in range(simulations):
    wifi_sim.append(wifi_total * random.uniform(0.9, 1.15))
    p5g_sim.append(p5g_total * random.uniform(0.9, 1.15))

fig3 = go.Figure()
fig3.add_trace(go.Histogram(x=wifi_sim, name="Wi-Fi", opacity=0.6))
fig3.add_trace(go.Histogram(x=p5g_sim, name="Private 5G", opacity=0.6))

fig3.update_layout(barmode="overlay", template="plotly_white")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.caption("Simulated enterprise financial model for strategic comparison purposes.")