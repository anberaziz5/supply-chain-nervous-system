import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import pickle
import sys
import os

# Add AI module to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.triage import generate_mitigation_strategy

# --- CINEMATIC DARK MODE CSS ---
st.set_page_config(page_title="OpsNervousSystem", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0f1115; color: #e2e8f0; }
    h1, h2, h3 { color: #10b981; font-family: 'Inter', sans-serif; }
    .stMetric { background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); padding: 15px; border-radius: 8px; backdrop-filter: blur(10px); }
    .stButton>button { background-color: #10b981; color: #000000; font-weight: bold; border: none; border-radius: 4px; }
    .stButton>button:hover { background-color: #059669; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Predictive Supply Chain Nervous System")
st.caption("Machine Learning Engine: XGBoost | Real-time Logistic Telemetry & AI Mitigation")

# Load Model & Data
@st.cache_resource
def load_ml_assets():
    with open("models/saved/xgboost_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("models/saved/encoders.pkl", "rb") as f:
        encoders = pickle.load(f)
    df = pd.read_csv("data/historical_logistics.csv").sample(50) # Load a sample of active shipments
    return model, encoders, df

model, encoders, df = load_ml_assets()

# --- PREDICTION PIPELINE ---
def predict_risk(row):
    features = pd.DataFrame([{
        "Origin_Port": encoders["Origin_Port"].transform([row["Origin_Port"]])[0],
        "Destination_Port": encoders["Destination_Port"].transform([row["Destination_Port"]])[0],
        "Carrier": encoders["Carrier"].transform([row["Carrier"]])[0],
        "Weather_En_Route": encoders["Weather_En_Route"].transform([row["Weather_En_Route"]])[0],
        "Container_Weight_Tons": row["Container_Weight_Tons"],
        "Port_Congestion_Index": row["Port_Congestion_Index"],
        "Route_Distance_NM": row["Route_Distance_NM"]
    }])
    probability = model.predict_proba(features)[0][1]
    return round(probability * 100, 1)

df["Risk_Score_%"] = df.apply(predict_risk, axis=1)
df = df.sort_values(by="Risk_Score_%", ascending=False)

# --- DASHBOARD UI ---
col1, col2, col3 = st.columns(3)
col1.metric("Active Shipments", len(df))
col2.metric("Critical Risks (>70%)", len(df[df["Risk_Score_%"] > 70]))
col3.metric("Network Congestion Avg", f"{df['Port_Congestion_Index'].mean():.2f}")

st.markdown("---")

col_map, col_data = st.columns([2, 1])

with col_map:
    st.subheader("Global Anomaly Radar")
    # Port coordinates for geographic visualization
    port_coords = {
        "Rotterdam": [51.92, 4.47], "Singapore": [1.35, 103.81], "Los Angeles": [33.72, -118.26],
        "Shanghai": [31.23, 121.47], "Hamburg": [53.55, 9.99], "Dubai": [25.27, 55.22]
    }
    
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB dark_matter")
    for _, row in df.head(10).iterrows():
        color = "red" if row["Risk_Score_%"] > 70 else "orange" if row["Risk_Score_%"] > 40 else "green"
        folium.CircleMarker(
            location=port_coords[row["Origin_Port"]],
            radius=row["Risk_Score_%"] / 10,
            color=color, fill=True, popup=f"{row['Shipment_ID']} - Risk: {row['Risk_Score_%']}%"
        ).add_to(m)
    st_folium(m, width=800, height=400)

with col_data:
    st.subheader("High-Risk Queue")
    st.dataframe(df[["Shipment_ID", "Origin_Port", "Carrier", "Risk_Score_%"]].head(8), hide_index=True)

st.markdown("---")
st.subheader("🤖 Autonomous AI Triage")

triage_target = st.selectbox("Select Shipment to Generate Mitigation Plan", df[df["Risk_Score_%"] > 60]["Shipment_ID"])
if st.button("Initialize Triage Protocol"):
    target_data = df[df["Shipment_ID"] == triage_target].iloc[0]
    with st.spinner("AI analyzing network topography and drafting operational shift..."):
        plan = generate_mitigation_strategy(
            target_data["Shipment_ID"], target_data["Origin_Port"], target_data["Destination_Port"],
            target_data["Risk_Score_%"], target_data["Weather_En_Route"], target_data["Port_Congestion_Index"]
        )
        st.success("Triage Plan Generated")
        st.markdown(plan)