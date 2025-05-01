from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class SensorType(Enum):
    FLOW_METER = "flow_meter"
    RAINFALL_GAUGE = "rainfall_gauge"
    SOIL_MOISTURE = "soil_moisture"
    WATER_QUALITY = "water_quality"

@dataclass
class SensorConfig:
    sensor_id: str
    sensor_type: SensorType
    location: Dict[str, float]  # {latitude: float, longitude: float}
    sampling_rate: int  # in seconds
    measurement_unit: str
    alert_thresholds: Optional[Dict[str, float]] = None

class SensorNetwork:
    def __init__(self):
        self.sensors: Dict[str, SensorConfig] = {}
        
    def add_sensor(self, config: SensorConfig):
        self.sensors[config.sensor_id] = config
        
    def get_sensor_config(self, sensor_id: str) -> Optional[SensorConfig]:
        return self.sensors.get(sensor_id)

# Default configurations for different sensor types
DEFAULT_CONFIGS = {
    SensorType.FLOW_METER: {
        "sampling_rate": 300,  # 5 minutes
        "measurement_unit": "cubic_meters_per_second",
        "alert_thresholds": {
            "min_flow": 0.5,
            "max_flow": 100.0
        }
    },
    SensorType.RAINFALL_GAUGE: {
        "sampling_rate": 3600,  # 1 hour
        "measurement_unit": "millimeters",
        "alert_thresholds": {
            "heavy_rainfall": 50.0  # mm/hour
        }
    },
    SensorType.SOIL_MOISTURE: {
        "sampling_rate": 1800,  # 30 minutes
        "measurement_unit": "percentage",
        "alert_thresholds": {
            "min_moisture": 20.0,
            "max_moisture": 80.0
        }
    },
    SensorType.WATER_QUALITY: {
        "sampling_rate": 900,  # 15 minutes
        "measurement_unit": "multi_parameter",
        "alert_thresholds": {
            "ph_min": 6.5,
            "ph_max": 8.5,
            "turbidity_max": 5.0
        }
    }
}