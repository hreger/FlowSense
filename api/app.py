from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json

app = FastAPI(
    title="FlowSense API",
    description="River Flow Prediction & Rural Water Allocation System",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SensorData(BaseModel):
    timestamp: datetime
    location: str
    flow_rate: float
    water_level: float
    turbidity: float
    rainfall: float
    soil_moisture: float

@app.get("/")
async def root():
    return {
        "message": "Welcome to FlowSense API",
        "version": "0.1.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "operational",
            "sensors": "operational",
            "ml_model": "initializing"
        }
    }

@app.post("/sensor-data")
async def receive_sensor_data(data: SensorData):
    try:
        # Placeholder for data processing
        return {
            "status": "success",
            "message": "Data received successfully",
            "timestamp": data.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sensor-status")
async def sensor_status():
    # Placeholder for sensor status
    return {
        "flow_meter": "active",
        "rainfall_gauge": "active",
        "soil_moisture": "active"
    }