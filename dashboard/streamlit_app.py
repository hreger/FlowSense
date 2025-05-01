import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
from datetime import datetime, timedelta
import requests
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# Database connection
conn_str = "postgresql://postgres:arif@localhost:5432/flowsense"
engine = create_engine(conn_str)

# App title
st.title("Amazon River Monitoring Dashboard")
st.subheader("Real-time data from public databases")

# Data sources and their APIs
SOURCES = {
    "USGS Water Services": "https://waterservices.usgs.gov/nwis/iv/",
    "NASA GRACE": "https://grace.jpl.nasa.gov/data/get-data/",
    "NOAA NCEI": "https://www.ncei.noaa.gov/access/services/data/v1",
    "Global Runoff Data Centre": "https://portal.grdc.bafg.de/applications/public.html",
    "ANA Hidroweb": "http://www.snirh.gov.br/hidroweb/serieshistoricas"
}

# Time range selector
time_range = st.selectbox(
    "Select Time Range",
    ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week", "Last Month"]
)

# Convert time range to timedelta
range_dict = {
    "Last Hour": timedelta(hours=1),
    "Last 6 Hours": timedelta(hours=6),
    "Last 24 Hours": timedelta(hours=24),
    "Last Week": timedelta(days=7),
    "Last Month": timedelta(days=30)
}

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_ana_data(data_type, time_delta):
    """Fetch data from ANA public endpoints"""
    try:
        if data_type == "flow_meter":
            # Example stations in Amazon basin
            stations = ["17093000", "17050001", "17090000"]  # Manaus, Óbidos, and Santarém
            
            data = []
            for station in stations:
                url = f"http://www.snirh.gov.br/hidroweb/rest/api/documento/convencionais/{station}"
                response = requests.get(url)
                if response.status_code == 200:
                    json_data = response.json()
                    # Process flow data
                    for reading in json_data.get('dados', []):
                        data.append({
                            'time': pd.to_datetime(reading['data']),
                            'value': float(reading.get('vazao', 0)),  # flow rate
                            'sensor_id': f"ANA_FLOW_{station}"
                        })
            
            return pd.DataFrame(data) if data else pd.DataFrame()
            
        elif data_type == "rainfall":
            # Example rainfall stations in Amazon basin
            stations = ["00359000", "00360000", "00361000"]
            
            data = []
            for station in stations:
                url = f"http://www.snirh.gov.br/hidrotelemetria/SerieHistorica/{station}"
                response = requests.get(url)
                if response.status_code == 200:
                    json_data = response.json()
                    # Process rainfall data
                    for reading in json_data.get('dados', []):
                        data.append({
                            'time': pd.to_datetime(reading['data']),
                            'value': float(reading.get('chuva', 0)),  # rainfall
                            'sensor_id': f"ANA_RAIN_{station}"
                        })
            
            return pd.DataFrame(data) if data else pd.DataFrame()
    
    except Exception as e:
        st.error(f"Error fetching ANA data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_usgs_data(time_delta):
    """Fetch data from USGS Water Services"""
    try:
        # USGS API key from environment variables
        usgs_api_key = os.getenv("USGS_API_KEY")
        
        # Amazon basin USGS stations
        stations = ["15030000", "15040000", "15050000"]  # Example station IDs
        
        end_date = datetime.now()
        start_date = end_date - time_delta
        
        data = []
        for station in stations:
            url = f"https://waterservices.usgs.gov/nwis/iv/"
            params = {
                "format": "json",
                "sites": station,
                "startDT": start_date.isoformat(),
                "endDT": end_date.isoformat(),
                "parameterCd": "00060",  # Discharge
                "siteStatus": "all",
                "access": usgs_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                json_data = response.json()
                if 'value' in json_data and 'timeSeries' in json_data['value']:
                    values = json_data['value']['timeSeries'][0]['values'][0]['value']
                    for v in values:
                        data.append({
                            'time': pd.to_datetime(v['dateTime']),
                            'value': float(v['value']),
                            'sensor_id': f"USGS_{station}"
                        })
            
        return pd.DataFrame(data) if data else pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error fetching USGS data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def optimize_dataframe(df):
    """Optimize DataFrame memory usage"""
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = pd.to_numeric(df[col], downcast='float')
        elif df[col].dtype == 'int64':
            df[col] = pd.to_numeric(df[col], downcast='integer')
    return df

@st.cache_data(ttl=300)
def load_amazon_data(data_type, time_delta):
    if data_type == "flow_meter":
        # Parallel fetch of USGS and ANA data
        with ThreadPoolExecutor(max_workers=2) as executor:
            usgs_future = executor.submit(fetch_usgs_data, time_delta)
            ana_future = executor.submit(fetch_ana_data, "flow_meter", time_delta)
            
            usgs_data = usgs_future.result()
            ana_data = ana_future.result()
            
        return pd.concat([usgs_data, ana_data]) if not ana_data.empty else usgs_data
    
    elif data_type == "rainfall":
        # Combine NOAA and ANA rainfall data
        noaa_data = fetch_noaa_data(time_delta)
        ana_data = fetch_ana_data("rainfall", time_delta)
        return pd.concat([noaa_data, ana_data]) if not ana_data.empty else noaa_data
    
    elif data_type == "soil_moisture":
        try:
            # NASA GRACE API
            nasa_api_key = os.getenv("NASA_API_KEY")
            bbox = "-73.98,-3.43,-50.79,5.27"
            
            url = f"https://api.nasa.gov/planetary/earth/assets"
            params = {
                "lon": "-60.0",  # Center of Amazon basin
                "lat": "0.0",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "dim": 0.25,
                "api_key": nasa_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                json_data = response.json()
                data = pd.DataFrame(json_data['results'])
                data['time'] = pd.to_datetime(data['date'])
                data['value'] = data['soil_moisture']
                data['sensor_id'] = "GRACE_SOIL"
                return data[['time', 'value', 'sensor_id']]
        except Exception as e:
            st.error(f"Error fetching NASA GRACE data: {str(e)}")
    
    elif data_type == "sediment_level":
        try:
            stations = ["15400000", "15030000"]
            data = []
            for station in stations:
                url = f"http://www.snirh.gov.br/hidroweb/rest/api/documento/convencionais/{station}"
                response = requests.get(url)
                if response.status_code == 200:
                    json_data = response.json()
                    station_data = pd.DataFrame(json_data['dados'])
                    station_data['time'] = pd.to_datetime(station_data['data'])
                    station_data['value'] = station_data['sedimentos']
                    station_data['sensor_id'] = f"ANA_{station}"
                    data.append(station_data[['time', 'value', 'sensor_id']])
            
            return pd.concat(data) if data else pd.DataFrame()
        except Exception as e:
            st.error(f"Error fetching sediment data: {str(e)}")
    
    elif data_type == "sea_level":
        try:
            noaa_api_key = os.getenv("NOAA_API_KEY")
            station = "8534720"  # Amazon Delta station
            
            url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
            params = {
                "station": station,
                "product": "water_level",
                "datum": "MLLW",
                "units": "metric",
                "time_zone": "GMT",
                "format": "json",
                "begin_date": (datetime.now() - time_delta).strftime("%Y%m%d"),
                "end_date": datetime.now().strftime("%Y%m%d"),
                "application": "FlowSense",
                "api_key": noaa_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                json_data = response.json()
                data = pd.DataFrame(json_data['data'])
                data['time'] = pd.to_datetime(data['t'])
                data['value'] = data['v']
                data['sensor_id'] = f"NOAA_{station}"
                return data[['time', 'value', 'sensor_id']]
        except Exception as e:
            st.error(f"Error fetching NOAA sea level data: {str(e)}")

    # Fallback to sample data if API calls fail
    st.warning(f"Using sample data for {data_type} due to API issues")
    return pd.DataFrame({
        'time': pd.date_range(end=datetime.now(), periods=100, freq='15T'),
        'value': np.random.normal(loc=100, scale=10, size=100),
        'sensor_id': f'SAMPLE_{data_type}_1'
    })

# Initialize session state for tab tracking
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'Flow Rate'

# Create tabs for different measurements
tabs = st.tabs(["Flow Rate", "Rainfall", "Soil Moisture", "Sediment", "Sea Level"])

with tabs[0]:
    st.subheader("Amazon River Flow Rate")
    flow_data = load_amazon_data("flow_meter", range_dict[time_range])
    fig1 = px.line(flow_data, x="time", y="value", color="sensor_id",
                   title="River Discharge Rate",
                   labels={"value": "Flow Rate (m³/s)", "time": "Time"})
    st.plotly_chart(fig1, use_container_width=True)
    
    if not flow_data.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Flow Rate", f"{flow_data['value'].mean():.2f} m³/s")
        with col2:
            st.metric("Max Flow Rate", f"{flow_data['value'].max():.2f} m³/s")
        with col3:
            st.metric("Min Flow Rate", f"{flow_data['value'].min():.2f} m³/s")

# Update current tab in session state (move this to the end)
for tab_idx, tab in enumerate(tabs):
    if tab.selected:
        st.session_state.current_tab = ["Flow Rate", "Rainfall", "Soil Moisture", "Sediment", "Sea Level"][tab_idx]

# Data source information
st.sidebar.title("Data Sources")
for source, url in SOURCES.items():
    st.sidebar.markdown(f"- [{source}]({url})")

# Add data refresh controls
st.sidebar.button("Refresh Data")

# Add metadata about the monitoring stations
st.sidebar.title("Monitoring Stations")
st.sidebar.markdown("""
- Manaus Station (AM)
- Óbidos Station (PA)
- Santarém Station (PA)
""")

# Auto-refresh
st.empty()

# Add request timeout and error handling
def make_api_request(url, params=None, timeout=10):
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.warning(f"Request timeout for {url}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")


@st.cache_data(ttl=300)
def fetch_noaa_data(time_delta):
    """Fetch data from NOAA API"""
    try:
        noaa_api_key = os.getenv("NOAA_API_KEY")
        stations = ["8534720", "8545240"]  # Example NOAA stations
        
        data = []
        for station in stations:
            url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
            params = {
                "station": station,
                "product": "water_level",
                "datum": "MLLW",
                "units": "metric",
                "time_zone": "GMT",
                "format": "json",
                "begin_date": (datetime.now() - time_delta).strftime("%Y%m%d"),
                "end_date": datetime.now().strftime("%Y%m%d"),
                "application": "FlowSense",
                "api_key": noaa_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                json_data = response.json()
                if 'data' in json_data:
                    station_data = pd.DataFrame(json_data['data'])
                    station_data['time'] = pd.to_datetime(station_data['t'])
                    station_data['value'] = pd.to_numeric(station_data['v'])
                    station_data['sensor_id'] = f"NOAA_{station}"
                    data.append(station_data[['time', 'value', 'sensor_id']])
        
        return pd.concat(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching NOAA data: {str(e)}")