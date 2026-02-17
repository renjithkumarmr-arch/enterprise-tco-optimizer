import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import math
import numpy as np

st.set_page_config(layout="wide")

st.markdown("""
<style>
.main-title { font-size:34px; font-weight:700; }
.section-title { font-size:22px; font-weight:600; margin-top:30px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏛 Enterprise Wireless Strategic Investment Engine</div>', unsafe_allow_html=True)

# ============================================================
# SIDEBAR – CORE INPUTS
# ============================================================

st.sidebar.header("🏢 Strategic Inputs")

sqft = st.sidebar.number_input("Facility Size (sqft)", 1000, 10000000, 500000, 10000)
years = st.sidebar.slider("Investment Horizon (Years)", 3, 10, 5)
discount_rate = st.sidebar.slider("Discount Rate (%)", 5, 20, 10) / 100

coverage = st.sidebar.selectbox("Coverage Model",
                                ["Indoor Only", "Outdoor Only", "Indoor + Outdoor"])

growth = st.sidebar.slider("Annual Growth (%)", 0, 30, 10)
latency = st.sidebar.slider("Latency Requirement (ms)", 1, 50, 15)
sla = st.sidebar.selectbox("Availability Target", ["99.9%","99.99%","99.999%"])

# ============================================================
# COST STACK INPUTS
# ============================================================

st.sidebar.markdown("---")
st.sidebar.header("📶 Wi-Fi Stack")

wifi_ap_cost = st.sidebar.number_input("AP Cost ($)", 500, 5000, 1200)
wifi_switch_cost = st.sidebar.number_input("Switch Cost ($)", 2000, 20000, 8000)
wifi_controller_cost = st.sidebar.number_input("Controller Cost ($)", 10000, 200000, 50000)
wifi_install_percent = st.sidebar.slider("Wi-Fi Installation (%)", 5, 30, 15) / 100
wifi_maint = st.sidebar.slider("Wi-Fi Maintenance (%)", 5, 30, 18) / 100

st.sidebar.markdown("---")
st.sidebar.header("📡 Private 5G Stack")

p5g_cell_cost = st.sidebar.number_input("Small Cell Cost ($)", 2000, 10000, 5000)
p5g_core_cost = st.sidebar.number_input("5G Core Cost ($)", 20000, 200000, 80000)
p5g_edge_cost = st.sidebar.number_input("Edge Server Cost ($)", 10000, 150000, 60000)
p5g_backhaul_cost = st.sidebar.number_input("Backhaul Cost ($)", 10000, 200000, 40000)
p5g_install_percent = st.sidebar.slider("5G Installation (%)", 5, 30, 12) / 100
p5g_maint = st.sidebar.slider("5G Maintenance (%)", 5, 30, 15) / 100

# ============================================================
# MULTIPLIERS
# ============================================================

def sla_multiplier(sla):
    return {"99.9%":1.0,"99.99%":1.08,"99.999%":1.15}[sla]

def coverage_multiplier(coverage):
    return {"Indoor Only":1.0,"Outdoor Only":1.25,"Indoor + Outdoor":1.15}[coverage]

def growth_multiplier(growth, years):
    return (1 + growth/100) ** years

# ============================================================
# Wi-Fi CALCULATION
# ============================================================

wifi_ap_count = math.ceil((sqft / 2500) * coverage_multiplier(coverage))
wifi_switch_count = math.ceil(wifi_ap_count / 24)

wifi_capex_raw = (
    wifi_ap_count * wifi_ap_cost
    + wifi_switch_count * wifi_switch_cost
    + wifi_controller_cost
)

wifi_capex = wifi_capex_raw * (1 + wifi_install_percent)
wifi_opex = wifi_capex * wifi_maint * years
wifi_total = (wifi_capex + wifi_opex) * sla_multiplier(sla) * growth_multiplier(growth, years)

if latency < 10:
    wifi_total *= 1.10

# ============================================================
# 5G CALCULATION
# ============================================================

p5g_cell_count = math.ceil((sqft / 10000) * coverage_multiplier(coverage))

p5g_capex_raw = (
    p5g_cell_count * p5g_cell_cost
    + p5g_core_cost
    + p5g_edge_cost
    + p5g_backhaul_cost
)

p5g_capex = p5g_capex_raw * (1 + p5g_install_percent)
p5g_opex = p5g_capex * p5g_maint * years
p5g_total = (p5g_capex + p5g_opex) * sla_multiplier(sla) * growth_multiplier(growth, years)

# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

st.markdown('<div class="section-title">1️⃣ Executive Summary</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
c1.metric("Wi-Fi 5Y TCO", f"${wifi_total:,.0f}")
c2.metric("Private 5G 5Y TCO", f"${p5g_total:,.0f}")

# ============================================================
# BREAK-EVEN DETECTION
# ============================================================

st.markdown('<div class="section-title">2️⃣ Break-Even Analysis</div>', unsafe_allow_html=True)

break_even_year = None

for y in range(1, years+1):
    wifi_y = wifi_capex + (wifi_capex * wifi_maint * y)
    p5g_y = p5g_capex + (p5g_capex * p5g_maint * y)
    if p5g_y <= wifi_y:
        break_even_year = y
        break

if break_even_year:
    st.success(f"Private 5G reaches cost parity in Year {break_even_year}.")
else:
    st.info("No break-even within selected investment horizon.")

# ============================================================
# ROI & NPV
# ============================================================

st.markdown('<div class="section-title">3️⃣ NPV & ROI Modeling</div>', unsafe_allow_html=True)

cash_flows_wifi = [-wifi_capex] + [-wifi_capex * wifi_maint] * years
cash_flows_p5g = [-p5g_capex] + [-p5g_capex * p5g_maint] * years

npv_wifi = np.npv(discount_rate, cash_flows_wifi)
npv_p5g = np.npv(discount_rate, cash_flows_p5g)

col1, col2 = st.columns(2)
col1.metric("Wi-Fi NPV", f"${npv_wifi:,.0f}")
col2.metric("Private 5G NPV", f"${npv_p5g:,.0f}")

roi = (wifi_total - p5g_total) / p5g_total * 100
st.write(f"ROI comparison (Wi-Fi vs 5G): {roi:.1f}%")

# ============================================================
# SENSITIVITY HEATMAP
# ============================================================

st.markdown('<div class="section-title">4️⃣ Sensitivity Heatmap (Growth vs Maintenance)</div>', unsafe_allow_html=True)

growth_range = np.linspace(0, 20, 5)
maint_range = np.linspace(0.1, 0.25, 5)

heatmap = []

for g in growth_range:
    row = []
    for m in maint_range:
        total = (wifi_capex + wifi_capex * m * years) * growth_multiplier(g, years)
        row.append(total)
    heatmap.append(row)

heatmap_df = pd.DataFrame(heatmap,
                          index=[f"{g:.0f}%" for g in growth_range],
                          columns=[f"{m:.2f}" for m in maint_range])

fig_heat = px.imshow(heatmap_df,
                     labels=dict(x="Maintenance Rate", y="Growth Rate", color="Wi-Fi TCO"),
                     aspect="auto")

st.plotly_chart(fig_heat, use_container_width=True)

# ============================================================
# SCENARIO COMPARISON MODE
# ============================================================

st.markdown('<div class="section-title">5️⃣ Scenario Comparison Mode</div>', unsafe_allow_html=True)

scenario_discount = st.slider("Alternate Discount Rate (%)", 5, 20, 12) / 100

npv_wifi_alt = np.npv(scenario_discount, cash_flows_wifi)
npv_p5g_alt = np.npv(scenario_discount, cash_flows_p5g)

st.write(f"At {scenario_discount*100:.0f}% discount rate:")
st.write(f"- Wi-Fi NPV: ${npv_wifi_alt:,.0f}")
st.write(f"- Private 5G NPV: ${npv_p5g_alt:,.0f}")