from abc import ABC, abstractmethod
from typing import Any, Dict
from .config import SensorConfig

class SensorInterface(ABC):
    def __init__(self, config: SensorConfig):
        self.config = config
        self.is_active = False
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the sensor hardware"""
        pass
        
    @abstractmethod
    async def read_data(self) -> Dict[str, Any]:
        """Read current sensor data"""
        pass
        
    @abstractmethod
    async def calibrate(self) -> bool:
        """Calibrate the sensor"""
        pass
        
    @abstractmethod
    async def shutdown(self) -> bool:
        """Safely shutdown the sensor"""
        pass
    
    def check_thresholds(self, data: Dict[str, float]) -> Dict[str, bool]:
        """Check if sensor data exceeds configured thresholds"""
        alerts = {}
        if self.config.alert_thresholds:
            for threshold_name, threshold_value in self.config.alert_thresholds.items():
                if threshold_name.startswith('min_'):
                    param = threshold_name[4:]
                    alerts[threshold_name] = data.get(param, 0) < threshold_value
                elif threshold_name.startswith('max_'):
                    param = threshold_name[4:]
                    alerts[threshold_name] = data.get(param, 0) > threshold_value
        return alerts