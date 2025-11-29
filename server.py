from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
from datetime import datetime

app = FastAPI(title="SUMO/TraCI RSU-Based Ingest")

DB_PATH = "telemetry.db"

# Initialize the database with vehicle_logs and rsu_logs tables if they don't exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Original vehicle_logs table (for backward compatibility)
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
    
    # New RSU-based vehicle logs table with traffic density fields
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rsu_vehicle_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_utc TEXT NOT NULL,
            rsu_id TEXT NOT NULL,
            rsu_position_x REAL,
            rsu_position_y REAL,
            vehicle_id TEXT NOT NULL,
            vehicle_type TEXT,
            edge_id TEXT,
            lane_id TEXT,
            lane_position REAL,
            speed REAL NOT NULL,
            battery_charge REAL NOT NULL,
            battery_capacity REAL,
            battery_percentage REAL,
            vehicles_ahead_count INTEGER,
            same_direction_ahead INTEGER,
            distance_to_traffic_light REAL,
            next_traffic_light TEXT,
            traffic_light_state TEXT,
            edge_occupancy_percentage REAL,
            sim_time REAL NOT NULL,
            collection_timestamp TEXT,
            rsu_received_at TEXT NOT NULL
        )
    """)
    
    # RSU status logs table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rsu_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_utc TEXT NOT NULL,
            rsu_id TEXT NOT NULL,
            position_x REAL,
            position_y REAL,
            vehicle_count INTEGER,
            data_records INTEGER
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# Pydantic model for vehicle log (backward compatibility)
class VehicleLog(BaseModel):
    vehicle_id: str
    speed: float
    battery_charge: float
    battery_capacity: Optional[str] = None
    sim_time: float

# Pydantic model for RSU data ingestion
class RSUVehicleData(BaseModel):
    vehicle_id: str
    speed: float
    battery_charge: float
    battery_capacity: Optional[str] = None
    sim_time: float
    rsu_id: str
    rsu_position: tuple
    collection_timestamp: str

class RSUIngestPayload(BaseModel):
    rsu_id: str
    rsu_position: tuple
    vehicle_data: List[Dict[str, Any]]
    timestamp: str

# Endpoint to ingest vehicle logs (original - for backward compatibility)
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

# Endpoint to ingest data from RSUs
@app.post("/ingest_rsu")
def ingest_rsu(payload: RSUIngestPayload):
    if not payload.vehicle_data:
        raise HTTPException(status_code=400, detail="Empty vehicle data")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    rsu_received_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    
    # Insert vehicle data received from RSU with traffic density fields
    records = []
    for data in payload.vehicle_data:
        records.append((
            rsu_received_at,
            payload.rsu_id,
            payload.rsu_position[0],
            payload.rsu_position[1],
            data.get('vehicle_id'),
            data.get('vehicle_type'),
            data.get('edge_id'),
            data.get('lane_id'),
            data.get('lane_position'),
            data.get('speed'),
            data.get('battery_charge'),
            data.get('battery_capacity'),
            data.get('battery_percentage'),
            data.get('vehicles_ahead_count'),
            data.get('same_direction_ahead'),
            data.get('distance_to_traffic_light'),
            data.get('next_traffic_light'),
            data.get('traffic_light_state'),
            data.get('edge_occupancy_percentage'),
            data.get('sim_time'),
            data.get('collection_timestamp'),
            rsu_received_at
        ))
    
    cur.executemany("""
        INSERT INTO rsu_vehicle_logs 
        (ts_utc, rsu_id, rsu_position_x, rsu_position_y, vehicle_id, vehicle_type, 
         edge_id, lane_id, lane_position, speed, battery_charge, battery_capacity, 
         battery_percentage, vehicles_ahead_count, same_direction_ahead, 
         distance_to_traffic_light, next_traffic_light, traffic_light_state, 
         edge_occupancy_percentage, sim_time, collection_timestamp, rsu_received_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)
    
    # Log RSU status
    cur.execute("""
        INSERT INTO rsu_status (ts_utc, rsu_id, position_x, position_y, vehicle_count, data_records)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        rsu_received_at,
        payload.rsu_id,
        payload.rsu_position[0],
        payload.rsu_position[1],
        len(set(data.get('vehicle_id') for data in payload.vehicle_data)),
        len(payload.vehicle_data)
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "ok",
        "rsu_id": payload.rsu_id,
        "inserted": len(payload.vehicle_data),
        "timestamp": rsu_received_at
    }

# Endpoint to get RSU statistics
@app.get("/rsu_stats")
def get_rsu_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Get latest status for each RSU
    cur.execute("""
        SELECT rsu_id, position_x, position_y, 
               SUM(vehicle_count) as total_vehicles, 
               SUM(data_records) as total_records,
               MAX(ts_utc) as last_update
        FROM rsu_status
        GROUP BY rsu_id
    """)
    
    stats = []
    for row in cur.fetchall():
        stats.append({
            "rsu_id": row[0],
            "position": (row[1], row[2]),
            "total_vehicles": row[3],
            "total_records": row[4],
            "last_update": row[5]
        })
    
    conn.close()
    return {"rsu_stats": stats}

# Endpoint to clear the vehicle_logs table
@app.delete("/clear_data")
def clear_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM vehicle_logs")  # Clears all data in the table
    cur.execute("DELETE FROM rsu_vehicle_logs")  # Clear RSU-based logs
    cur.execute("DELETE FROM rsu_status")  # Clear RSU status
    conn.commit()
    conn.close()
    return {"status": "All data cleared"}

if __name__ == "__main__":
    import uvicorn
    init_db()  # Initialize database on startup
    print("Starting FastAPI server on http://127.0.0.1:8000")
    print("RSU data ingestion endpoints:")
    print("  POST /ingest_rsu - Receive vehicle data from RSUs")
    print("  GET /rsu_stats - Get RSU statistics")
    print("  DELETE /clear_data - Clear all data")
    uvicorn.run(app, host="127.0.0.1", port=8000)
