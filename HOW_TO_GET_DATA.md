# 🚗📡 RSU-Based V2I System - Complete Guide

## 📋 Quick Reference

### File Structure
```
Route Optimization of EV/
├── rsu.py                      # RSU classes and network manager
├── server.py                   # FastAPI server with RSU endpoints
├── traCI_rsu.py               # Main simulation script
├── extract_data.py             # Data extraction utility
├── analyze_data.py             # Data analysis and visualization
├── visualize_rsu.py           # RSU coverage visualization
├── start_server.bat           # Server launcher (Windows)
├── run_simulation.bat         # Simulation launcher (Windows)
├── QUICKSTART_GUIDE.md        # Detailed step-by-step guide
├── RSU_README.md              # Architecture documentation
└── telemetry.db               # SQLite database (created after run)
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```powershell
pip install fastapi uvicorn pydantic requests pandas openpyxl matplotlib
```

### Step 2: Start Server (Terminal 1)
**Option A: Using batch file**
```powershell
.\start_server.bat
```

**Option B: Manual**
```powershell
uvicorn server:app --reload
```

### Step 3: Run Simulation (Terminal 2)
**Option A: Using batch file**
```powershell
.\run_simulation.bat
```

**Option B: Manual**
```powershell
python traCI_rsu.py
```

---

## 📊 Getting Your Data

### Method 1: Quick Export (Recommended)
```powershell
python extract_data.py
```
**Output:**
- `rsu_telemetry_data_YYYYMMDD_HHMMSS.xlsx` (Excel with multiple sheets)
- `rsu_vehicle_logs_YYYYMMDD_HHMMSS.csv` (Vehicle data)
- `rsu_status_YYYYMMDD_HHMMSS.csv` (RSU statistics)

### Method 2: Analysis with Charts
```powershell
python analyze_data.py
```
**Output:**
- `rsu_analysis_YYYYMMDD_HHMMSS.png` (4 charts: records, speed, battery, activity)
- `battery_discharge_YYYYMMDD_HHMMSS.png` (Battery over time)
- `analysis_report_YYYYMMDD_HHMMSS.txt` (Text report)

### Method 3: Direct Database Access

**Using Python:**
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('telemetry.db')
df = pd.read_sql_query("SELECT * FROM rsu_vehicle_logs", conn)
df.to_excel('my_data.xlsx', index=False)
conn.close()
```

**Using SQLite CLI:**
```powershell
sqlite3 telemetry.db
# Then run SQL commands:
SELECT * FROM rsu_vehicle_logs LIMIT 10;
SELECT rsu_id, COUNT(*) FROM rsu_vehicle_logs GROUP BY rsu_id;
.exit
```

---

## 🗄️ Database Tables

### 1. `rsu_vehicle_logs` - Main Data Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Unique record ID |
| ts_utc | TEXT | Server timestamp |
| rsu_id | TEXT | Which RSU collected this |
| rsu_position_x | REAL | RSU X coordinate |
| rsu_position_y | REAL | RSU Y coordinate |
| vehicle_id | TEXT | Vehicle identifier |
| speed | REAL | Speed (m/s) |
| battery_charge | REAL | Current battery level |
| battery_capacity | TEXT | Max battery capacity |
| sim_time | REAL | Simulation time (s) |
| collection_timestamp | TEXT | When RSU collected it |
| rsu_received_at | TEXT | When server received it |

### 2. `rsu_status` - RSU Performance
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Unique record ID |
| ts_utc | TEXT | Timestamp |
| rsu_id | TEXT | RSU identifier |
| position_x | REAL | X coordinate |
| position_y | REAL | Y coordinate |
| vehicle_count | INTEGER | Vehicles in this batch |
| data_records | INTEGER | Records sent |

### 3. `vehicle_logs` - Legacy (backward compatibility)
Same as original TraCI implementation

---

## 🔍 Common Data Queries

### Get all data for a specific RSU
```sql
SELECT * FROM rsu_vehicle_logs 
WHERE rsu_id = 'RSU_Doratana'
ORDER BY sim_time;
```

### Get vehicle trajectory
```sql
SELECT vehicle_id, sim_time, rsu_id, speed, battery_charge
FROM rsu_vehicle_logs
WHERE vehicle_id = 'vehicle_0'
ORDER BY sim_time;
```

### Get RSU performance summary
```sql
SELECT 
    rsu_id,
    COUNT(*) as total_records,
    COUNT(DISTINCT vehicle_id) as unique_vehicles,
    AVG(speed) as avg_speed,
    MIN(battery_charge) as min_battery
FROM rsu_vehicle_logs
GROUP BY rsu_id
ORDER BY total_records DESC;
```

### Get vehicles with low battery
```sql
SELECT DISTINCT vehicle_id, MIN(battery_charge) as lowest_battery
FROM rsu_vehicle_logs
GROUP BY vehicle_id
HAVING lowest_battery < 20
ORDER BY lowest_battery;
```

