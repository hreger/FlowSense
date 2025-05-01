import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.cloud.timescale_db import TimeScaleDB
import asyncio
from datetime import datetime, timedelta

async def load_sensor_data(db: TimeScaleDB, hours: int = 24):
    async with db.pool.acquire() as conn:
        data = await conn.fetch('''
            SELECT time, sensor_id, value, unit
            FROM sensor_data
            WHERE time > NOW() - interval '$1 hours'
            ORDER BY time ASC
        ''', hours)
        return pd.DataFrame(data, columns=['time', 'sensor_id', 'value', 'unit'])

def create_line_plot(df: pd.DataFrame, sensor_id: str):
    sensor_data = df[df['sensor_id'] == sensor_id]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sensor_data['time'],
        y=sensor_data['value'],
        mode='lines+markers',
        name=sensor_id
    ))
    
    fig.update_layout(
        title=f'{sensor_id} Measurements',
        xaxis_title='Time',
        yaxis_title=sensor_data['unit'].iloc[0] if not sensor_data.empty else ''
    )
    
    return fig

async def main():
    st.title('FlowSense Dashboard')
    
    # Initialize database connection
    db = TimeScaleDB(st.secrets["timescale_dsn"])
    await db.connect()
    
    # Sidebar controls
    time_range = st.sidebar.slider('Time Range (hours)', 1, 168, 24)
    
    # Load data
    df = await load_sensor_data(db, time_range)
    
    # Create tabs for different sensor types
    tabs = st.tabs(['Flow Meter', 'Rainfall', 'Soil Moisture'])
    
    with tabs[0]:
        st.plotly_chart(create_line_plot(df, 'FM001'))
        
    with tabs[1]:
        st.plotly_chart(create_line_plot(df, 'RG001'))
        
    with tabs[2]:
        st.plotly_chart(create_line_plot(df, 'SM001'))
        
    # Add real-time alerts section
    st.sidebar.title('Alerts')
    alerts = df[df['value'].apply(lambda x: x > 50)]  # Example threshold
    if not alerts.empty:
        for _, alert in alerts.iterrows():
            st.sidebar.warning(f"High reading from {alert['sensor_id']}: {alert['value']} {alert['unit']}")

if __name__ == "__main__":
    asyncio.run(main())