import streamlit as st
import plotly.graph_objects as go
import math

st.set_page_config(layout="wide")

st.markdown("""
<style>
.main-title { font-size:34px; font-weight:700; }
.section-title { font-size:22px; font-weight:600; margin-top:30px; }
.small-note { font-size:14px; color:gray; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏛 Enterprise Wireless Investment Decision Engine</div>', unsafe_allow_html=True)

# ============================================================
# VENUE SIZE BASE MODELING
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
# SIDEBAR – DRILL DOWN MODEL
# ============================================================

st.sidebar.header("🏢 Venue Classification")

venue_type = st.sidebar.selectbox(
    "Select Venue Size",
    ["Small Venue", "Medium Venue", "Large Venue"]
)

profile = VENUE_PROFILES[venue_type]

st.sidebar.markdown(f"**Base Model Applied:** {venue_type}")

st.sidebar.markdown("---")
st.sidebar.header("Strategic Parameters")

sqft = st.sidebar.number_input("Facility Size (sqft)", 1000, 10000000, profile["sqft"], 10000)
years = st.sidebar.slider("Investment Horizon (Years)", 3, 10, 5)
coverage = st.sidebar.selectbox("Coverage Model",
                                 ["Indoor Only", "Outdoor Only", "Indoor + Outdoor"],
                                 index=["Indoor Only","Outdoor Only","Indoor + Outdoor"].index(profile["coverage"]))
growth = st.sidebar.slider("Annual Device Growth (%)", 0, 30, profile["growth"])
latency = st.sidebar.slider("Latency Requirement (ms)", 1, 50, profile["latency"])
sla = st.sidebar.selectbox("Availability Target",
                           ["99.9%","99.99%","99.999%"],
                           index=["99.9%","99.99%","99.999%"].index(profile["sla"]))

st.sidebar.markdown("---")
st.sidebar.header("💰 Financial Assumptions")

wifi_ap_cost = st.sidebar.number_input("Wi-Fi Access Point Cost ($)", 500, 5000, 1200, 100)
wifi_maint = st.sidebar.slider("Wi-Fi Annual Maintenance (%)", 5, 30, 18) / 100

p5g_cell_cost = st.sidebar.number_input("5G Small Cell Cost ($)", 2000, 10000, 5000, 500)
p5g_core_cost = st.sidebar.number_input("5G Core Cost ($)", 20000, 200000, 80000, 5000)
p5g_maint = st.sidebar.slider("5G Annual Maintenance (%)", 5, 30, 15) / 100

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

# Relative Delta
cheapest = min(wifi_total, p5g_total, hyb_total)

st.markdown('<div class="section-title">2️⃣ Relative Cost Positioning</div>', unsafe_allow_html=True)

if cheapest == wifi_total:
    delta = (p5g_total - wifi_total)/wifi_total*100
    st.success(f"Wi-Fi delivers approximately {delta:.1f}% lower total investment vs Private 5G.")
elif cheapest == p5g_total:
    delta = (wifi_total - p5g_total)/p5g_total*100
    st.success(f"Private 5G delivers approximately {delta:.1f}% lower total investment vs Wi-Fi.")
else:
    st.success("Hybrid provides balanced cost structure across CAPEX and OPEX.")

# ============================================================
# CAPEX & OPEX SEPARATE
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
# STRATEGIC TRIGGERS
# ============================================================

st.markdown('<div class="section-title">5️⃣ Strategic Impact Indicators</div>', unsafe_allow_html=True)

if latency < 10:
    st.info("Low latency requirement strengthens Private 5G strategic case.")

if growth > 15:
    st.info("High growth environment favors scalable architecture.")

if sla == "99.999%":
    st.warning("Ultra-high availability requirement increases resilience cost.")