from src.sensors import SensorType, SensorConfig, SensorNetwork
from src.sensors.manager import SensorManager
from src.cloud.aws_iot import IoTCore
from src.preprocessing.pipeline import DataPreprocessor
import asyncio
import os

async def main():
    # Create a sensor network
    network = SensorNetwork()
    
    # Add sensors
    flow_meter_config = SensorConfig(
        sensor_id="FM001",
        sensor_type=SensorType.FLOW_METER,
        location={"latitude": 23.4567, "longitude": 78.9012},
        sampling_rate=300,
        measurement_unit="cubic_meters_per_second",
        alert_thresholds={"min_flow": 0.5, "max_flow": 100.0}
    )
    
    rainfall_gauge_config = SensorConfig(
        sensor_id="RG001",
        sensor_type=SensorType.RAINFALL_GAUGE,
        location={"latitude": 23.4567, "longitude": 78.9012},
        sampling_rate=3600,
        measurement_unit="millimeters",
        alert_thresholds={"heavy_rainfall": 50.0}
    )
    
    soil_moisture_config = SensorConfig(
        sensor_id="SM001",
        sensor_type=SensorType.SOIL_MOISTURE,
        location={"latitude": 23.4567, "longitude": 78.9012},
        sampling_rate=1800,
        measurement_unit="percentage",
        alert_thresholds={"min_moisture": 20.0, "max_moisture": 80.0}
    )
    
    network.add_sensor(flow_meter_config)
    network.add_sensor(rainfall_gauge_config)
    network.add_sensor(soil_moisture_config)
    
    # Initialize components
    manager = SensorManager(network)
    preprocessor = DataPreprocessor()
    
    # AWS IoT Core setup
    iot = IoTCore(
        endpoint=os.getenv("AWS_IOT_ENDPOINT"),
        cert_path=os.getenv("AWS_CERT_PATH"),
        key_path=os.getenv("AWS_KEY_PATH")
    )
    
    await manager.initialize_sensors()
    await iot.connect()
    
    try:
        while True:
            # Collect raw data
            raw_data = await manager.collect_data()
            
            # Preprocess data
            processed_data = await preprocessor.process_sensor_data(raw_data)
            
            # Publish to AWS IoT Core
            await iot.publish_data("sensors/data", processed_data)
            
            print("Processed Data:", processed_data)
            await asyncio.sleep(300)  # 5-minute intervals
            
    finally:
        await manager.shutdown_all()
        await iot.disconnect()

if __name__ == "__main__":
    asyncio.run(main())