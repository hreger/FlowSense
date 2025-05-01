import asyncio
import json
from awscli.clidriver import create_clidriver
from awsiotsdk.mqtt5_client_builder import Mqtt5Client
from typing import Dict, Any

class IoTCore:
    def __init__(self, endpoint: str, cert_path: str, key_path: str):
        self.endpoint = endpoint
        self.cert_path = cert_path
        self.key_path = key_path
        self.client = None
        
    async def connect(self):
        try:
            self.client = Mqtt5Client.builder()\
                .with_endpoint(self.endpoint)\
                .with_cert_path(self.cert_path)\
                .with_key_path(self.key_path)\
                .build()
            
            await self.client.connect()
            return True
        except Exception as e:
            print(f"Failed to connect to AWS IoT Core: {e}")
            return False
            
    async def publish_data(self, topic: str, data: Dict[str, Any]):
        if self.client and self.client.is_connected():
            message = json.dumps(data)
            await self.client.publish(
                topic=topic,
                payload=message,
                qos=1
            )
            
    async def disconnect(self):
        if self.client:
            await self.client.disconnect()