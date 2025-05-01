from ..interface import SensorInterface
from ..config import SensorConfig
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from typing import Dict, Any

class SoilMoistureSensor(SensorInterface):
    def __init__(self, config: SensorConfig):
        super().__init__(config)
        self.i2c = None
        self.ads = None
        self.chan = None
        
    async def initialize(self) -> bool:
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(self.i2c)
            self.chan = AnalogIn(self.ads, ADS.P0)
            self.is_active = True
            return True
        except Exception as e:
            print(f"Error initializing soil moisture sensor: {e}")
            return False
            
    async def read_data(self) -> Dict[str, Any]:
        if not self.is_active:
            return {"error": "Sensor not active"}
            
        voltage = self.chan.voltage
        moisture = self._convert_to_moisture(voltage)
        
        data = {
            "moisture": moisture,
            "unit": self.config.measurement_unit,
            "voltage": voltage
        }
        
        alerts = self.check_thresholds({"moisture": moisture})
        data["alerts"] = alerts
        
        return data
        
    def _convert_to_moisture(self, voltage: float) -> float:
        # Convert voltage to moisture percentage
        # This is a simplified conversion - calibrate based on your soil type
        return max(0, min(100, (voltage / 3.3) * 100))
        
    async def calibrate(self) -> bool:
        if not self.is_active:
            return False
        # Perform calibration routine
        return True
        
    async def shutdown(self) -> bool:
        self.is_active = False
        return True