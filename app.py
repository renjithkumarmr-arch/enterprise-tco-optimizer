import streamlit as st
import plotly.graph_objects as go
import math

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
    def __init__(self, sqft, years, vendor, growth_rate, latency, sla, coverage):
        self.sqft = sqft
        self.years = years
        self.vendor = VENDOR_PRICING[vendor]
        self.growth_rate = growth_rate
        self.latency = latency
        self.sla = sla
        self.coverage = coverage

    def sla_multiplier(self):
        return {"99.9%":1.0, "99.99%":1.08, "99.999%":1.15}[self.sla]

    def growth_multiplier(self):
        return (1 + self.growth_rate/100) ** self.years

    def wifi(self):
        ap = math.ceil(self.sqft / 2500)
        if self.coverage == "Indoor + Outdoor":
            ap *= 1.2
        capex = ap * self.vendor["wifi_ap_cost"]
        opex = capex * self.vendor["maintenance_wifi"] * self.years
        total = (capex + opex) * self.sla_multiplier() * self.growth_multiplier()
        if self.latency < 10:
            total *= 1.10
        return capex, opex, total

    def p5g(self):
        cells = math.ceil(self.sqft / 10000)
        if self.coverage == "Indoor + Outdoor":
            cells *= 1.15
        capex = cells * self.vendor["p5g_small_cell_cost"] + self.vendor["core_cost"]
        opex = capex * self.vendor["maintenance_p5g"] * self.years
        total = (capex + opex) * self.sla_multiplier() * self.growth_multiplier()
        return capex, opex, total

    def hybrid(self):
        wifi_capex, wifi_opex, _ = self.wifi()
        p5g_capex, p5g_opex, _ = self.p5g()

        capex = (wifi_capex * 0.6) + (p5g_capex * 0.6)
        opex = (wifi_opex * 0.6) + (p5g_opex * 0.6)
        total = (capex + opex) * self.sla_multiplier() * self.growth_multiplier()
        return capex, opex, total


# ============================================================
# UI
# ============================================================

st.set_page_config(page_title="Enterprise Wireless Economic Engine", layout="wide")
st.title("🌐 Enterprise Wireless Economic Engine")

# Sidebar
st.sidebar.header("🏢 Facility Parameters")

sqft = st.sidebar.number_input("Facility Size (sqft)", 1000, 10000000, 500000, 10000)
years = st.sidebar.slider("Analysis Horizon (Years)", 1, 10, 5)
vendor = st.sidebar.selectbox("Vendor", ["Cisco", "Nokia", "Ericsson"])
growth_rate = st.sidebar.slider("Annual Device Growth (%)", 0, 30, 8)
latency = st.sidebar.slider("Latency Requirement (ms)", 1, 50, 15)
sla = st.sidebar.selectbox("Availability Target", ["99.9%", "99.99%", "99.999%"])
coverage = st.sidebar.selectbox("Coverage Type", ["Indoor Only", "Indoor + Outdoor"])

model = WirelessTCOModel(sqft, years, vendor, growth_rate, latency, sla, coverage)

wifi_capex, wifi_opex, wifi_total = model.wifi()
p5g_capex, p5g_opex, p5g_total = model.p5g()
hyb_capex, hyb_opex, hyb_total = model.hybrid()

# ============================================================
# Executive Summary
# ============================================================

st.header("📊 Executive Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Wi-Fi 6E TCO", f"${wifi_total:,.0f}")
col2.metric("Private 5G TCO", f"${p5g_total:,.0f}")
col3.metric("Hybrid TCO", f"${hyb_total:,.0f}")

cheapest = min(wifi_total, p5g_total, hyb_total)

st.markdown("---")
st.subheader("📌 Cost Insight")

if cheapest == wifi_total:
    delta = (p5g_total - wifi_total) / wifi_total * 100
    st.success(f"Wi-Fi is approximately {delta:.1f}% more cost-efficient than Private 5G.")
elif cheapest == p5g_total:
    delta = (wifi_total - p5g_total) / p5g_total * 100
    st.success(f"Private 5G is approximately {delta:.1f}% more cost-efficient than Wi-Fi.")
else:
    st.success("Hybrid provides balanced investment profile under current assumptions.")

# ============================================================
# Wi-Fi Section
# ============================================================

st.header("📡 Wi-Fi 6E Financials")
st.write(f"CAPEX: ${wifi_capex:,.0f}")
st.write(f"OPEX: ${wifi_opex:,.0f}")

# ============================================================
# Private 5G Section
# ============================================================

st.header("📶 Private 5G Financials")
st.write(f"CAPEX: ${p5g_capex:,.0f}")
st.write(f"OPEX: ${p5g_opex:,.0f}")

# ============================================================
# Hybrid Section
# ============================================================

st.header("🔀 Hybrid Architecture Financials")
st.write(f"CAPEX: ${hyb_capex:,.0f}")
st.write(f"OPEX: ${hyb_opex:,.0f}")

# ============================================================
# CAPEX Chart
# ============================================================

st.header("💰 CAPEX Comparison")

fig_capex = go.Figure()
fig_capex.add_trace(go.Bar(name="CAPEX", x=["Wi-Fi", "Private 5G", "Hybrid"],
                           y=[wifi_capex, p5g_capex, hyb_capex]))
fig_capex.update_layout(template="plotly_white")
st.plotly_chart(fig_capex, use_container_width=True)

# ============================================================
# OPEX Chart
# ============================================================

st.header("📉 OPEX Comparison")

fig_opex = go.Figure()
fig_opex.add_trace(go.Bar(name="OPEX", x=["Wi-Fi", "Private 5G", "Hybrid"],
                          y=[wifi_opex, p5g_opex, hyb_opex]))
fig_opex.update_layout(template="plotly_white")
st.plotly_chart(fig_opex, use_container_width=True)