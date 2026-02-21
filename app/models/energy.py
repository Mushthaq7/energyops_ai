from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.models.base import Base

class EnergyProduction(Base):
    __tablename__ = "energy_production"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(String(50), index=True)
    timestamp = Column(DateTime) # In DB it's timestamp without time zone
    solar_output = Column(Float)
    wind_output = Column(Float)
    battery_level = Column(Float)
    grid_load = Column(Float)
    anomaly_flag = Column(Boolean, default=False)
