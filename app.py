import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import math

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(layout="wide")

st.markdown("""
<style>
.main-title { font-size:34px; font-weight:700; }
.section-title { font-size:22px; font-weight:600; margin-top:30px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏛 Enterprise Wireless Investment Decision Engine</div>', unsafe_allow_html=True)

# ============================================================
# VENUE BASE PROFILES
# ============================================================

VENUE_PROFILES = {
    "Small Venue": {"sqft":100000,"growth":5,"coverage":"Indoor Only","latency":20,"sla":"99.9%"},
    "Medium Venue": {"sqft":500000,"growth":8,"coverage":"Indoor + Outdoor","latency":15,"sla":"99.99%"},
    "Large Venue": {"sqft":2000000,"growth":15,"coverage":"Indoor + Outdoor","latency":8,"sla":"99.999%"}
}

# ============================================================
# SIDEBAR INPUTS
# ============================================================

st.sidebar.header("🏢 Venue Classification")
venue_type = st.sidebar.selectbox("Select Venue Size", list(VENUE_PROFILES.keys()))
profile = VENUE_PROFILES[venue_type]

st.sidebar.markdown(f"**Base Profile Applied:** {venue_type}")
st.sidebar.markdown("---")

st.sidebar.header("Strategic Parameters")
sqft = st.sidebar.number_input("Facility Size (sqft)", 1000, 10000000, profile["sqft"], 10000)
years = st.sidebar.slider("Investment Horizon (Years)", 3, 10, 5)

coverage = st.sidebar.selectbox(
    "Coverage Model",
    ["Indoor Only", "Outdoor Only", "Indoor + Outdoor"],
    index=["Indoor Only","Outdoor Only","Indoor + Outdoor"].index(profile["coverage"])
)

growth = st.sidebar.slider("Annual Device Growth (%)", 0, 30, profile["growth"])
latency = st.sidebar.slider("Latency Requirement (ms)", 1, 50, profile["latency"])

sla = st.sidebar.selectbox(
    "Availability Target",
    ["99.9%","99.99%","99.999%"],
    index=["99.9%","99.99%","99.999%"].index(profile["sla"])
)

st.sidebar.markdown("---")
st.sidebar.header("📌 Reference Pricing (Editable)")

wifi_ap_cost = st.sidebar.number_input("Wi-Fi Access Point Cost ($)", 500, 5000, 1200, 100)
wifi_maint = st.sidebar.slider("Wi-Fi Maintenance (%)", 5, 30, 18) / 100

p5g_cell_cost = st.sidebar.number_input("5G Small Cell Cost ($)", 2000, 10000, 5000, 500)
p5g_core_cost = st.sidebar.number_input("5G Core Cost ($)", 20000, 200000, 80000, 5000)
p5g_maint = st.sidebar.slider("5G Maintenance (%)", 5, 30, 15) / 100

# ============================================================
# MULTIPLIERS
# ============================================================

def sla_multiplier(sla):
    return {"99.9%":1.0,"99.99%":1.08,"99.999%":1.15}[sla]

def growth_multiplier(growth, years):
    return (1 + growth/100) ** years

def coverage_multiplier(coverage):
    if coverage == "Indoor Only":
        return 1.0
    elif coverage == "Outdoor Only":
        return 1.25
    else:
        return 1.15

# ============================================================
# COST CALCULATIONS
# ============================================================

wifi_ap_count = math.ceil((sqft/2500) * coverage_multiplier(coverage))
wifi_capex = wifi_ap_count * wifi_ap_cost
wifi_opex = wifi_capex * wifi_maint * years
wifi_total = (wifi_capex + wifi_opex) * sla_multiplier(sla) * growth_multiplier(growth, years)
if latency < 10:
    wifi_total *= 1.10

p5g_cell_count = math.ceil((sqft/10000) * coverage_multiplier(coverage))
p5g_capex = (p5g_cell_count * p5g_cell_cost) + p5g_core_cost
p5g_opex = p5g_capex * p5g_maint * years
p5g_total = (p5g_capex + p5g_opex) * sla_multiplier(sla) * growth_multiplier(growth, years)

hyb_capex = (wifi_capex * 0.6) + (p5g_capex * 0.6)
hyb_opex = (wifi_opex * 0.6) + (p5g_opex * 0.6)
hyb_total = (hyb_capex + hyb_opex) * sla_multiplier(sla) * growth_multiplier(growth, years)

# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

st.markdown('<div class="section-title">1️⃣ Executive Financial Overview</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Wi-Fi 5Y TCO", f"${wifi_total:,.0f}")
col2.metric("Private 5G 5Y TCO", f"${p5g_total:,.0f}")
col3.metric("Hybrid 5Y TCO", f"${hyb_total:,.0f}")

# ============================================================
# RELATIVE POSITIONING (Wi-Fi BASELINE)
# ============================================================

st.markdown('<div class="section-title">2️⃣ Relative Cost Positioning (Wi-Fi Baseline)</div>', unsafe_allow_html=True)

def percent_change(base, compare):
    return ((compare - base) / base) * 100

p5g_vs_wifi = percent_change(wifi_total, p5g_total)
hyb_vs_wifi = percent_change(wifi_total, hyb_total)

annual_wifi = wifi_total / years
annual_p5g = p5g_total / years
annual_hyb = hyb_total / years

wifi_per_sqft = wifi_total / sqft
p5g_per_sqft = p5g_total / sqft
hyb_per_sqft = hyb_total / sqft

data = pd.DataFrame({
    "Architecture": ["Wi-Fi (Baseline)", "Private 5G", "Hybrid"],
    "5Y TCO ($)": [wifi_total, p5g_total, hyb_total],
    "Annual Run Rate ($)": [annual_wifi, annual_p5g, annual_hyb],
    "Cost per Sqft ($)": [wifi_per_sqft, p5g_per_sqft, hyb_per_sqft],
    "% vs Wi-Fi": [
        "Baseline",
        f"{p5g_vs_wifi:+.1f}%",
        f"{hyb_vs_wifi:+.1f}%"
    ]
})

data["5Y TCO ($)"] = data["5Y TCO ($)"].map(lambda x: f"${x:,.0f}")
data["Annual Run Rate ($)"] = data["Annual Run Rate ($)"].map(lambda x: f"${x:,.0f}")
data["Cost per Sqft ($)"] = data["Cost per Sqft ($)"].map(lambda x: f"{x:.2f}")

def highlight(row):
    if row["% vs Wi-Fi"] == "Baseline":
        return ["background-color:#e9ecef"]*len(row)
    elif "-" in row["% vs Wi-Fi"]:
        return ["background-color:#d4edda"]*len(row)
    else:
        return ["background-color:#f8d7da"]*len(row)

st.dataframe(data.style.apply(highlight, axis=1), use_container_width=True, hide_index=True)

st.markdown("---")

if p5g_vs_wifi < 0:
    st.success(f"Private 5G reduces total investment by {abs(p5g_vs_wifi):.1f}% compared to Wi-Fi.")
else:
    st.warning(f"Private 5G increases total investment by {abs(p5g_vs_wifi):.1f}% compared to Wi-Fi.")

if hyb_vs_wifi < 0:
    st.success(f"Hybrid reduces total investment by {abs(hyb_vs_wifi):.1f}% compared to Wi-Fi.")
else:
    st.warning(f"Hybrid increases total investment by {abs(hyb_vs_wifi):.1f}% compared to Wi-Fi.")

# ============================================================
# CAPEX / OPEX
# ============================================================

st.markdown('<div class="section-title">3️⃣ Capital Investment (CAPEX)</div>', unsafe_allow_html=True)

fig_capex = go.Figure()
fig_capex.add_trace(go.Bar(x=["Wi-Fi","Private 5G","Hybrid"],
                           y=[wifi_capex,p5g_capex,hyb_capex]))
fig_capex.update_layout(template="plotly_white")
st.plotly_chart(fig_capex, use_container_width=True)

st.markdown('<div class="section-title">4️⃣ Operational Cost Exposure (OPEX)</div>', unsafe_allow_html=True)

fig_opex = go.Figure()
fig_opex.add_trace(go.Bar(x=["Wi-Fi","Private 5G","Hybrid"],
                          y=[wifi_opex,p5g_opex,hyb_opex]))
fig_opex.update_layout(template="plotly_white")
st.plotly_chart(fig_opex, use_container_width=True)

# ============================================================
# 5-YEAR TREND
# ============================================================

st.markdown('<div class="section-title">5️⃣ Investment Trend (Cumulative)</div>', unsafe_allow_html=True)

years_list = list(range(1, years+1))

wifi_trend = [wifi_capex + wifi_capex*wifi_maint*y for y in years_list]
p5g_trend = [p5g_capex + p5g_capex*p5g_maint*y for y in years_list]
hyb_trend = [hyb_capex + hyb_capex*wifi_maint*y for y in years_list]

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(x=years_list, y=wifi_trend, mode='lines+markers', name='Wi-Fi'))
fig_trend.add_trace(go.Scatter(x=years_list, y=p5g_trend, mode='lines+markers', name='Private 5G'))
fig_trend.add_trace(go.Scatter(x=years_list, y=hyb_trend, mode='lines+markers', name='Hybrid'))
fig_trend.update_layout(template="plotly_white")
st.plotly_chart(fig_trend, use_container_width=True)

# ============================================================
# NORMALIZED COST
# ============================================================

st.markdown('<div class="section-title">6️⃣ Normalized Cost Indicators</div>', unsafe_allow_html=True)

device_estimate = sqft * 0.01

c1, c2, c3 = st.columns(3)
c1.metric("Wi-Fi Cost per Device", f"${wifi_total/device_estimate:,.0f}")
c2.metric("5G Cost per Device", f"${p5g_total/device_estimate:,.0f}")
c3.metric("Hybrid Cost per Device", f"${hyb_total/device_estimate:,.0f}")