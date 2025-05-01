import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="FlowSense Dashboard",
    page_icon="🌊",
    layout="wide"
)

# Title and Description
st.title("🌊 FlowSense Monitoring Dashboard")
st.markdown("""
    Real-time monitoring system for river flow prediction and water allocation.
    Currently monitoring: **Godavari Basin**
""")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Sensor Data", "Analytics", "Alerts"])

if page == "Overview":
    # System Status
    st.header("System Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Active Sensors", value="3/3", delta="Operational")
    with col2:
        st.metric(label="Data Points Today", value="1,420", delta="+120")
    with col3:
        st.metric(label="System Uptime", value="99.9%", delta="+0.1%")

    # Real-time Flow Rate
    st.subheader("Real-time Flow Rate")
    # Simulated data for demonstration
    times = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                         end=datetime.now(), freq='15T')
    flow_data = np.random.normal(loc=100, scale=10, size=len(times))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=flow_data, mode='lines', name='Flow Rate'))
    fig.update_layout(
        title='24-Hour Flow Rate Monitoring',
        xaxis_title='Time',
        yaxis_title='Flow Rate (m³/s)'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Alert System
    st.subheader("Recent Alerts")
    st.warning("Medium: Increased turbidity detected in Sector A-7")
    st.info("Low: Rainfall prediction updated for next 24 hours")

elif page == "Sensor Data":
    st.header("Sensor Readings")
    # Implement sensor data visualization here

elif page == "Analytics":
    st.header("Analytics Dashboard")
    # Implement analytics visualization here

elif page == "Alerts":
    st.header("Alert Management")
    # Implement alert management system here