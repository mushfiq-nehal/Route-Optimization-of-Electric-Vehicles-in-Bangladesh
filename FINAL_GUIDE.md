# RSU-Based Vehicle Data Collection - Complete Guide

## Overview
This system collects electric vehicle data through Roadside Units (RSUs) instead of direct TraCI queries. The data flow is:

**Vehicle → RSU → Server → Database → Excel/CSV**

## System Architecture

```
🚗 Electric Vehicles (31 EVs)
    ↓ V2I Communication (500m range)
📡 RSUs (7 roadside units)
    ↓ HTTP POST requests
🖥️  FastAPI Server (Port 8000)
    ↓ SQLite storage
💾 Database (telemetry.db)
    ↓ Data extraction
📊 Excel & CSV Files
```

## Quick Start (3 Simple Steps)

### Step 1: Start the Server

Open a terminal and run:
```powershell
python server.py
```

You should see:
```
Starting FastAPI server on http://127.0.0.1:8000
RSU data ingestion endpoints:
  POST /ingest_rsu - Receive vehicle data from RSUs
  GET /rsu_stats - Get RSU statistics
  DELETE /clear_data - Clear all data
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal open** - the server must stay running.

### Step 2: Run the Simulation

Open a **new terminal** and choose one option:

**Option A: Quick Test (Recommended First Run)**
```powershell
python quick_test.py
```
- Runs 100 simulation steps (~30 seconds)
- No GUI window
- Perfect for testing the system

**Option B: Extended Test (See Battery Discharge)**
```powershell
python test_battery_discharge.py
```
- Runs 500 simulation steps (~2 minutes)
- Shows detailed battery discharge analysis
- Displays discharge statistics

**Option C: Full Simulation (Watch Vehicles Move)**
```powershell
python traCI_rsu.py
```
- Opens SUMO GUI window
- Watch 31 vehicles in real-time
- Runs until all vehicles complete routes

### Step 3: Extract the Data

After simulation completes, run:
```powershell
python extract_data.py
```

This creates:
- `rsu_telemetry_data_YYYYMMDD_HHMMSS.xlsx` - Excel file with all data
- `rsu_vehicle_logs_YYYYMMDD_HHMMSS.csv` - Vehicle tracking CSV
- `rsu_status_YYYYMMDD_HHMMSS.csv` - RSU status CSV

---

## What Data Is Collected?

### Vehicle Data Fields
| Field | Description | Example |
|-------|-------------|---------|
| vehicle_id | Unique vehicle identifier | t_10_Easybike_ER-02B |
| speed | Current speed (m/s) | 8.45 |
| battery_charge | Current battery charge (Wh) | 1224.10 |
| battery_capacity | Total battery capacity (Wh) | 3000 |
| **battery_percentage** | **Battery % remaining** | **40.80%** |
| sim_time | Simulation time (seconds) | 211.0 |
| rsu_id | Which RSU collected data | RSU_Doratana |
| rsu_position_x, y | RSU coordinates | (-44.04, 49.98) |

### RSU Network Configuration

| RSU ID | Location | Coverage | Typical Records |
|--------|----------|----------|-----------------|
| RSU_Palbari | (-218.70, 214.90) | 500m | ~185 |
| RSU_Doratana | (-44.04, 49.98) | 500m | ~225 |
| RSU_Dhormotola | (-194.59, 27.16) | 500m | ~206 |
| RSU_Chachra | (-165.47, -199.59) | 500m | ~159 |
| RSU_NewMarket | (2.93, 170.72) | 500m | ~150 |
| RSU_Muroli | (223.72, -213.15) | 500m | Low traffic |
| RSU_Monihar | (79.98, -8.38) | 500m | ~34 |

### Vehicle Types & Realistic Battery Specs

| Vehicle Type | Battery Capacity | Starting Charge | Expected Discharge |
|--------------|------------------|-----------------|-------------------|
| Easybike_ER-02B | 3000 Wh (3 kWh) | 50% (1500 Wh) | 9-12% per route |
| Electric_Rickshaw_V8 | 2500 Wh (2.5 kWh) | 50% (1250 Wh) | 7-10% per route |
| Small_Easybike_V12 | 2000 Wh (2 kWh) | 50% (1000 Wh) | 9-12% per route |
| Default_EV | 35000 Wh (35 kWh) | 50% (17500 Wh) | 2-5% per route |

**Note:** Batteries start at 50% to ensure measurable discharge during simulation.

---

## Expected Results

### Typical Simulation Output

**Quick Test (100 steps):**
```
✓ RSU Network ready with 7 RSUs
✓ Cleared old data from server

