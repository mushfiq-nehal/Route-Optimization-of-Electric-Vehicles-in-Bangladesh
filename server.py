from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3
from datetime import datetime

app = FastAPI(title="SUMO/TraCI Ingest")

DB_PATH = "telemetry.db"

# Initialize the database with vehicle_logs table if it doesn't exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_utc TEXT NOT NULL,
            vehicle_id TEXT NOT NULL,
            speed REAL NOT NULL,
            battery_charge REAL NOT NULL,
            battery_capacity TEXT,
            sim_time REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Pydantic model for vehicle log
class VehicleLog(BaseModel):
    vehicle_id: str
    speed: float
    battery_charge: float
    battery_capacity: str | None = None
    sim_time: float

# Endpoint to ingest vehicle logs
@app.post("/ingest")
def ingest(logs: List[VehicleLog]):
    if not logs:
        raise HTTPException(status_code=400, detail="Empty payload")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO vehicle_logs (ts_utc, vehicle_id, speed, battery_charge, battery_capacity, sim_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (datetime.utcnow().isoformat(timespec="seconds")+"Z",
         l.vehicle_id, l.speed, l.battery_charge, l.battery_capacity, l.sim_time)
        for l in logs
    ])
    conn.commit()
    conn.close()
    return {"status": "ok", "inserted": len(logs)}

# Endpoint to clear the vehicle_logs table
@app.delete("/clear_data")
def clear_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM vehicle_logs")  # Clears all data in the table
    conn.commit()
    conn.close()
    return {"status": "Data cleared"}
