import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import math

st.set_page_config(layout="wide")

st.markdown("""
<style>
.main-title { font-size:34px; font-weight:700; }
.section-title { font-size:22px; font-weight:600; margin-top:30px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏛 Enterprise Wireless Full-Stack Investment Model</div>', unsafe_allow_html=True)

# ============================================================
# SIDEBAR – STRATEGIC INPUTS
# ============================================================

st.sidebar.header("🏢 Strategic Parameters")

sqft = st.sidebar.number_input("Facility Size (sqft)", 1000, 10000000, 500000, 10000)
years = st.sidebar.slider("Investment Horizon (Years)", 3, 10, 5)

coverage = st.sidebar.selectbox(
    "Coverage Model",
    ["Indoor Only", "Outdoor Only", "Indoor + Outdoor"]
)

growth = st.sidebar.slider("Annual Device Growth (%)", 0, 30, 10)
latency = st.sidebar.slider("Latency Requirement (ms)", 1, 50, 15)
sla = st.sidebar.selectbox("Availability Target", ["99.9%","99.99%","99.999%"])

# ============================================================
# SIDEBAR – Wi-Fi STACK
# ============================================================

st.sidebar.markdown("---")
st.sidebar.header("📶 Wi-Fi Infrastructure Stack")

wifi_ap_cost = st.sidebar.number_input("Access Point Cost ($)", 500, 5000, 1200, 100)
wifi_switch_cost = st.sidebar.number_input("Access Switch Cost ($)", 2000, 20000, 8000, 500)
wifi_controller_cost = st.sidebar.number_input("Controller / Core Cost ($)", 10000, 200000, 50000, 5000)
wifi_install_percent = st.sidebar.slider("Installation & Cabling (%)", 5, 30, 15) / 100
wifi_maint = st.sidebar.slider("Annual Maintenance (%)", 5, 30, 18) / 100

# ============================================================
# SIDEBAR – PRIVATE 5G STACK
# ============================================================

st.sidebar.markdown("---")
st.sidebar.header("📡 Private 5G Infrastructure Stack")

p5g_cell_cost = st.sidebar.number_input("Small Cell Cost ($)", 2000, 10000, 5000, 500)
p5g_core_cost = st.sidebar.number_input("5G Core Cost ($)", 20000, 200000, 80000, 5000)
p5g_edge_cost = st.sidebar.number_input("Edge Server Cost ($)", 10000, 150000, 60000, 5000)
p5g_backhaul_cost = st.sidebar.number_input("Backhaul / Transport Cost ($)", 10000, 200000, 40000, 5000)
p5g_install_percent = st.sidebar.slider("Installation (%)", 5, 30, 12) / 100
p5g_maint = st.sidebar.slider("Annual Maintenance (%)", 5, 30, 15) / 100

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

wifi_capex = (
    (wifi_ap_count * wifi_ap_cost)
    + (wifi_switch_count * wifi_switch_cost)
    + wifi_controller_cost
)

wifi_capex *= (1 + wifi_install_percent)

wifi_opex = wifi_capex * wifi_maint * years
wifi_total = (wifi_capex + wifi_opex) * sla_multiplier(sla) * growth_multiplier(growth, years)

if latency < 10:
    wifi_total *= 1.10

# ============================================================
# 5G CALCULATION
# ============================================================

p5g_cell_count = math.ceil((sqft / 10000) * coverage_multiplier(coverage))

p5g_capex = (
    (p5g_cell_count * p5g_cell_cost)
    + p5g_core_cost
    + p5g_edge_cost
    + p5g_backhaul_cost
)

p5g_capex *= (1 + p5g_install_percent)

p5g_opex = p5g_capex * p5g_maint * years
p5g_total = (p5g_capex + p5g_opex) * sla_multiplier(sla) * growth_multiplier(growth, years)

# ============================================================
# HYBRID (60% Infra Blending)
# ============================================================

hyb_capex = (wifi_capex * 0.6) + (p5g_capex * 0.6)
hyb_opex = (wifi_opex * 0.6) + (p5g_opex * 0.6)
hyb_total = (hyb_capex + hyb_opex) * sla_multiplier(sla) * growth_multiplier(growth, years)

# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

st.markdown('<div class="section-title">1️⃣ Executive Financial Overview</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Wi-Fi 5Y TCO", f"${wifi_total:,.0f}")
c2.metric("Private 5G 5Y TCO", f"${p5g_total:,.0f}")
c3.metric("Hybrid 5Y TCO", f"${hyb_total:,.0f}")

# ============================================================
# RELATIVE POSITIONING (Wi-Fi BASELINE)
# ============================================================

st.markdown('<div class="section-title">2️⃣ Relative Cost Positioning (Wi-Fi Baseline)</div>', unsafe_allow_html=True)

def percent_change(base, compare):
    return ((compare - base) / base) * 100

p5g_vs_wifi = percent_change(wifi_total, p5g_total)
hyb_vs_wifi = percent_change(wifi_total, hyb_total)

data = pd.DataFrame({
    "Architecture": ["Wi-Fi (Baseline)", "Private 5G", "Hybrid"],
    "5Y TCO ($)": [wifi_total, p5g_total, hyb_total],
    "% vs Wi-Fi": ["Baseline", f"{p5g_vs_wifi:+.1f}%", f"{hyb_vs_wifi:+.1f}%"]
})

data["5Y TCO ($)"] = data["5Y TCO ($)"].map(lambda x: f"${x:,.0f}")

st.dataframe(data, use_container_width=True, hide_index=True)

st.markdown("---")

if p5g_vs_wifi < 0:
    st.success(f"Private 5G reduces investment by {abs(p5g_vs_wifi):.1f}% vs Wi-Fi.")
else:
    st.warning(f"Private 5G increases investment by {abs(p5g_vs_wifi):.1f}% vs Wi-Fi.")

if hyb_vs_wifi < 0:
    st.success(f"Hybrid reduces investment by {abs(hyb_vs_wifi):.1f}% vs Wi-Fi.")
else:
    st.warning(f"Hybrid increases investment by {abs(hyb_vs_wifi):.1f}% vs Wi-Fi.")