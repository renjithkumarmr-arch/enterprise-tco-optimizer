import streamlit as st
import plotly.graph_objects as go
import math

# ============================================================
# Vendor Profiles (Simulated Enterprise Pricing)
# ============================================================

VENDORS = {
    "Cisco": {"wifi_ap":1300, "p5g_cell":5200, "core":85000, "wifi_maint":0.18, "p5g_maint":0.16},
    "Nokia": {"wifi_ap":1200, "p5g_cell":5000, "core":80000, "wifi_maint":0.17, "p5g_maint":0.15},
    "Ericsson": {"wifi_ap":1250, "p5g_cell":5500, "core":90000, "wifi_maint":0.19, "p5g_maint":0.17}
}

# ============================================================
# Decision Model
# ============================================================

class DecisionModel:
    def __init__(self, sqft, years, vendor, growth, latency, sla, coverage):
        self.sqft = sqft
        self.years = years
        self.vendor = VENDORS[vendor]
        self.growth = growth
        self.latency = latency
        self.sla = sla
        self.coverage = coverage

    def sla_multiplier(self):
        return {"99.9%":1.0, "99.99%":1.08, "99.999%":1.15}[self.sla]

    def growth_multiplier(self):
        return (1 + self.growth/100) ** self.years

    def wifi(self):
        ap = math.ceil(self.sqft/2500)
        if self.coverage == "Indoor + Outdoor":
            ap *= 1.2
        capex = ap * self.vendor["wifi_ap"]
        opex = capex * self.vendor["wifi_maint"] * self.years
        total = (capex + opex) * self.sla_multiplier() * self.growth_multiplier()
        if self.latency < 10:
            total *= 1.10
        return capex, opex, total

    def p5g(self):
        cells = math.ceil(self.sqft/10000)
        if self.coverage == "Indoor + Outdoor":
            cells *= 1.15
        capex = cells * self.vendor["p5g_cell"] + self.vendor["core"]
        opex = capex * self.vendor["p5g_maint"] * self.years
        total = (capex + opex) * self.sla_multiplier() * self.growth_multiplier()
        return capex, opex, total

    def hybrid(self):
        w_capex, w_opex, _ = self.wifi()
        p_capex, p_opex, _ = self.p5g()
        capex = (w_capex*0.6) + (p_capex*0.6)
        opex = (w_opex*0.6) + (p_opex*0.6)
        total = (capex + opex) * self.sla_multiplier() * self.growth_multiplier()
        return capex, opex, total


# ============================================================
# UI
# ============================================================

st.set_page_config(layout="wide")
st.title("🏛 Enterprise Wireless Final Decision Engine")

# Sidebar Inputs
st.sidebar.header("Strategic Inputs")

sqft = st.sidebar.number_input("Facility Size (sqft)", 1000, 10000000, 500000, 10000)
years = st.sidebar.slider("Investment Horizon (Years)", 3, 10, 5)
vendor = st.sidebar.selectbox("Vendor", ["Cisco","Nokia","Ericsson"])
growth = st.sidebar.slider("Annual Device Growth (%)",0,30,8)
latency = st.sidebar.slider("Latency Requirement (ms)",1,50,15)
sla = st.sidebar.selectbox("Availability Target",["99.9%","99.99%","99.999%"])
coverage = st.sidebar.selectbox("Coverage Type",["Indoor Only","Indoor + Outdoor"])

model = DecisionModel(sqft, years, vendor, growth, latency, sla, coverage)

wifi_capex, wifi_opex, wifi_total = model.wifi()
p5g_capex, p5g_opex, p5g_total = model.p5g()
hyb_capex, hyb_opex, hyb_total = model.hybrid()

# ============================================================
# 1️⃣ EXECUTIVE DECISION SUMMARY
# ============================================================

st.header("1️⃣ Executive Investment Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Wi-Fi 5Y TCO", f"${wifi_total:,.0f}")
col2.metric("Private 5G 5Y TCO", f"${p5g_total:,.0f}")
col3.metric("Hybrid 5Y TCO", f"${hyb_total:,.0f}")

annual_wifi = wifi_total/years
annual_p5g = p5g_total/years
annual_hyb = hyb_total/years

st.markdown("**Annualized Run-Rate Impact:**")
st.write(f"Wi-Fi: ${annual_wifi:,.0f} per year")
st.write(f"Private 5G: ${annual_p5g:,.0f} per year")
st.write(f"Hybrid: ${annual_hyb:,.0f} per year")

# ============================================================
# 2️⃣ FINANCIAL STRUCTURE
# ============================================================

st.header("2️⃣ Capital vs Operational Structure")

fig_capex = go.Figure()
fig_capex.add_trace(go.Bar(name="CAPEX", x=["Wi-Fi","Private 5G","Hybrid"],
                           y=[wifi_capex,p5g_capex,hyb_capex]))
st.plotly_chart(fig_capex, use_container_width=True)

fig_opex = go.Figure()
fig_opex.add_trace(go.Bar(name="OPEX (5Y)", x=["Wi-Fi","Private 5G","Hybrid"],
                          y=[wifi_opex,p5g_opex,hyb_opex]))
st.plotly_chart(fig_opex, use_container_width=True)

# ============================================================
# 3️⃣ STRATEGIC FIT ANALYSIS
# ============================================================

st.header("3️⃣ Strategic Fit Outlook")

if latency < 10:
    st.info("Low latency requirement increases strategic advantage of Private 5G.")

if growth > 15:
    st.info("High device growth favors scalable architecture (Private 5G or Hybrid).")

if sla == "99.999%":
    st.info("Ultra-high availability target increases operational complexity and cost.")

# ============================================================
# 4️⃣ FINAL RECOMMENDATION ENGINE
# ============================================================

st.header("4️⃣ Decision Recommendation")

cheapest = min(wifi_total, p5g_total, hyb_total)

if cheapest == wifi_total:
    st.success("Recommendation: Wi-Fi 6E provides lowest financial exposure under current assumptions.")
elif cheapest == p5g_total:
    st.success("Recommendation: Private 5G offers better long-term value given scale and SLA requirements.")
else:
    st.success("Recommendation: Hybrid architecture balances cost, scalability, and resilience.")
