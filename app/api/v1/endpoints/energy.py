from typing import List, Optional
from datetime import datetime, timedelta
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

@router.get("/trends")
def get_production_trends(db: Session = Depends(deps.get_db)):
    """
    Compare total renewable output for the last 7 days vs the 7 days before that.
    Returns percentage change for production and efficiency.
    """
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    def _agg(start, end):
        return db.query(
            func.sum(EnergyProduction.solar_output + EnergyProduction.wind_output).label("total_output"),
            func.avg(EnergyProduction.grid_load).label("avg_load"),
            func.count(EnergyProduction.id).label("cnt"),
        ).filter(
            EnergyProduction.timestamp >= start,
            EnergyProduction.timestamp < end,
        ).one()

    current = _agg(week_ago, now)
    previous = _agg(two_weeks_ago, week_ago)

    def _pct_change(curr, prev):
        if prev and prev > 0:
            return round(((curr - prev) / prev) * 100, 1)
        return 0.0

    curr_output = current.total_output or 0.0
    prev_output = previous.total_output or 0.0
    curr_efficiency = (curr_output / (current.avg_load * current.cnt) * 100) if (current.avg_load and current.cnt) else 0.0
    prev_efficiency = (prev_output / (previous.avg_load * previous.cnt) * 100) if (previous.avg_load and previous.cnt) else 0.0

    return {
        "production_change_pct": _pct_change(curr_output, prev_output),
        "efficiency_change_pct": _pct_change(curr_efficiency, prev_efficiency),
    }


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
        func.max(EnergyProduction.battery_level).label("max_battery_level"),
        func.count(EnergyProduction.id).label("record_count")
    )

    if plant_id:
        query = query.filter(EnergyProduction.plant_id == plant_id)

    results = query.group_by(EnergyProduction.plant_id).all()

    if not results and plant_id:
         raise HTTPException(status_code=404, detail=f"No data found for plant_id {plant_id}")

    output = []
    for r in results:
        total_solar = r.total_solar or 0.0
        total_wind = r.total_wind or 0.0
        avg_grid_load = r.avg_grid_load or 0.0
        record_count = r.record_count or 1
        # Renewable energy coverage: how much of total grid demand was met by renewables
        total_generation = total_solar + total_wind
        total_grid_demand = avg_grid_load * record_count
        efficiency = min(round((total_generation / total_grid_demand) * 100, 1), 100.0) if total_grid_demand > 0 else 0.0

        output.append({
            "plant_id": r.plant_id,
            "total_solar": round(total_solar, 2),
            "total_wind": round(total_wind, 2),
            "avg_grid_load": round(avg_grid_load, 2),
            "max_battery_level": round(r.max_battery_level or 0.0, 2),
            "efficiency": efficiency
        })
        
    return output
