# RSU-Based Vehicle Tracking System - WORKING! ✅

## System Overview
Your RSU (Roadside Unit) based V2I (Vehicle-to-Infrastructure) communication system is now **fully operational**!

## What the System Does
Instead of directly querying vehicles through TraCI, the system:
1. **RSUs** are placed at strategic junctions on the road network
2. **Vehicles** send their data to the nearest RSU within range (500m)
3. **RSUs** batch the data and forward it to the FastAPI server
4. **Server** stores all data in a SQLite database
5. **You** can extract and analyze the data

## Test Results ✅
- **31 vehicles** successfully tracked
- **232 records** sent from RSUs to server
- **5 RSUs** actively collecting data
- **Simulation duration**: 90 seconds
- **No errors**: All data transmission successful!

## How to Run the System

### Method 1: Quick Test (Fastest)
```powershell
# 1. Start the server
python server.py

# 2. Run quick test (100 simulation steps, non-GUI)
python quick_test.py

# 3. Extract data
python extract_data.py
```

### Method 2: Full Simulation with GUI
```powershell
# 1. Start the server
python server.py

# 2. Run full simulation (opens SUMO GUI)
python traCI_rsu.py

# 3. Extract data
python extract_data.py
```

### Method 3: Automated Batch File
```powershell
# Run everything automatically
run_complete_test.bat
```

## RSU Network Configuration

### RSU Locations
| RSU ID | Position (x, y) | Coverage Radius |
|--------|-----------------|-----------------|
| RSU_Chachra | (-165.47, -199.59) | 500m |
| RSU_Dhormotola | (-194.59, 27.16) | 500m |
| RSU_Doratana | (-44.04, 49.98) | 500m |
| RSU_Monihar | (79.98, -8.38) | 500m |
| RSU_Muroli | (223.72, -213.15) | 500m |
| RSU_NewMarket | (2.93, 170.72) | 500m |
| RSU_Palbari | (-218.70, 214.90) | 500m |

### Latest Test Results
From the most recent test run:
- **RSU_Palbari**: 100 records (most active)
- **RSU_Doratana**: 97 records
- **RSU_Monihar**: 26 records
- **RSU_NewMarket**: 6 records
- **RSU_Dhormotola**: 3 records

## Output Files

### Excel File
`rsu_telemetry_data_YYYYMMDD_HHMMSS.xlsx`
- **Sheet 1 - RSU Vehicle Logs**: All vehicle data with RSU information
- **Sheet 2 - RSU Status**: RSU activity logs
- **Sheet 3 - Summary Statistics**: Aggregated metrics

### CSV Files
- `rsu_vehicle_logs_YYYYMMDD_HHMMSS.csv`: Vehicle tracking data
- `rsu_status_YYYYMMDD_HHMMSS.csv`: RSU status logs

## Data Fields

### RSU Vehicle Logs
- `ts_utc`: UTC timestamp when data was logged
- `rsu_id`: Which RSU received the data
- `rsu_position_x`, `rsu_position_y`: RSU coordinates
- `vehicle_id`: Unique vehicle identifier
- `speed`: Vehicle speed (m/s)
- `battery_charge`: Current battery charge (Wh)
- `battery_capacity`: Battery capacity (Wh)
- `sim_time`: Simulation time in seconds
- `collection_timestamp`: When vehicle data was collected
- `rsu_received_at`: When RSU received the data

### Analysis Metrics
- **Average Speed per RSU**: Shows traffic patterns at each junction
- **Average Battery Charge per RSU**: Shows battery consumption patterns
- **Vehicle Distribution**: Which RSUs see the most traffic
- **Time Range**: Duration of simulation

## Key Features

### 1. V2I Communication
✅ Vehicles communicate with nearest RSU
✅ RSUs batch data for efficient transmission
✅ Server-side aggregation and storage

### 2. Coverage-Based Routing
✅ 500m coverage radius per RSU
✅ Automatic nearest-RSU selection
✅ Multiple RSUs can track the same vehicle

### 3. Data Batching
✅ RSUs buffer data before sending
✅ Configurable batch size (currently 100 records)
✅ Reduces network overhead

