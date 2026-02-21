from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class EnergyProductionBase(BaseModel):
    plant_id: str
    timestamp: datetime
    solar_output: float
    wind_output: float
    battery_level: float
    grid_load: float
    anomaly_flag: bool

class EnergyProductionCreate(EnergyProductionBase):
    pass

class EnergyProduction(EnergyProductionBase):
    id: int

    class Config:
        from_attributes = True

class EnergySummary(BaseModel):
    plant_id: str
    total_solar: float
    total_wind: float
    avg_grid_load: float
    max_battery_level: float
    efficiency: float
