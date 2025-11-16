# Quick Start Guide: RSU-Based V2I System

## Step-by-Step Instructions

### Step 1: Install Required Dependencies

Open PowerShell in your project directory and run:

```powershell
# Install Python packages
pip install fastapi uvicorn pydantic requests sqlite3

# If you don't have SUMO TraCI, install it
pip install traci

# Optional: For visualization
pip install matplotlib numpy
```

---

### Step 2: Start the FastAPI Server

**Open Terminal 1 (PowerShell):**

```powershell
# Navigate to your project directory
cd "C:\Users\mushf\OneDrive\Desktop\Route Optimization of EV"

# Start the server
uvicorn server:app --reload --host 127.0.0.1 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Keep this terminal running!** The server is now listening for data.

---

### Step 3: Run the RSU-Based Simulation

**Open Terminal 2 (PowerShell):**

```powershell
# Navigate to your project directory
cd "C:\Users\mushf\OneDrive\Desktop\Route Optimization of EV"

# Run the RSU-based TraCI script
python traCI_rsu.py
```

**What Happens:**
1. ✅ RSU network is set up (7 RSUs at intersections)
2. ✅ Old data is cleared from the server
3. ✅ SUMO GUI opens with the simulation
4. ✅ Vehicles start moving
5. ✅ Every 10 seconds, vehicle data is collected
6. ✅ Data is routed through nearby RSUs
7. ✅ RSUs send data to the server in batches

**Expected Console Output:**
```
============================================================
RSU-BASED VEHICLE-TO-INFRASTRUCTURE COMMUNICATION SYSTEM
============================================================

Setting up RSU Network...
[RSU Network] Added RSU-RSU_Chachra at position (-165.47, -199.59) with 500.0m range
[RSU Network] Added RSU-RSU_Dhormotola at position (-194.59, 27.16) with 500.0m range
...
RSU Network setup complete with 7 RSUs

Data cleared successfully before the run.

SUMO simulation started

Starting simulation loop...

[Sim Time: 10.0s] Collecting data from 15 vehicles...
[RSU-RSU_Doratana] Successfully sent 12 records to server
[RSU-RSU_NewMarket] Successfully sent 8 records to server
...
```

---

### Step 4: Monitor the Simulation

While the simulation is running, you can:

**4a. Watch SUMO GUI:**
- See vehicles moving on the road network
- Observe traffic at intersections where RSUs are placed

**4b. Monitor Server Logs (Terminal 1):**
```
INFO:     127.0.0.1:xxxxx - "POST /ingest_rsu HTTP/1.1" 200 OK
INFO:     127.0.0.1:xxxxx - "POST /ingest_rsu HTTP/1.1" 200 OK
```

**4c. Check RSU Network Status (Terminal 2):**
Every 100 simulation steps, you'll see:
```
============================================================
RSU NETWORK STATUS
============================================================
RSU-RSU_Chachra:
  Position: (-165.47, -199.59)
  Coverage: 500.0m
  Connected Vehicles: 5
  Buffered Records: 23
...
```

---

### Step 5: Access Data While Running

**Option 1: Check RSU Statistics (Browser/curl)**

Open browser: http://127.0.0.1:8000/rsu_stats

Or in PowerShell:
```powershell
curl http://127.0.0.1:8000/rsu_stats
```

**Response:**
```json
{
  "rsu_stats": [
    {
      "rsu_id": "RSU_Chachra",
      "position": [-165.47, -199.59],
      "total_vehicles": 45,
      "total_records": 523,
      "last_update": "2025-11-13T10:30:45Z"
    },
    ...
  ]
}
```

**Option 2: Check API Documentation**

Open browser: http://127.0.0.1:8000/docs

This opens FastAPI's interactive API documentation where you can:
- See all endpoints
- Test API calls directly
- View request/response schemas

---

### Step 6: Extract Data from Database

After the simulation completes, extract data from the SQLite database:

**Method 1: Using Python Script**

Create `extract_data.py`:
```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('telemetry.db')

# Extract RSU-based vehicle logs
df_rsu_logs = pd.read_sql_query("""
    SELECT * FROM rsu_vehicle_logs
    ORDER BY sim_time
""", conn)

# Extract RSU status
df_rsu_status = pd.read_sql_query("""
    SELECT * FROM rsu_status
    ORDER BY ts_utc
""", conn)

# Save to Excel
df_rsu_logs.to_excel('rsu_vehicle_data.xlsx', index=False)
df_rsu_status.to_excel('rsu_status.xlsx', index=False)

# Print summary
print(f"Total records collected: {len(df_rsu_logs)}")
print(f"\nRecords per RSU:")
print(df_rsu_logs.groupby('rsu_id').size())

conn.close()
print("\nData exported to Excel files!")
```

Run it:
```powershell
python extract_data.py
```

**Method 2: Using SQLite Browser**

1. Download [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Open `telemetry.db`
3. Browse tables:
   - `rsu_vehicle_logs` - All vehicle data
   - `rsu_status` - RSU statistics
   - `vehicle_logs` - Legacy data (if any)

**Method 3: Direct SQL Queries**

```powershell
# Open SQLite in PowerShell
sqlite3 telemetry.db

# Run queries
SELECT COUNT(*) FROM rsu_vehicle_logs;
SELECT rsu_id, COUNT(*) as records FROM rsu_vehicle_logs GROUP BY rsu_id;
SELECT * FROM rsu_vehicle_logs LIMIT 10;
```

---

### Step 7: Analyze the Data

**Create Analysis Script (`analyze_data.py`):**

```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('telemetry.db')

