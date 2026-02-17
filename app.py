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
    "Small Venue": {
        "sqft": 100000,
        "growth": 5,
        "coverage": "Indoor Only",
        "latency": 20,
        "sla": "99.9%"
    },
    "Medium Venue": {
        "sqft": 500000,
        "growth": 8,
        "coverage": "Indoor + Outdoor",
        "latency": 15,
        "sla": "99.99%"
    },
    "Large Venue": {
        "sqft": 2000000,
        "growth": 15,
        "coverage": "Indoor + Outdoor",
        "latency": 8,
        "sla": "99.999%"
    }
}

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🏢 Venue Classification")

venue_type = st.sidebar.selectbox(
    "Select Venue Size",
    ["Small Venue", "Medium Venue", "Large Venue"]
)

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
st.sidebar.header("💰 Financial Assumptions")

wifi_ap_cost = st.sidebar.number_input("Wi-Fi Access Point Cost ($)", 500, 5000, 1200, 100)
wifi_maint = st.sidebar.slider("Wi-Fi Annual Maintenance (%)", 5, 30, 18) / 100

p5g_cell_cost = st.sidebar.number_input("5G Small Cell Cost ($)", 2000, 10000, 5000, 500)
p5g_core_cost = st.sidebar.number_input("5G Core Cost ($)", 20000, 200000, 80000, 5000)
p5g_maint = st.sidebar.slider("5G Annual Maintenance (%)", 5, 30, 15) / 100

# ============================================================
# REFERENCE PRICING PANEL (NEW)
# ============================================================

st.sidebar.markdown("---")
st.sidebar.header("📌 Reference Pricing Benchmarks")

st.sidebar.markdown("""
**Industry Typical Ranges:**

• Wi-Fi AP: $900 – $1,500  
• Wi-Fi Maintenance: 15% – 20%  

• 5G Small Cell: $4,000 – $6,000  
• 5G Core: $70,000 – $120,000  
• 5G Maintenance: 12% – 18%  

*Benchmarks based on enterprise deployments.*
""")

# ============================================================
# MULTIPLIERS
# ============================================================

def sla_multiplier(sla):
    return {"99.9%":1.0, "99.99%":1.08, "99.999%":1.15}[sla]

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

wifi_ap_count = math.ceil((sqft / 2500) * coverage_multiplier(coverage))
wifi_capex = wifi_ap_count * wifi_ap_cost
wifi_opex = wifi_capex * wifi_maint * years
wifi_total = (wifi_capex + wifi_opex) * sla_multiplier(sla) * growth_multiplier(growth, years)

if latency < 10:
    wifi_total *= 1.10

p5g_cell_count = math.ceil((sqft / 10000) * coverage_multiplier(coverage))
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
# RELATIVE COST TABLE (STYLED)
# ============================================================

st.markdown('<div class="section-title">2️⃣ Relative Cost Positioning</div>', unsafe_allow_html=True)

annual_wifi = wifi_total / years
annual_p5g = p5g_total / years
annual_hyb = hyb_total / years

wifi_per_sqft = wifi_total / sqft
p5g_per_sqft = p5g_total / sqft
hyb_per_sqft = hyb_total / sqft

cheapest_value = min(wifi_total, p5g_total, hyb_total)

def percent_diff(base, compare):
    return ((compare - base) / base) * 100

data = pd.DataFrame({
    "Architecture": ["Wi-Fi", "Private 5G", "Hybrid"],
    "5Y TCO ($)": [wifi_total, p5g_total, hyb_total],
    "Annual Run Rate ($)": [annual_wifi, annual_p5g, annual_hyb],
    "Cost per Sqft ($)": [wifi_per_sqft, p5g_per_sqft, hyb_per_sqft]
})

data["% vs Lowest Cost"] = data["5Y TCO ($)"].apply(
    lambda x: "Baseline" if x == cheapest_value
    else f"{percent_diff(cheapest_value, x):.1f}%"
)

data["5Y TCO ($)"] = data["5Y TCO ($)"].map(lambda x: f"${x:,.0f}")
data["Annual Run Rate ($)"] = data["Annual Run Rate ($)"].map(lambda x: f"${x:,.0f}")
data["Cost per Sqft ($)"] = data["Cost per Sqft ($)"].map(lambda x: f"{x:.2f}")

def highlight_row(row):
    if row["% vs Lowest Cost"] == "Baseline":
        return ["background-color: #d4edda"] * len(row)
    return [""] * len(row)

styled_table = data.style.apply(highlight_row, axis=1)

st.dataframe(styled_table, use_container_width=True, hide_index=True)

# ============================================================
# CAPEX & OPEX
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
# EXECUTIVE RECOMMENDATION
# ============================================================

st.markdown('<div class="section-title">5️⃣ Executive Recommendation</div>', unsafe_allow_html=True)

if cheapest_value == wifi_total:
    st.success("Recommendation: Wi-Fi provides the lowest total financial exposure under current assumptions.")
elif cheapest_value == p5g_total:
    st.success("Recommendation: Private 5G offers stronger scalability and long-term resilience.")
else:
    st.success("Recommendation: Hybrid architecture balances capital efficiency and operational flexibility.")