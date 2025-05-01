import asyncpg
from typing import Dict, Any
from datetime import datetime

class TimeScaleDB:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None
        
    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn)
        
        async with self.pool.acquire() as conn:
            # Create hypertable for sensor data
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS sensor_data (
                    time TIMESTAMPTZ NOT NULL,
                    sensor_id TEXT NOT NULL,
                    sensor_type TEXT NOT NULL,
                    value DOUBLE PRECISION,
                    unit TEXT,
                    metadata JSONB,
                    PRIMARY KEY (time, sensor_id)
                );
                
                SELECT create_hypertable('sensor_data', 'time', if_not_exists => TRUE);
            ''')
            
    async def store_data(self, data: Dict[str, Any]):
        async with self.pool.acquire() as conn:
            timestamp = datetime.now()
            for sensor_id, sensor_data in data.items():
                await conn.execute('''
                    INSERT INTO sensor_data (time, sensor_id, sensor_type, value, unit, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                ''', timestamp, sensor_id, sensor_data['type'], 
                    sensor_data.get('value'), sensor_data.get('unit'),
                    sensor_data)