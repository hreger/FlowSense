import asyncio
from typing import Dict, List, Any
from .config import SensorNetwork, SensorType
from .collectors.flow_meter import FlowMeterSensor
from .collectors.rainfall_gauge import RainfallGaugeSensor

class SensorManager:
    def __init__(self, network: SensorNetwork):
        self.network = network
        self.active_sensors: Dict[str, Any] = {}
        
    async def initialize_sensors(self):
        for sensor_id, config in self.network.sensors.items():
            sensor_instance = None
            
            if config.sensor_type == SensorType.FLOW_METER:
                sensor_instance = FlowMeterSensor(config)
            elif config.sensor_type == SensorType.RAINFALL_GAUGE:
                sensor_instance = RainfallGaugeSensor(config)
                
            if sensor_instance:
                success = await sensor_instance.initialize()
                if success:
                    self.active_sensors[sensor_id] = sensor_instance
                    
    async def collect_data(self) -> Dict[str, Any]:
        data = {}
        for sensor_id, sensor in self.active_sensors.items():
            if sensor.is_active:
                try:
                    sensor_data = await sensor.read_data()
                    data[sensor_id] = sensor_data
                except Exception as e:
                    print(f"Error reading from sensor {sensor_id}: {e}")
        return data
        
    async def shutdown_all(self):
        for sensor in self.active_sensors.values():
            await sensor.shutdown()
        self.active_sensors.clear()