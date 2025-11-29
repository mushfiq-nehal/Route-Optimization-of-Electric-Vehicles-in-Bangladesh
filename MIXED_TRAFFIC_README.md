# Mixed Traffic Implementation - EV and Non-EV Vehicles

## Overview
The simulation now includes **realistic mixed traffic** with both Electric Vehicles (EVs) and conventional Non-EV vehicles (cars, buses, trucks, motorcycles, CNG rickshaws). The RSU system intelligently identifies and collects data **only from EVs**.

---

## 🚗 Vehicle Types

### Electric Vehicles (40% of traffic)
1. **Default_EV** - Standard electric car (35 kWh battery)
2. **Easybike_ER-02B** - Electric bike (3 kWh battery)
3. **Small_Easybike_V12** - Small electric bike (2 kWh battery)
4. **Electric_Rickshaw_V8** - Electric rickshaw (2.5 kWh battery)

### Non-Electric Vehicles (60% of traffic)
1. **Private_Car** - Regular passenger car
   - Length: 4.5m, Max Speed: 33.33 m/s (120 km/h)
   - Emission Class: HBEFA3/PC_G_EU4
   - Color: Gray (0.8, 0.8, 0.8)

2. **CNG_Rickshaw** - CNG auto-rickshaw
   - Length: 2.5m, Max Speed: 8.33 m/s (30 km/h)
   - Emission Class: HBEFA3/PC_G_EU4
   - Color: Yellow-Gold (0.9, 0.7, 0.2)

3. **Bus** - Public bus
   - Length: 12.0m, Max Speed: 19.44 m/s (70 km/h)
   - Emission Class: HBEFA3/Bus
   - Color: Blue (0.2, 0.4, 0.8)

4. **Truck** - Delivery truck
   - Length: 7.5m, Max Speed: 22.22 m/s (80 km/h)
   - Emission Class: HBEFA3/HDV
   - Color: Brown (0.6, 0.3, 0.1)

5. **Motorcycle** - Motorcycle/scooter
   - Length: 2.2m, Max Speed: 27.78 m/s (100 km/h)
   - Emission Class: HBEFA3/MC_SI_2S
   - Color: Dark Gray (0.3, 0.3, 0.3)

---

## 📊 Traffic Composition

### Current Configuration
```
Total Vehicles: 205
├─ Test Vehicles: 5 (all EVs)
└─ Traffic Vehicles: 200
   ├─ EVs: 80 (40%)
   └─ Non-EVs: 120 (60%)
```

### Distribution Pattern
The traffic is distributed across 5 routes with a **repeating pattern every 5 vehicles**:
- Vehicle 1: EV (e.g., Easybike_ER-02B)
- Vehicle 2: EV (e.g., Small_Easybike_V12)
- Vehicle 3: Non-EV (e.g., Private_Car)
- Vehicle 4: Non-EV (e.g., CNG_Rickshaw)
- Vehicle 5: Non-EV (e.g., Bus)

This pattern repeats to create a **40% EV / 60% Non-EV** realistic traffic mix.

---

## 🔍 RSU EV Detection System

### How It Works

#### 1. Vehicle Type Identification
The RSU system uses **battery device detection** to identify EVs:

```python
def is_electric_vehicle(vehicle_id):
    """Check if vehicle has battery device"""
    try:
        # Method 1: Check explicit battery flag
        has_battery = traci.vehicle.getParameter(vehicle_id, "has.battery.device")
        if has_battery and has_battery.lower() == "true":
            return True
        
        # Method 2: Check battery capacity
        capacity = float(traci.vehicle.getParameter(vehicle_id, "device.battery.capacity"))
        return capacity > 0
    except:
        return False  # No battery = Non-EV
```

#### 2. Selective Data Collection
Only EVs are tracked:
```python
# Filter vehicles
ev_ids = [vid for vid in vehicle_ids if is_electric_vehicle(vid)]
non_ev_count = len(vehicle_ids) - len(ev_ids)

# Collect data only from EVs
for vid in ev_ids:
    # Collect battery, speed, position data
    rsu_network.collect_vehicle_data(vid, position, vehicle_data, is_ev=True)
```

#### 3. RSU Network Filtering
The RSU network enforces EV-only data collection:
```python
def collect_vehicle_data(self, vehicle_id, vehicle_position, vehicle_data, is_ev=True):
    # Only process EVs
    if not is_ev:
        return  # Silently skip non-EVs
    
    # Route to nearest RSU
    nearest_rsu.collect_vehicle_data(vehicle_id, vehicle_data, is_ev)
```

---

## 📡 RSU Data Collection

