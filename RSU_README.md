# RSU-Based Vehicle-to-Infrastructure (V2I) Communication System

## Overview

This system implements a Roadside Unit (RSU) based architecture for collecting vehicle telemetry data from SUMO simulations. Instead of directly querying vehicles through TraCI, vehicles communicate with nearby RSUs, which then forward the data to a central server.

## Architecture

```
┌─────────────┐
│  Vehicles   │ (SUMO Simulation)
└──────┬──────┘
       │ V2I Communication
       ▼
┌─────────────┐
│    RSUs     │ (Roadside Units - Coverage Zones)
└──────┬──────┘
       │ Internet/Network
       ▼
┌─────────────┐
│   Server    │ (FastAPI Backend)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │ (SQLite)
└─────────────┘
```

## Components

### 1. RSU Module (`rsu.py`)

**RSU Class:**
- Represents a single Roadside Unit
- Properties:
  - `rsu_id`: Unique identifier
  - `position`: (x, y) coordinates in the road network
  - `coverage_radius`: Communication range (default: 500m)
  - `server_url`: Backend server endpoint
- Functions:
  - `is_vehicle_in_range()`: Check if vehicle is within coverage
  - `collect_vehicle_data()`: Collect data from nearby vehicles
  - `send_data_to_server()`: Forward buffered data to server

**RSUNetwork Class:**
- Manages multiple RSUs
- Functions:
  - `add_rsu()`: Add new RSU to the network
  - `find_nearest_rsu()`: Find closest RSU for a vehicle
  - `collect_vehicle_data()`: Route vehicle data to appropriate RSU
  - `send_all_data()`: Trigger data transmission from all RSUs

### 2. Server (`server.py`)

**New Endpoints:**

- `POST /ingest_rsu`: Receive data from RSUs
  - Payload includes RSU ID, position, and batch of vehicle data
  - Stores data in `rsu_vehicle_logs` table
  
- `GET /rsu_stats`: Get RSU statistics
  - Returns total vehicles served and records sent per RSU

**New Database Tables:**

- `rsu_vehicle_logs`: Vehicle data received via RSUs
  - Includes RSU metadata (ID, position, collection timestamp)
  
- `rsu_status`: RSU activity logs
  - Tracks number of vehicles and records per RSU

### 3. TraCI RSU Script (`traCI_rsu.py`)

**RSU Deployment:**
- RSUs are placed at major intersections:
  - RSU_Chachra: (-165.47, -199.59)
  - RSU_Dhormotola: (-194.59, 27.16)
  - RSU_Doratana: (-44.04, 49.98)
  - RSU_Monihar: (79.98, -8.38)
  - RSU_Muroli: (223.72, -213.15)
  - RSU_NewMarket: (2.93, 170.72)
  - RSU_Palbari: (-218.70, 214.90)

**Data Flow:**
1. Every 10 seconds, collect data from all vehicles
2. For each vehicle:
   - Get position and telemetry data
   - Find nearest RSU within coverage range
   - Send data to that RSU
3. RSUs buffer data and send to server in batches

## Usage

### 1. Start the Server

```powershell
python server.py
```

The server will start on `http://127.0.0.1:8000`

### 2. Run the RSU-based Simulation

```powershell
python traCI_rsu.py
```

This will:
- Setup the RSU network
- Clear previous data
- Start SUMO simulation
- Collect vehicle data via RSUs
- Send data to server periodically

### 3. Monitor RSU Activity

The script prints RSU status every 100 simulation steps:

```
============================================================
RSU NETWORK STATUS
============================================================
RSU-RSU_Chachra:
  Position: (-165.47, -199.59)
  Coverage: 500.0m
  Connected Vehicles: 5
  Buffered Records: 42
...
```

## Configuration

### Adjust RSU Coverage

In `traCI_rsu.py`, modify:
```python
RSU_COVERAGE_RADIUS = 500.0  # meters
```

### Adjust Data Collection Interval

```python
LOG_INTERVAL = 10  # seconds
```

### Adjust Batch Size

```python
RSU_BATCH_SIZE = 100  # records per batch
```

## Advantages of RSU-Based Architecture

1. **Realistic V2I Communication**: Mimics real-world vehicle-to-infrastructure scenarios
2. **Scalability**: RSUs can aggregate data from multiple vehicles
3. **Network Efficiency**: Batch transmission reduces network overhead
4. **Coverage Management**: Vehicles only communicate when in RSU range
5. **Data Enrichment**: RSU metadata (location, ID) added to each record
6. **Fault Tolerance**: Vehicles out of range are logged for monitoring

## Database Schema

### rsu_vehicle_logs

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| ts_utc | TEXT | Server reception timestamp |
| rsu_id | TEXT | RSU identifier |
| rsu_position_x | REAL | RSU X coordinate |
| rsu_position_y | REAL | RSU Y coordinate |
| vehicle_id | TEXT | Vehicle identifier |
| speed | REAL | Vehicle speed (m/s) |
| battery_charge | REAL | Current battery charge |
| battery_capacity | TEXT | Battery capacity |
| sim_time | REAL | Simulation timestamp |
| collection_timestamp | TEXT | RSU collection time |
| rsu_received_at | TEXT | Server reception time |

### rsu_status

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| ts_utc | TEXT | Timestamp |
| rsu_id | TEXT | RSU identifier |
| position_x | REAL | X coordinate |
| position_y | REAL | Y coordinate |
| vehicle_count | INTEGER | Number of vehicles |
| data_records | INTEGER | Number of records sent |

## API Examples

### Get RSU Statistics

```bash
curl http://127.0.0.1:8000/rsu_stats
```

Response:
```json
{
  "rsu_stats": [
    {
      "rsu_id": "RSU_Chachra",
      "position": [-165.47, -199.59],
      "total_vehicles": 150,
      "total_records": 1523,
      "last_update": "2025-11-12T10:30:45Z"
    }
  ]
}
```

### Clear All Data

```bash
curl -X DELETE http://127.0.0.1:8000/clear_data
```

## Comparison with Direct TraCI

| Aspect | Direct TraCI (traCI.py) | RSU-Based (traCI_rsu.py) |
|--------|------------------------|--------------------------|
| Communication | Direct vehicle queries | Via RSU intermediaries |
| Realism | Less realistic | More realistic V2I |
| Coverage | All vehicles | Only vehicles in RSU range |
| Data Enrichment | Basic telemetry | + RSU metadata |
| Scalability | Limited | Better (RSU aggregation) |
| Network Load | Higher | Lower (batching) |

## Troubleshooting

### No vehicles in RSU range

- Increase `RSU_COVERAGE_RADIUS`
- Add more RSUs at strategic locations
- Check vehicle routes overlap with RSU positions

### High data loss

- Increase RSU coverage radius
- Reduce `LOG_INTERVAL`
- Increase `RSU_BATCH_SIZE`

### Server connection errors

- Verify server is running on port 8000
- Check `SERVER_URL` in `traCI_rsu.py`
- Check firewall settings

## Future Enhancements

1. **Dynamic RSU Placement**: Automatically place RSUs based on traffic density
2. **RSU-to-RSU Communication**: Enable data forwarding between RSUs
3. **Priority-based Data**: Prioritize critical vehicle data (low battery, accidents)
4. **Real-time Analytics**: Add dashboard for live RSU monitoring
5. **Blockchain Integration**: Secure data transmission using blockchain
6. **Machine Learning**: Predict optimal RSU placement using ML

## License

This project is part of the Route Optimization of Electric Vehicles system.
