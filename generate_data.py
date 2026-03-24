import psycopg2
import random
import math
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "energyops_db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "host": os.getenv("POSTGRES_SERVER", "127.0.0.1"),
    "port": os.getenv("POSTGRES_PORT", "5432")
}

PLANTS = ["SolarFarm_01", "WindPark_02", "HybridPlant_03"]
DAYS = 30
INTERVAL_MINUTES = 60

def generate_solar_output(hour):
    """Simple solar model: Peak at noon, zero at night."""
    if 6 <= hour <= 19:
        # Normalized hours for sine wave (0 to pi)
        x = (hour - 6) / (19 - 6) * math.pi
        base = math.sin(x)
        # Add random cloud cover effect
        cloud_cover = random.uniform(0.8, 1.2)
        return max(0, base * 50 * cloud_cover)
    return 0.0

def generate_wind_output(hour, prev_wind):
    """Simple wind model: Random walk with tendency to stay within bounds."""
    change = random.uniform(-5, 5)
    new_wind = prev_wind + change
    # Clamp between 0 and 100
    new_wind = max(0, min(100, new_wind))
    return new_wind

def generate_grid_load(hour):
    """Dual peak load curve."""
    # Morning peak around 9, Evening peak around 19
    morning_peak = 80 * math.exp(-((hour - 9)**2) / 8)
    evening_peak = 100 * math.exp(-((hour - 19)**2) / 8)
    base_load = 40
    noise = random.uniform(-5, 5)
    return base_load + morning_peak + evening_peak + noise

def generate_data():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"Connected to {DB_CONFIG['dbname']}. Generating data...")
        
        start_date = datetime.now() - timedelta(days=DAYS)
        total_records = 0
        
        for plant in PLANTS:
            current_time = start_date
            prev_wind = random.uniform(10, 30)
            
            records = []
            for _ in range(DAYS * 24 * (60 // INTERVAL_MINUTES)):
                hour = current_time.hour
                
                solar = generate_solar_output(hour)
                # Modify solar for wind-only plant
                if "Wind" in plant:
                    solar = 0
                
                wind = generate_wind_output(hour, prev_wind)
                prev_wind = wind
                # Modify wind for solar-only plant
                if "Solar" in plant:
                    wind = 0
                
                grid_load = generate_grid_load(hour)
                
                # Simple battery logic: Charge when generation > load, Discharge when load > generation
                total_gen = solar + wind
                battery_level = 50 + (total_gen - grid_load) * 0.1
                battery_level = max(0, min(100, battery_level))
                
                # Anomaly flag: 1% chance
                anomaly = random.random() < 0.01
                if anomaly:
                    # Create an anomaly in the data
                    if random.choice([True, False]):
                        solar *= 0.1 # Drop in solar
                    else:
                        grid_load *= 2 # Spike in load
                
                records.append((
                    plant,
                    current_time,
                    round(solar, 2),
                    round(wind, 2),
                    round(battery_level, 2),
                    round(grid_load, 2),
                    anomaly
                ))
                
                current_time += timedelta(minutes=INTERVAL_MINUTES)
            
            # Batch insert
            args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s)", x).decode('utf-8') for x in records)
            cursor.execute("INSERT INTO energy_production (plant_id, timestamp, solar_output, wind_output, battery_level, grid_load, anomaly_flag) VALUES " + args_str)
            total_records += len(records)
            print(f"Inserted {len(records)} records for {plant}")

        conn.commit()
        print(f"Successfully inserted {total_records} total records.")
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()

if __name__ == "__main__":
    generate_data()