# Query 1: Vehicle data by RSU
df = pd.read_sql_query("""
    SELECT 
        rsu_id,
        vehicle_id,
        AVG(speed) as avg_speed,
        AVG(battery_charge) as avg_battery,
        COUNT(*) as records
    FROM rsu_vehicle_logs
    GROUP BY rsu_id, vehicle_id
""", conn)

print("=== Vehicle Statistics by RSU ===")
print(df)

# Query 2: RSU Performance
rsu_perf = pd.read_sql_query("""
    SELECT 
        rsu_id,
        SUM(vehicle_count) as total_vehicles,
        SUM(data_records) as total_records
    FROM rsu_status
    GROUP BY rsu_id
""", conn)

print("\n=== RSU Performance ===")
print(rsu_perf)

# Visualization: Records per RSU
plt.figure(figsize=(10, 6))
rsu_perf.plot(x='rsu_id', y='total_records', kind='bar')
plt.title('Total Records Collected per RSU')
plt.xlabel('RSU ID')
plt.ylabel('Number of Records')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('rsu_performance.png')
print("\nChart saved to rsu_performance.png")

# Query 3: Battery Analysis
battery_df = pd.read_sql_query("""
    SELECT 
        vehicle_id,
        MIN(battery_charge) as min_battery,
        MAX(battery_charge) as max_battery,
        AVG(battery_charge) as avg_battery
    FROM rsu_vehicle_logs
    GROUP BY vehicle_id
""", conn)

print("\n=== Battery Statistics ===")
print(battery_df.describe())

conn.close()
```

Run it:
```powershell
python analyze_data.py
```

---

### Step 8: Visualize RSU Coverage

```powershell
python visualize_rsu.py
```

This generates:
- Console output with coverage statistics
- `rsu_coverage_map.png` showing RSU positions and coverage areas

---

## Common Use Cases

### Use Case 1: Export All Data to CSV

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('telemetry.db')

# Export all RSU vehicle logs
df = pd.read_sql_query("SELECT * FROM rsu_vehicle_logs", conn)
df.to_csv('all_vehicle_data.csv', index=False)

print(f"Exported {len(df)} records to all_vehicle_data.csv")
conn.close()
```

### Use Case 2: Get Data for Specific RSU

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('telemetry.db')

# Get data from specific RSU
rsu_id = 'RSU_Doratana'
df = pd.read_sql_query(f"""
    SELECT * FROM rsu_vehicle_logs 
    WHERE rsu_id = '{rsu_id}'
    ORDER BY sim_time
""", conn)

df.to_excel(f'{rsu_id}_data.xlsx', index=False)
print(f"Exported {len(df)} records from {rsu_id}")
conn.close()
```

### Use Case 3: Get Data for Specific Vehicle

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('telemetry.db')

# Get trajectory of specific vehicle
vehicle_id = 'vehicle_0'
df = pd.read_sql_query(f"""
    SELECT 
        sim_time,
        rsu_id,
        speed,
        battery_charge,
        rsu_position_x,
        rsu_position_y
    FROM rsu_vehicle_logs 
    WHERE vehicle_id = '{vehicle_id}'
    ORDER BY sim_time
""", conn)

print(f"Vehicle {vehicle_id} Trajectory:")
print(df)

# Plot battery over time
import matplotlib.pyplot as plt
plt.plot(df['sim_time'], df['battery_charge'])
plt.xlabel('Simulation Time (s)')
plt.ylabel('Battery Charge')
plt.title(f'Battery Discharge - {vehicle_id}')
plt.savefig(f'{vehicle_id}_battery.png')

conn.close()
```

---

## Troubleshooting

### Problem 1: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```powershell
pip install fastapi uvicorn pydantic
```

### Problem 2: "Connection refused" when running traCI_rsu.py

**Solution:**
- Make sure the server is running in Terminal 1
- Check if port 8000 is available
- Verify the URL in `traCI_rsu.py` is `http://127.0.0.1:8000`

### Problem 3: "No vehicles in RSU range"

**Solution:**
- Increase RSU_COVERAGE_RADIUS in `traCI_rsu.py`:
```python
RSU_COVERAGE_RADIUS = 1000.0  # Increase from 500m to 1000m
```

### Problem 4: SUMO not starting

**Solution:**
- Check if SUMO is installed: `sumo-gui --version`
- Verify `CustomRoadNetwork.sumocfg` exists
- Make sure you're in the correct directory

### Problem 5: Database locked

**Solution:**
```powershell
# Close any SQLite browser
# Stop the server (Ctrl+C in Terminal 1)
# Delete the database and restart
rm telemetry.db
```

---

## Data Schema Reference

### rsu_vehicle_logs Table

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INTEGER | Auto-increment ID | 1, 2, 3... |
| ts_utc | TEXT | Server reception time | "2025-11-13T10:30:45Z" |
| rsu_id | TEXT | RSU identifier | "RSU_Doratana" |
| rsu_position_x | REAL | RSU X coordinate | -44.04 |
| rsu_position_y | REAL | RSU Y coordinate | 49.98 |
| vehicle_id | TEXT | Vehicle identifier | "vehicle_0" |
| speed | REAL | Speed in m/s | 13.89 |
| battery_charge | REAL | Battery level | 85.5 |
| battery_capacity | TEXT | Max capacity | "100.0" |
| sim_time | REAL | Simulation time | 120.0 |
| collection_timestamp | TEXT | RSU collection time | "2025-11-13T10:30:43Z" |
| rsu_received_at | TEXT | Server log time | "2025-11-13T10:30:45Z" |

---

## Next Steps

1. ✅ Run the simulation
2. ✅ Collect data
3. ✅ Export to Excel/CSV
4. ✅ Analyze with Python/Pandas
5. ✅ Create visualizations
6. ✅ Use data for optimization algorithms

**You're all set!** Start with Step 1 and follow the guide sequentially.