### 4. Real-time Tracking
✅ 10-second collection intervals
✅ Continuous vehicle monitoring
✅ Battery state tracking

## System Architecture

```
┌─────────────┐
│   Vehicles  │  (31 EVs with battery models)
└──────┬──────┘
       │ V2I Communication (500m range)
       ▼
┌─────────────┐
│    RSUs     │  (7 roadside units at junctions)
│  - Collect  │
│  - Buffer   │
│  - Route    │
└──────┬──────┘
       │ HTTP POST /ingest_rsu
       ▼
┌─────────────┐
│ FastAPI     │
│ Server      │  (Port 8000)
│ :8000       │
└──────┬──────┘
       │ SQLite Database
       ▼
┌─────────────┐
│  telemetry  │
│     .db     │  (3 tables: rsu_vehicle_logs, rsu_status, vehicle_logs)
└──────┬──────┘
       │ Data Extraction
       ▼
┌─────────────┐
│ Excel/CSV   │
│   Files     │
└─────────────┘
```

## Server API Endpoints

### POST /ingest_rsu
Receives batched vehicle data from RSUs
- Request: RSUIngestPayload (rsu_id, rsu_position, vehicle_data[])
- Response: Confirmation with record count

### GET /rsu_stats
Get statistics per RSU
- Response: Total records and vehicle count per RSU

### DELETE /clear_data
Clear all database tables
- Use before starting a new simulation

## Troubleshooting

### Problem: "Server exits with code 1"
**Solution**: Check if port 8000 is in use
```powershell
Stop-Process -Name python -Force
python server.py
```

### Problem: "No vehicles in simulation"
**Solution**: The route file has 31 vehicles - they all appear at time 0.00 and complete their routes within ~1700 steps. Use `quick_test.py` for a fast verification.

### Problem: "Database is empty"
**Solution**: Make sure to:
1. Start server first (`python server.py`)
2. Run simulation second (`python quick_test.py`)
3. Then extract data (`python extract_data.py`)

### Problem: "500 Server Error"
**Solution**: This was a SQL parameter mismatch - **FIXED** ✅
The server now correctly handles all 11 database columns.

## Files in Your Workspace

### Core System Files
- `rsu.py` - RSU and RSU Network classes
- `server.py` - FastAPI backend with database
- `traCI_rsu.py` - Full simulation with GUI
- `quick_test.py` - Fast test without GUI

### Data Tools
- `extract_data.py` - Export database to Excel/CSV
- `analyze_data.py` - Statistical analysis with charts
- `visualize_rsu.py` - RSU network visualization
- `check_system.py` - System diagnostics

### Configuration Files
- `CustomRoadNetwork.sumocfg` - SUMO configuration
- `CustomRoadNetwork.net.xml` - Road network
- `CustomRoadNetwork.rou.xml` - Vehicle routes (31 vehicles)
- `chargingStations.add.xml` - Charging stations

### Batch Files
- `run_complete_test.bat` - Automated test run
- `start_server.bat` - Start server only
- `run_simulation.bat` - Run simulation only

### Documentation
- `RSU_README.md` - RSU implementation details
- `QUICKSTART_GUIDE.md` - Quick start instructions
- `HOW_TO_GET_DATA.md` - Data extraction guide
- `SYSTEM_STATUS.md` - **THIS FILE** ✅

## Next Steps

1. **Run More Tests**
   ```powershell
   python quick_test.py
   ```

2. **Analyze Different Scenarios**
   - Modify RSU positions in `traCI_rsu.py`
   - Adjust coverage radius (currently 500m)
   - Change data collection interval (currently 10s)

3. **Visualize Results**
   ```powershell
   python analyze_data.py  # Creates charts
   python visualize_rsu.py  # Network visualization
   ```

4. **Export for Research**
   - Excel files have multiple sheets for easy analysis
   - CSV files for Python/R/MATLAB processing
   - Summary statistics for quick reporting

## System Status: ✅ OPERATIONAL

**Last Test**: 2024-11-13 14:55:24
- Server: ✅ Running on port 8000
- RSUs: ✅ 7 units configured
- Vehicles: ✅ 31 tracked
- Database: ✅ 232 records stored
- Data Export: ✅ Excel & CSV files created

**System is ready for use!** 🎉