Step 0: 5 vehicles active
Step 50: 31 vehicles active
Step 100: 31 vehicles active

[RSU-RSU_Doratana] Successfully sent 50 records to server
[RSU-RSU_Palbari] Successfully sent 50 records to server

Total unique vehicles seen: 31
Total data points collected: 259
Server received data from 5 RSUs
```

**Extended Test (500 steps) - Battery Discharge:**
```
t_10_Easybike_ER-02B:
  Capacity: 3000 Wh
  Start: 1500.00 Wh (50.00%) at 1s
  End:   1224.10 Wh (40.80%) at 211s
  Discharged: 275.90 Wh (9.20%)
```

**Data Extraction:**
```
Total RSU Vehicle Records: 959
Unique Vehicles Tracked: 31
Simulation Duration: 480.00s

Battery Statistics:
  Minimum Battery %: 37.80%
  Maximum Battery %: 50.00%
  Average Battery %: 45.70%
```

---

## Data Flow Details

### 1. Vehicle Data Collection (Every 10 seconds)
```python
# TraCI queries vehicle state
position = traci.vehicle.getPosition(vehicle_id)
speed = traci.vehicle.getSpeed(vehicle_id)
battery_charge = traci.vehicle.getParameter(vehicle_id, "device.battery.actualBatteryCapacity")
battery_capacity = traci.vehicle.getParameter(vehicle_id, "device.battery.capacity")

# Calculate battery percentage
battery_percentage = (battery_charge / battery_capacity) × 100
```

### 2. RSU Routing
```python
# Find nearest RSU within 500m range
for each RSU:
    distance = sqrt((veh_x - rsu_x)² + (veh_y - rsu_y)²)
    
if distance < 500m:
    route_to_nearest_RSU(vehicle_data)
```

### 3. Data Transmission (Batches of 100)
```python
# RSU batches data and sends to server
POST http://127.0.0.1:8000/ingest_rsu
{
    "rsu_id": "RSU_Doratana",
    "rsu_position": [-44.04, 49.98],
    "vehicle_data": [
        {
            "vehicle_id": "t_10_Easybike_ER-02B",
            "speed": 8.45,
            "battery_charge": 1224.10,
            "battery_capacity": 3000,
            "battery_percentage": 40.80,
            "sim_time": 211.0
        }
    ]
}
```

### 4. Database Storage
```sql
-- Server stores in rsu_vehicle_logs table
INSERT INTO rsu_vehicle_logs (
    ts_utc, rsu_id, rsu_position_x, rsu_position_y,
    vehicle_id, speed, battery_charge, battery_capacity,
    battery_percentage, sim_time, collection_timestamp, rsu_received_at
) VALUES (...)
```

---

## Additional Tools

### View Battery Statistics
```powershell
python verify_battery.py
```
Shows sample data and battery info by vehicle type.

### Generate Visualizations
```powershell
python analyze_data.py
```
Creates charts:
- RSU activity distribution
- Battery discharge over time
- Vehicle trajectories
- Temporal analysis

### Visualize RSU Network
```powershell
python visualize_rsu.py
```
Creates a map showing RSU locations and coverage areas.

---

## Automated Execution

Use the batch file for fully automated run:
```powershell
run_complete_test.bat
```

This automatically:
1. Starts server in new window
2. Waits 3 seconds
3. Runs simulation
4. Extracts data to Excel/CSV

---

## Troubleshooting

### ❌ Server won't start
```powershell
# Kill existing Python processes and restart
Stop-Process -Name python -Force
python server.py
```

### ❌ No vehicles in simulation
- Check `CustomRoadNetwork.rou.xml` has 31 vehicle definitions
- All vehicles depart at time 0.00
- Use SUMO GUI to visually confirm vehicles appear

### ❌ Database is empty
**Correct order:**
1. Start server FIRST
2. Run simulation SECOND
3. Wait for completion
4. Extract data LAST

### ❌ Port 8000 already in use
```powershell
Stop-Process -Name python -Force
Start-Sleep -Seconds 2
python server.py
```

### ❌ Battery not discharging
- System now uses `Energy/unknown` emission class
- Batteries discharge from 50% to 38-48%
- If still at 50%, check vehicle type has `emissionClass="Energy/unknown"`

---

## Configuration Options

### Change Data Collection Frequency
In `traCI_rsu.py` or `quick_test.py`:
```python
collection_interval = 10  # Change to 5, 15, 20, etc. (seconds)
```

### Change RSU Coverage Range
In `traCI_rsu.py`:
```python
RSU_COVERAGE_RADIUS = 500.0  # Change to 300, 1000, etc. (meters)
```

### Change Batch Size
In `rsu.py` - `send_data_to_server()` method:
```python
def send_data_to_server(self, batch_size=100):  # Change to 50, 200, etc.
```

### Run Longer Simulation
In `CustomRoadNetwork.sumocfg`:
```xml
<time>
    <end value="3000"/>  <!-- Change to 5000, 10000, etc. -->
