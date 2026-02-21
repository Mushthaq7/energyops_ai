from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api import deps
from app.models.energy import EnergyProduction
from app.schemas.energy import EnergyProduction as EnergyProductionSchema
from app.schemas.energy import EnergySummary

router = APIRouter()

@router.get("/latest", response_model=List[EnergyProductionSchema])
def get_latest_energy_data(
    db: Session = Depends(deps.get_db),
    limit: int = 10,
    plant_id: Optional[str] = None
):
    query = db.query(EnergyProduction).order_by(EnergyProduction.timestamp.desc())
    if plant_id:
        query = query.filter(EnergyProduction.plant_id == plant_id)
    return query.limit(limit).all()

@router.get("/anomalies", response_model=List[EnergyProductionSchema])
def get_anomalies(
    db: Session = Depends(deps.get_db),
    limit: int = 20
):
    """
    Get recent anomalies (where anomaly_flag is True).
    """
    return (
        db.query(EnergyProduction)
        .filter(EnergyProduction.anomaly_flag == True)
        .order_by(EnergyProduction.timestamp.desc())
        .limit(limit)
        .all()
    )

@router.get("/summary", response_model=List[EnergySummary])
def get_energy_summary(
    plant_id: Optional[str] = Query(None, description="The ID of the plant to summarize"),
    db: Session = Depends(deps.get_db)
):
    """
    Aggregates data per plant. Returns a list of summaries.
    """
    query = db.query(
        EnergyProduction.plant_id,
        func.sum(EnergyProduction.solar_output).label("total_solar"),
        func.sum(EnergyProduction.wind_output).label("total_wind"),
        func.avg(EnergyProduction.grid_load).label("avg_grid_load"),
        func.max(EnergyProduction.battery_level).label("max_battery_level")
    )
    
    if plant_id:
        query = query.filter(EnergyProduction.plant_id == plant_id)
        
    results = query.group_by(EnergyProduction.plant_id).all()
    
    if not results and plant_id:
         raise HTTPException(status_code=404, detail=f"No data found for plant_id {plant_id}")

    output = []
    for r in results:
        # Mocking efficiency for the dashboard demo
        # Imagine efficiency = (Actual Power / Theoretical Max) * 100
        # For this demo, let's use a base + variance
        mock_efficiency = round(85.0 + (5.0 if "Solar" in r.plant_id else 8.0) * (index % 1.5 if 'index' in locals() else 0.5), 1)
        # Actually let's just use a more stable random based on plant_id
        stable_seed = sum(ord(c) for c in r.plant_id) % 10
        mock_efficiency = 88.5 + (stable_seed % 5)

        output.append({
            "plant_id": r.plant_id,
            "total_solar": round(r.total_solar or 0.0, 2),
            "total_wind": round(r.total_wind or 0.0, 2),
            "avg_grid_load": round(r.avg_grid_load or 0.0, 2),
            "max_battery_level": round(r.max_battery_level or 0.0, 2),
            "efficiency": mock_efficiency
        })
        
    return output