### Get activity by time period
```sql
SELECT 
    CAST(sim_time / 60 AS INTEGER) as minute,
    COUNT(*) as records,
    COUNT(DISTINCT vehicle_id) as active_vehicles
FROM rsu_vehicle_logs
GROUP BY minute
ORDER BY minute;
```

---

## 🌐 API Endpoints

### While Server is Running

**1. Interactive API Docs**
- URL: http://127.0.0.1:8000/docs
- Test all endpoints in your browser

**2. Get RSU Statistics**
```powershell
curl http://127.0.0.1:8000/rsu_stats
```

**3. Clear All Data**
```powershell
curl -X DELETE http://127.0.0.1:8000/clear_data
```

**4. Legacy Vehicle Ingestion**
```powershell
curl -X POST http://127.0.0.1:8000/ingest -H "Content-Type: application/json" -d @data.json
```

---

## 🎨 Visualization

### RSU Coverage Map
```powershell
python visualize_rsu.py
```
**Output:** `rsu_coverage_map.png` showing RSU positions and coverage areas

### Custom Visualization Example
```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('telemetry.db')

# Get speed data
df = pd.read_sql_query("""
    SELECT rsu_id, AVG(speed) as avg_speed
    FROM rsu_vehicle_logs
    GROUP BY rsu_id
""", conn)

# Plot
plt.bar(df['rsu_id'], df['avg_speed'])
plt.title('Average Speed by RSU')
plt.xlabel('RSU ID')
plt.ylabel('Speed (m/s)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('speed_by_rsu.png')
plt.show()

conn.close()
```

---

## ⚙️ Configuration

### Adjust RSU Coverage
Edit `traCI_rsu.py`:
```python
RSU_COVERAGE_RADIUS = 500.0  # Change to 1000.0 for wider coverage
```

### Adjust Data Collection Frequency
Edit `traCI_rsu.py`:
```python
LOG_INTERVAL = 10  # Change to 5 for more frequent collection
```

### Adjust Batch Size
Edit `traCI_rsu.py`:
```python
RSU_BATCH_SIZE = 100  # Change to 50 for smaller batches
```

### Add More RSUs
Edit `traCI_rsu.py` in `setup_rsu_network()`:
```python
rsu_positions = {
    'RSU_Chachra': (-165.47, -199.59),
    # ... existing RSUs ...
    'RSU_MyCustom': (100.0, 50.0),  # Add new RSU here
}
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Import errors | Run: `pip install fastapi uvicorn pydantic requests pandas openpyxl matplotlib` |
| Server won't start | Check if port 8000 is free: `netstat -ano \| findstr :8000` |
| No data collected | Increase `RSU_COVERAGE_RADIUS` or add more RSUs |
| SUMO won't start | Verify: `sumo-gui --version` works |
| Database locked | Close all database browsers, stop server |
| Empty Excel files | Make sure simulation ran and completed |

---

## 📈 Example Workflow

### Complete Research Data Collection Workflow

```powershell
# 1. Install dependencies
pip install fastapi uvicorn pydantic requests pandas openpyxl matplotlib

# 2. Start server (Terminal 1)
uvicorn server:app --reload

# 3. Run simulation (Terminal 2)
python traCI_rsu.py
# Let it run for desired duration, then stop

# 4. Extract data
python extract_data.py
# Creates: rsu_telemetry_data_YYYYMMDD_HHMMSS.xlsx

# 5. Analyze data
python analyze_data.py
# Creates: Charts and analysis report

# 6. Visualize coverage
python visualize_rsu.py
# Creates: rsu_coverage_map.png

# 7. Custom analysis (optional)
# Open Excel file or use Python/pandas for further analysis
```

---

## 📚 Documentation Files

- **QUICKSTART_GUIDE.md** - Detailed step-by-step instructions
- **RSU_README.md** - Architecture and technical details
- **THIS_FILE.md** - Quick reference and common tasks

---

## 🎯 Next Steps

1. ✅ Run the system and collect data
2. ✅ Export to Excel/CSV
3. ✅ Analyze with provided scripts
4. ✅ Create custom visualizations
5. ✅ Use data for route optimization research
6. ✅ Modify RSU positions for different scenarios
7. ✅ Integrate with machine learning models

---

## 💡 Tips

- **Long simulations**: Let SUMO run for 1000+ seconds for rich data
- **Multiple runs**: Clear data between runs for clean datasets
- **Backup data**: Copy `telemetry.db` before clearing
- **Export formats**: CSV for Python/R, Excel for manual analysis
- **Performance**: Increase `RSU_BATCH_SIZE` for fewer server calls
- **Coverage**: Use `visualize_rsu.py` to check gaps in coverage

---

## 📞 Support

Need help? Check:
1. QUICKSTART_GUIDE.md for detailed instructions
2. RSU_README.md for architecture details
3. Code comments in each Python file
4. FastAPI docs at http://127.0.0.1:8000/docs (when server running)

---

**You're all set! Start with the 3-step Quick Start above and you'll have data in minutes!** 🚀