### What Gets Collected (EVs Only)
For each EV within RSU range, the following data is collected:
```json
{
    "vehicle_id": "r1_v1",
    "vehicle_type": "Easybike_ER-02B",
    "speed": 12.5,
    "battery_charge": 2500.0,
    "battery_capacity": 3000.0,
    "battery_percentage": 83.33,
    "sim_time": 120.0,
    "position": [100.5, 200.3],
    "rsu_id": "RSU_Palbari",
    "rsu_position": [-218.70, 214.90],
    "collection_timestamp": "2025-11-27T10:30:45Z",
    "vehicle_type": "EV"
}
```

### What Gets Ignored (Non-EVs)
Non-EV vehicles are:
- ✅ Visible in simulation (participate in traffic)
- ✅ Interact with traffic lights, lanes, other vehicles
- ❌ NOT tracked by RSU system
- ❌ NO data collected or sent to server
- ❌ NOT counted in data statistics

---

## 🎯 Benefits of Mixed Traffic

### 1. **Realistic Traffic Conditions**
- Mimics real-world road conditions in Bangladesh
- Various vehicle sizes and speeds
- Different acceleration/deceleration patterns

### 2. **Accurate EV Performance Testing**
- EVs navigate through realistic traffic
- Overtaking scenarios with mixed vehicle types
- Real congestion patterns

### 3. **Focused Data Collection**
- RSU resources focused on EVs only
- Reduced server load (60% fewer data points)
- Cleaner dataset for EV analysis

### 4. **Visual Distinction**
Different colors help identify vehicle types:
- 🔴 Red: Test EVs (your 5 test vehicles)
- ⚪ Gray: Private cars
- 🟡 Yellow-gold: CNG rickshaws
- 🔵 Blue: Buses
- 🟤 Brown: Trucks
- ⚫ Dark gray: Motorcycles
- EVs: Default SUMO colors (vary by type)

---

## 🚀 Running the Simulation

### Option 1: Quick Run (SUMO GUI)
```bash
python traCI_rsu.py
```
This will:
1. Start SUMO GUI with mixed traffic
2. Show all vehicles (EVs and Non-EVs)
3. Collect and send data only from EVs
4. Display real-time statistics

### Option 2: With FastAPI Server
```bash
# Terminal 1: Start server
python server.py

# Terminal 2: Run simulation
python traCI_rsu.py
```

---

## 📈 Console Output Example

```
Starting simulation loop...

⚡ RSU Network configured to collect data ONLY from Electric Vehicles

[Step 100] New vehicles appeared: 10 (EVs: 4, Non-EVs: 6)
[Sim Time: 10.0s] Active vehicles: 25 (EVs: 10, Non-EVs: 15)
  Collecting data from 10 EVs...
  📊 Total seen: 25 vehicles (10 EVs), EV data points collected: 10

[Sim Time: 20.0s] Active vehicles: 40 (EVs: 16, Non-EVs: 24)
  Collecting data from 16 EVs...
  📊 Total seen: 40 vehicles (16 EVs), EV data points collected: 26

[RSU-RSU_Palbari] Successfully sent 16 records to server
```

---

## 🛠️ Customization

### Adjust EV/Non-EV Ratio
Edit `generate_traffic.py`:
```python
# Current: 40% EV, 60% Non-EV
# To change to 50/50, modify the pattern:
if i % 2 == 0:  # Every other vehicle
    v_type = ev_types[i % len(ev_types)]
else:
    v_type = non_ev_types[i % len(non_ev_types)]
```

### Add More Non-EV Types
Edit `CustomRoadNetwork.rou.xml`:
```xml
<vType id="Taxi" vClass="taxi" accel="2.0" decel="4.0" 
       length="4.2" width="1.8" maxSpeed="25.0" 
       guiShape="taxi" color="1.0,1.0,0.0">
</vType>
```

Then add to `non_ev_types` list in `generate_traffic.py`:
```python
non_ev_types = ['Private_Car', 'CNG_Rickshaw', 'Bus', 'Truck', 'Motorcycle', 'Taxi']
```

### Regenerate Traffic
After any changes:
```bash
python generate_traffic.py
```

---

## 🔬 Technical Details

### Lane Change Behavior
All vehicles use LC2013 model with realistic parameters:
- **EVs**: Balanced behavior (strategic=1.0, cooperative=1.0)
- **Private Cars/Motorcycles**: Aggressive lane changes (speedGain=1.0-1.5)
- **Buses/Trucks**: Prefer right lane (lcKeepRight=1.0)
- **CNG Rickshaws**: Conservative (speedGain=0.5)

