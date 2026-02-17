import streamlit as st
st.write("App is starting...")

import plotly.graph_objects as go
from logic import WirelessTCOModel

st.set_page_config(page_title="Enterprise Wireless TCO Model", layout="wide")
st.title("📊 Wireless Strategy Optimizer: Private 5G vs Wi-Fi 6E")

st.sidebar.header("Facility Parameters")
sqft = st.sidebar.number_input("Facility Square Footage", value=500000)
years = st.sidebar.slider("Analysis Horizon (Years)", 1, 10, 5)

model = WirelessTCOModel(facility_sqft=sqft, years=years)

wifi_tco = model.calculate_wifi_tco()
p5g_tco = model.calculate_p5g_tco()

st.subheader(f"Total Cost Comparison over {years} Years")

fig = go.Figure(data=[
    go.Bar(name="Wi-Fi 6E", x=["TCO"], y=[wifi_tco]),
    go.Bar(name="Private 5G", x=["TCO"], y=[p5g_tco])
])

fig.update_layout(barmode="group")
st.plotly_chart(fig, use_container_width=True)