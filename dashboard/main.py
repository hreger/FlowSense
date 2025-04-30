import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="FlowSense Dashboard",
    page_icon="🌊",
    layout="wide"
)

st.title("🌊 FlowSense Monitoring Dashboard")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Sensor Data", "Analytics"])

if page == "Overview":
    st.header("System Overview")
    
    # System Status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Active Sensors", value="3/3")
    with col2:
        st.metric(label="Data Points Today", value="1,420")
    with col3:
        st.metric(label="System Uptime", value="99.9%")

    # Placeholder for real-time data
    st.subheader("Real-time Flow Rate")
    placeholder_data = np.random.rand(100) * 10
    fig = go.Figure(data=go.Scatter(y=placeholder_data))
    st.plotly_chart(fig)

elif page == "Sensor Data":
    st.header("Sensor Readings")
    # Placeholder for sensor data
    
elif page == "Analytics":
    st.header("Basic Analytics")
    # Placeholder for analytics