### Emission Classes
- **EVs**: Energy/unknown (no emissions, battery-based)
- **Cars/CNG**: HBEFA3/PC_G_EU4 (Euro 4 standards)
- **Buses**: HBEFA3/Bus (heavy duty diesel)
- **Trucks**: HBEFA3/HDV (heavy duty vehicle)
- **Motorcycles**: HBEFA3/MC_SI_2S (2-stroke gasoline)

### Vehicle Dimensions
Realistic sizes for Bangladesh roads:
- **CNG Rickshaw**: 2.5m × 1.0m (compact)
- **Private Car**: 4.5m × 1.8m (sedan)
- **Bus**: 12.0m × 2.5m (large)
- **Truck**: 7.5m × 2.4m (medium delivery)
- **Motorcycle**: 2.2m × 0.8m (narrow)

---

## ✅ Verification Checklist

After running the simulation, verify:

1. **Visual Check (SUMO GUI)**
   - [ ] See different colored vehicles
   - [ ] Buses and trucks are larger
   - [ ] Mixed vehicle types on all routes

2. **Console Output**
   - [ ] "Active vehicles: X (EVs: Y, Non-EVs: Z)"
   - [ ] "Collecting data from Y EVs..."
   - [ ] EV count ≈ 40% of total vehicles

3. **Server Data (if using FastAPI)**
   - [ ] Only EV data in database
   - [ ] Vehicle types show EV models only
   - [ ] No private cars, buses, trucks in data

4. **Traffic Statistics**
   - [ ] Total vehicles: 205
   - [ ] EVs tracked: ~85 (5 test + 80 traffic)
   - [ ] Non-EVs ignored: ~120

---

## 🐛 Troubleshooting

### Issue: All vehicles look the same
**Solution**: Colors defined in vType, regenerate traffic:
```bash
python generate_traffic.py
```

### Issue: RSU collecting data from all vehicles
**Solution**: Check traCI_rsu.py has `is_electric_vehicle()` function and uses it:
```python
ev_ids = [vid for vid in vehicle_ids if is_electric_vehicle(vid)]
```

### Issue: No Non-EVs in simulation
**Solution**: Verify CustomRoadNetwork.rou.xml has Non-EV vTypes:
```bash
grep "Private_Car\|Bus\|Truck" CustomRoadNetwork.rou.xml
```

### Issue: Battery parameter errors
**Solution**: Non-EVs don't have battery parameters. This is expected and handled:
```python
try:
    battery = traci.vehicle.getParameter(vid, "device.battery.capacity")
except:
    # Not an EV, skip silently
    pass
```

---

## 📚 Related Files

- `CustomRoadNetwork.rou.xml` - Vehicle definitions and routes
- `generate_traffic.py` - Traffic generation script
- `traCI_rsu.py` - Simulation with EV detection
- `rsu.py` - RSU network module with EV filtering
- `server.py` - FastAPI backend (receives only EV data)

---

## 🎓 For Your Thesis Defense

### Key Points to Mention:
1. **Realistic simulation** with 60% conventional vehicles (cars, buses, trucks)
2. **Smart RSU system** that identifies EVs via battery device detection
3. **Selective data collection** - only EVs tracked (40% of traffic)
4. **Accurate representation** of Bangladesh road conditions
5. **Efficient system** - reduces data collection overhead by 60%

### Demonstration Tips:
1. Show SUMO GUI with mixed traffic colors
2. Point out different vehicle sizes (buses vs motorcycles)
3. Highlight console showing "EVs: X, Non-EVs: Y"
4. Explain battery device detection logic
5. Show server only receiving EV data

---

## 📊 Statistics Summary

```
═══════════════════════════════════════════════════════
                  TRAFFIC COMPOSITION
═══════════════════════════════════════════════════════
Total Vehicles:           205
├─ Test Vehicles:         5    (2.4%)  [All EVs]
└─ Traffic Vehicles:      200  (97.6%)
   ├─ Electric Vehicles:  80   (40.0%)
   └─ Non-EV Vehicles:    120  (60.0%)
      ├─ Private Cars:    ~24  (12.0%)
      ├─ CNG Rickshaws:   ~24  (12.0%)
      ├─ Buses:           ~24  (12.0%)
      ├─ Trucks:          ~24  (12.0%)
      └─ Motorcycles:     ~24  (12.0%)

RSU Data Collection:
├─ EVs Tracked:           85   (100% of EVs)
└─ Non-EVs Ignored:       120  (100% of Non-EVs)

Efficiency Gain:          60% reduction in data points
═══════════════════════════════════════════════════════
```

---

**Last Updated**: November 27, 2025  
**Status**: ✅ Fully Implemented and Tested
