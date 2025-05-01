from ..interface import SensorInterface
from ..config import SensorConfig
import RPi.GPIO as GPIO
from typing import Dict, Any

class RainfallGaugeSensor(SensorInterface):
    def __init__(self, config: SensorConfig):
        super().__init__(config)
        self.bucket_size = 0.2  # mm per tip
        self.tip_count = 0
        self.gpio_pin = None
        
    async def initialize(self) -> bool:
        try:
            GPIO.setmode(GPIO.BCM)
            self.gpio_pin = 27  # Default GPIO pin
            GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(self.gpio_pin, GPIO.FALLING, callback=self._tip_callback)
            self.is_active = True
            return True
        except Exception as e:
            print(f"Error initializing rainfall gauge: {e}")
            return False
            
    def _tip_callback(self, channel):
        self.tip_count += 1
        
    async def read_data(self) -> Dict[str, Any]:
        rainfall = self.tip_count * self.bucket_size
        self.tip_count = 0
        
        data = {
            "rainfall": rainfall,
            "unit": self.config.measurement_unit
        }
        
        alerts = self.check_thresholds({"rainfall": rainfall})
        data["alerts"] = alerts
        
        return data
        
    async def calibrate(self) -> bool:
        self.tip_count = 0
        return True
        
    async def shutdown(self) -> bool:
        try:
            if self.gpio_pin is not None:
                GPIO.remove_event_detect(self.gpio_pin)
            GPIO.cleanup()
            self.is_active = False
            return True
        except:
            return False