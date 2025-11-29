# Route 1 (Direct E0) Heavy Traffic Configuration

## Changes Applied - November 19, 2025

### 1. Traffic Light Red Duration - 3X Increase

**Route 1 (E0 Direct: Palbari → Doratana)** passes through:
- **Palbari Junction (J1)** - Traffic light at start
- **Doratana Junction (J2)** - Traffic light at end

#### J1 (Palbari) Traffic Light Changes:
- **All-Red Duration**: 2s → **6s** (3x increase)
  - Phase 5: `duration="6" state="rrrrrrrr"` 
  - Phase 8: `duration="6" state="rrrrrrrr"`
- **Effect**: Vehicles on E0 must wait 3x longer at red lights when departing Palbari

#### J2 (Doratana) Traffic Light Changes:
- **All-Red Duration**: 2s → **6s** (3x increase)
  - Phase 5: `duration="6" state="rrrrrrrrrrrrrrrrrrrrrrrrr"`
  - Phase 10: `duration="6" state="rrrrrrrrrrrrrrrrrrrrrrrrr"`
- **Effect**: Vehicles on E0 must wait 3x longer at red lights when arriving at Doratana

**Total Red Light Delay Increase**: 8 seconds per cycle (4s × 2 junctions)

### 2. Very Heavy Traffic on Route 1 (E0)

#### Traffic Increase:
- **Before**: 40 vehicles on Route 1
- **After**: 140 vehicles on Route 1 (100 additional vehicles added)
- **Increase**: +250% more traffic
- **Departure Times**: Vehicles depart from 5s to 288s (spread over 4.8 minutes)

#### Traffic Composition (Route 1):
- 35 × Easybike_ER-02B (3000 Wh battery)
- 35 × Small_Easybike_V12 (2000 Wh battery)
- 35 × Electric_Rickshaw_V8 (2500 Wh battery)
- 35 × Default_EV (35000 Wh battery)

### 3. Total Simulation Statistics

| Metric | Value |
|--------|-------|
| Total Vehicles | 305 |
| Route 1 (E0) | 140 vehicles |
| Route 2 (E3 E9) | 40 vehicles |
| Route 3 (E3 E3.189 -E4) | 40 vehicles |
| Route 4 (E2 -E1) | 40 vehicles |
| Route 5 (E2 -E8 E7) | 40 vehicles |
| Test Vehicles | 5 (1 per route) |

## Expected Impact on Route 1 Performance

### Increased Battery Consumption Due To:
1. **Longer Idling at Red Lights**
   - 3x longer all-red phases
   - More stop-and-go cycles
   - Increased auxiliary power consumption (100W constant intake)

2. **Heavy Traffic Congestion**
   - 140 vehicles competing for 2 lanes
   - More braking and acceleration
   - Lower average speeds
   - Queue formation at intersections

3. **Slower Travel Times**
   - Expected travel time increase from 3-5 minutes to 10-15+ minutes
   - More time spent in traffic = more energy consumption

### Battery Consumption Prediction:
- **Previous (40 vehicles, 2s red)**: ~245 Wh (16.4%)
- **Estimated (140 vehicles, 6s red)**: ~400-500 Wh (27-33%)
- **Increase**: +60-100% more battery consumption

## Testing Objective

This configuration tests whether **Route 1 (Direct)** remains the most charge-efficient route even under:
- ✅ Very heavy traffic (140 vehicles vs 40 on other routes)
- ✅ Longer red light delays (3x increase)
- ✅ Realistic urban congestion scenarios

**Hypothesis**: If Route 1 still performs better than longer alternative routes despite these handicaps, it proves the direct path is robustly optimal for charge efficiency.

## Files Modified

1. **CustomRoadNetwork.net.xml** - Traffic lights J1 and J2 red phases increased to 6s
2. **CustomRoadNetwork.rou.xml** - 100 additional vehicles added to Route 1 (r1_v41 to r1_v140)
3. **increase_route1_traffic.py** - Script to add heavy traffic to Route 1

## Run Configuration

```bash
python palbari_doratana_comparison.py
```

- Simulation time: Up to 6000 steps (100 minutes)
- Expected completion: All routes should complete within simulation time
- Output files: JSON, CSV, TXT with comparison results
