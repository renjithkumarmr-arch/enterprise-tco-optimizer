import streamlit as st
import plotly.graph_objects as go
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
# Wi-Fi STACK
# ============================================================

st.sidebar.markdown("---")
st.sidebar.header("📶 Wi-Fi Stack")

wifi_ap_cost = st.sidebar.number_input("Access Point Cost ($)", 500, 5000, 1200)
wifi_switch_cost = st.sidebar.number_input("Access Switch Cost ($)", 2000, 20000, 8000)
wifi_controller_cost = st.sidebar.number_input("Controller/Core Cost ($)", 10000, 200000, 50000)
wifi_install_percent = st.sidebar.slider("Installation (%)", 5, 30, 15) / 100
wifi_maint = st.sidebar.slider("Maintenance (%)", 5, 30, 18) / 100

# ============================================================
# PRIVATE 5G STACK
# ============================================================

st.sidebar.markdown("---")
st.sidebar.header("📡 Private 5G Stack")

p5g_cell_cost = st.sidebar.number_input("Small Cell Cost ($)", 2000, 10000, 5000)
p5g_core_cost = st.sidebar.number_input("5G Core Cost ($)", 20000, 200000, 80000)
p5g_edge_cost = st.sidebar.number_input("Edge Server Cost ($)", 10000, 150000, 60000)
p5g_backhaul_cost = st.sidebar.number_input("Backhaul Cost ($)", 10000, 200000, 40000)
p5g_install_percent = st.sidebar.slider("Installation (%)", 5, 30, 12) / 100
p5g_maint = st.sidebar.slider("Maintenance (%)", 5, 30, 15) / 100

# ============================================================
# MULTIPLIERS
# ============================================================

def sla_multiplier(s):
    return {"99.9%":1.0,"99.99%":1.08,"99.999%":1.15}[s]

def coverage_multiplier(c):
    return {"Indoor Only":1.0,"Outdoor Only":1.25,"Indoor + Outdoor":1.15}[c]

def growth_multiplier(g, y):
    return (1 + g/100) ** y

# ============================================================
# Wi-Fi CALCULATION
# ============================================================

wifi_ap_count = math.ceil((sqft / 2500) * coverage_multiplier(coverage))
wifi_switch_count = math.ceil(wifi_ap_count / 24)

wifi_access_cost = wifi_ap_count * wifi_ap_cost
wifi_switch_total = wifi_switch_count * wifi_switch_cost
wifi_core_total = wifi_controller_cost

wifi_capex_raw = wifi_access_cost + wifi_switch_total + wifi_core_total
wifi_install_cost = wifi_capex_raw * wifi_install_percent
wifi_capex = wifi_capex_raw + wifi_install_cost

wifi_opex = wifi_capex * wifi_maint * years
wifi_total = (wifi_capex + wifi_opex) * sla_multiplier(sla) * growth_multiplier(growth, years)

if latency < 10:
    wifi_total *= 1.10

# ============================================================
# 5G CALCULATION
# ============================================================

p5g_cell_count = math.ceil((sqft / 10000) * coverage_multiplier(coverage))

p5g_radio_cost = p5g_cell_count * p5g_cell_cost
p5g_core_total = p5g_core_cost
p5g_edge_total = p5g_edge_cost
p5g_backhaul_total = p5g_backhaul_cost

p5g_capex_raw = p5g_radio_cost + p5g_core_total + p5g_edge_total + p5g_backhaul_total
p5g_install_cost = p5g_capex_raw * p5g_install_percent
p5g_capex = p5g_capex_raw + p5g_install_cost

p5g_opex = p5g_capex * p5g_maint * years
p5g_total = (p5g_capex + p5g_opex) * sla_multiplier(sla) * growth_multiplier(growth, years)

# ============================================================
# HYBRID
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
# GRAPH CONTROL
# ============================================================

st.markdown('<div class="section-title">📊 Graph Controls</div>', unsafe_allow_html=True)

show_wifi = st.checkbox("Show Wi-Fi", True)
show_p5g = st.checkbox("Show Private 5G", True)
show_hybrid = st.checkbox("Show Hybrid", True)

# ============================================================
# STACKED CAPEX BREAKDOWN
# ============================================================

st.markdown('<div class="section-title">2️⃣ CAPEX Composition Breakdown</div>', unsafe_allow_html=True)

fig_stack = go.Figure()

if show_wifi:
    fig_stack.add_trace(go.Bar(name="Wi-Fi Access", x=["Wi-Fi"], y=[wifi_access_cost]))
    fig_stack.add_trace(go.Bar(name="Wi-Fi Switch", x=["Wi-Fi"], y=[wifi_switch_total]))
    fig_stack.add_trace(go.Bar(name="Wi-Fi Core", x=["Wi-Fi"], y=[wifi_core_total]))
    fig_stack.add_trace(go.Bar(name="Wi-Fi Install", x=["Wi-Fi"], y=[wifi_install_cost]))

if show_p5g:
    fig_stack.add_trace(go.Bar(name="5G Radio", x=["Private 5G"], y=[p5g_radio_cost]))
    fig_stack.add_trace(go.Bar(name="5G Core", x=["Private 5G"], y=[p5g_core_total]))
    fig_stack.add_trace(go.Bar(name="5G Edge", x=["Private 5G"], y=[p5g_edge_total]))
    fig_stack.add_trace(go.Bar(name="5G Backhaul", x=["Private 5G"], y=[p5g_backhaul_total]))
    fig_stack.add_trace(go.Bar(name="5G Install", x=["Private 5G"], y=[p5g_install_cost]))

fig_stack.update_layout(barmode='stack', template="plotly_white")
st.plotly_chart(fig_stack, use_container_width=True)

# ============================================================
# TOTAL CAPEX COMPARISON
# ============================================================

st.markdown('<div class="section-title">3️⃣ Total CAPEX Comparison</div>', unsafe_allow_html=True)

fig_capex = go.Figure()

if show_wifi:
    fig_capex.add_trace(go.Bar(name="Wi-Fi", x=["CAPEX"], y=[wifi_capex]))
if show_p5g:
    fig_capex.add_trace(go.Bar(name="Private 5G", x=["CAPEX"], y=[p5g_capex]))
if show_hybrid:
    fig_capex.add_trace(go.Bar(name="Hybrid", x=["CAPEX"], y=[hyb_capex]))

fig_capex.update_layout(barmode="group", template="plotly_white")
st.plotly_chart(fig_capex, use_container_width=True)

# ============================================================
# INVESTMENT TREND
# ============================================================

st.markdown('<div class="section-title">4️⃣ Investment Trend (Cumulative)</div>', unsafe_allow_html=True)

years_list = list(range(1, years+1))

fig_trend = go.Figure()

if show_wifi:
    wifi_trend = [wifi_capex + wifi_capex*wifi_maint*y for y in years_list]
    fig_trend.add_trace(go.Scatter(x=years_list, y=wifi_trend,
                                   mode='lines+markers', name='Wi-Fi'))

if show_p5g:
    p5g_trend = [p5g_capex + p5g_capex*p5g_maint*y for y in years_list]
    fig_trend.add_trace(go.Scatter(x=years_list, y=p5g_trend,
                                   mode='lines+markers', name='Private 5G'))

if show_hybrid:
    hyb_trend = [hyb_capex + hyb_capex*wifi_maint*y for y in years_list]
    fig_trend.add_trace(go.Scatter(x=years_list, y=hyb_trend,
                                   mode='lines+markers', name='Hybrid'))

fig_trend.update_layout(template="plotly_white")
st.plotly_chart(fig_trend, use_container_width=True)