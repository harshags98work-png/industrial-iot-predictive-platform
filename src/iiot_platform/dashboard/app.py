import os

import httpx
import pandas as pd
import plotly.express as px
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Industrial IoT Monitor", page_icon="⚙️", layout="wide")
st.title("Industrial IoT Monitor")
st.caption("Synthetic equipment telemetry • MQTT + OPC-UA • Isolation Forest scoring")


@st.cache_data(ttl=3)
def fetch(path: str, params: dict | None = None):
    with httpx.Client(base_url=API_BASE_URL, timeout=5) as client:
        response = client.get(path, params=params)
        response.raise_for_status()
        return response.json()


try:
    equipment = fetch("/api/v1/equipment")
except (httpx.HTTPError, ValueError) as exc:
    st.error(f"The API is not ready: {exc}")
    st.stop()

if not equipment:
    st.info("Waiting for collectors to store their first readings. Refresh in a few seconds.")
    st.stop()

equipment_by_label = {f"{item['name']} ({item['id']})": item for item in equipment}
selection = st.sidebar.selectbox("Equipment", list(equipment_by_label))
selected = equipment_by_label[selection]
window = st.sidebar.slider("History points", min_value=25, max_value=500, value=150, step=25)

status = fetch(f"/api/v1/equipment/{selected['id']}/status")
readings = fetch(f"/api/v1/equipment/{selected['id']}/readings", {"limit": window})
anomalies = fetch(
    "/api/v1/anomalies",
    {"equipment_id": selected["id"], "limit": 20, "anomalous_only": True},
)

health = status["health"]
latest = status["latest_reading"] or {}
columns = st.columns(5)
columns[0].metric("Health", health.upper())
columns[1].metric("Temperature", f"{latest.get('temperature_c', 0):.1f} °C")
columns[2].metric("Vibration", f"{latest.get('vibration_mm_s', 0):.2f} mm/s")
columns[3].metric("Current", f"{latest.get('current_a', 0):.1f} A")
columns[4].metric("Pressure", f"{latest.get('pressure_bar', 0):.1f} bar")

frame = pd.DataFrame(readings)
if not frame.empty:
    frame["observed_at"] = pd.to_datetime(frame["observed_at"], utc=True)
    frame = frame.sort_values("observed_at")
    plot_frame = frame.melt(
        id_vars=["observed_at"],
        value_vars=["temperature_c", "vibration_mm_s", "current_a", "pressure_bar"],
        var_name="signal",
        value_name="value",
    )
    figure = px.line(
        plot_frame,
        x="observed_at",
        y="value",
        facet_row="signal",
        color="signal",
        height=720,
        title="Recent sensor trends",
    )
    figure.update_yaxes(matches=None)
    figure.for_each_annotation(
        lambda annotation: annotation.update(text=annotation.text.split("=")[-1])
    )
    figure.update_layout(showlegend=False)
    st.plotly_chart(figure, use_container_width=True)

st.subheader("Recent anomaly events")
if anomalies:
    anomaly_frame = pd.DataFrame(anomalies)[
        ["scored_at", "score", "model_version", "explanation"]
    ]
    st.dataframe(anomaly_frame, use_container_width=True, hide_index=True)
else:
    st.success("No anomalies in the selected recent window.")

st.caption(f"Source protocol: {selected['protocol'].upper()} • Location: {selected['location']}")
