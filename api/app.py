from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
async def root():
    return {"message": "Welcome to FlowSense API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/sensor-status")
async def sensor_status():
    # Placeholder for sensor status
    return {
        "flow_meter": "active",
        "rainfall_gauge": "active",
        "soil_moisture": "active"
    }