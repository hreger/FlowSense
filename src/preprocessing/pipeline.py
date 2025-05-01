import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

class DataPreprocessor:
    def __init__(self):
        self.data_buffer = []
        self.window_size = 60  # 1 hour with 1-minute samples
        
    async def process_sensor_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        # Store in buffer
        self.data_buffer.append(data)
        if len(self.data_buffer) > self.window_size:
            self.data_buffer.pop(0)
            
        # Process data
        processed_data = self._apply_preprocessing(data)
        
        return processed_data
        
    def _apply_preprocessing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        processed = {}
        
        # Remove outliers and smooth data
        for sensor_id, sensor_data in data.items():
            if isinstance(sensor_data, dict):
                processed[sensor_id] = self._process_sensor_metrics(sensor_data)
                
        # Add derived features
        if len(self.data_buffer) >= 2:
            processed['derived_features'] = self._calculate_derived_features()
            
        return processed
        
    def _process_sensor_metrics(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        processed_data = sensor_data.copy()
        
        # Remove obvious outliers
        for key, value in sensor_data.items():
            if isinstance(value, (int, float)):
                if self._is_outlier(value):
                    processed_data[key] = self._get_last_valid_value(key)
                    
        return processed_data
        
    def _is_outlier(self, value: float) -> bool:
        # Simple outlier detection
        if not self.data_buffer:
            return False
            
        recent_values = [float(d.get(value, 0)) for d in self.data_buffer[-10:]]
        mean = np.mean(recent_values)
        std = np.std(recent_values)
        z_score = (value - mean) / std if std != 0 else 0
        
        return abs(z_score) > 3
        
    def _get_last_valid_value(self, key: str) -> float:
        for data in reversed(self.data_buffer[:-1]):
            if key in data and not self._is_outlier(data[key]):
                return data[key]
        return 0.0
        
    def _calculate_derived_features(self) -> Dict[str, float]:
        # Calculate derived features from recent data
        return {
            "rate_of_change": self._calculate_rate_of_change(),
            "trend": self._calculate_trend()
        }
        
    def _calculate_rate_of_change(self) -> float:
        # Calculate rate of change for the primary metric
        if len(self.data_buffer) < 2:
            return 0.0
        
        latest = self.data_buffer[-1]
        previous = self.data_buffer[-2]
        
        # Example for flow rate
        if "flow_rate" in latest and "flow_rate" in previous:
            return latest["flow_rate"] - previous["flow_rate"]
        return 0.0
        
    def _calculate_trend(self) -> float:
        # Calculate trend over the last hour
        if len(self.data_buffer) < self.window_size:
            return 0.0
            
        values = [d.get("flow_rate", 0) for d in self.data_buffer]
        return np.polyfit(range(len(values)), values, 1)[0]