</time>
```

### Modify Vehicle Battery Capacity
In `CustomRoadNetwork.rou.xml`:
```xml
<param key="device.battery.capacity" value="3000"/>  <!-- Change value -->
<param key="device.battery.initialCharge" value="3000"/>  <!-- Match capacity -->
```

---

## Excel File Structure

### Sheet 1: RSU_Vehicle_Logs
Main data sheet with columns:
- id, ts_utc, rsu_id, rsu_position_x, rsu_position_y
- vehicle_id, speed, battery_charge, battery_capacity, **battery_percentage**
- sim_time, collection_timestamp, rsu_received_at

### Sheet 2: RSU_Status
RSU activity logs:
- id, ts_utc, rsu_id, position_x, position_y
- vehicle_count, data_records

### Sheet 3: Legacy_Logs
Direct TraCI collection (backward compatibility, usually empty)

---

## File Reference

### Core System Files
- `rsu.py` - RSU and RSUNetwork classes
- `server.py` - FastAPI backend with database
- `traCI_rsu.py` - Full simulation with GUI
- `quick_test.py` - Fast test without GUI
- `test_battery_discharge.py` - Extended battery analysis

### Data Analysis Tools
- `extract_data.py` - Export to Excel/CSV
- `analyze_data.py` - Generate charts
- `visualize_rsu.py` - RSU network map
- `verify_battery.py` - Battery verification

### Configuration Files
- `CustomRoadNetwork.sumocfg` - SUMO configuration
- `CustomRoadNetwork.net.xml` - Road network
- `CustomRoadNetwork.rou.xml` - **Vehicle routes & battery specs**
- `chargingStations.add.xml` - Charging stations

### Automation
- `run_complete_test.bat` - Full automated run
- `start_server.bat` - Server only
- `run_simulation.bat` - Simulation only

---

## System Status ✅

**Last Updated:** November 16, 2025

- ✅ Server: Running on port 8000
- ✅ RSUs: 7 units configured
- ✅ Vehicles: 31 electric vehicles
- ✅ Battery Model: Realistic discharge enabled (50% → 38-48%)
- ✅ Database: 3 tables (rsu_vehicle_logs, rsu_status, vehicle_logs)
- ✅ Data Collection: Working (Vehicle → RSU → Server)
- ✅ Battery Percentage: Calculated and displayed
- ✅ Battery Capacity: Realistic values (2000-3000 Wh)

**The system is fully operational and ready for EV route optimization research!** 🚗⚡📊

---

## Quick Reference Commands

```powershell
# Standard workflow
python server.py                    # Terminal 1 - Keep open
python quick_test.py                # Terminal 2 - Run once
python extract_data.py              # Terminal 2 - After simulation

# View results
python verify_battery.py            # Battery statistics
python analyze_data.py              # Generate charts

# Clean restart
Stop-Process -Name python -Force    # Kill all Python
Remove-Item telemetry.db -Force     # Delete old database
python server.py                    # Fresh start
```

**For questions or issues, refer to `RSU_README.md` and `SYSTEM_STATUS.md`**
