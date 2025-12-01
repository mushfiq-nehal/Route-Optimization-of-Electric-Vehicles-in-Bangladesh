# R1-R7 Route Coverage Analysis

## Summary
✅ **All 7 routes now have complete vehicle type coverage**
- **Total Vehicles**: 35 (7 routes × 5 vehicle types)
- **Total Vehicle Types**: 5 (3 EV types + 1 Default EV + 1 Non-EV)
- **Total Routes**: 7 (R1 through R7)

## Vehicle Types

### Electric Vehicles (EVs)
1. **Easybike_ER-02B**
   - Battery: 3000 Wh
   - Weight: 700 kg
   - Max Speed: 13.9 m/s (50 km/h)
   - Range: 120-150 km
   - Passengers: 5

2. **Small_Easybike_V12**
   - Battery: 2000 Wh
   - Weight: 500 kg
   - Max Speed: 7.78 m/s (28 km/h)
   - Range: 100-120 km
   - Passengers: 2 adults + 1 kid

3. **Electric_Rickshaw_V8**
   - Battery: 2500 Wh
   - Weight: 500 kg
   - Max Speed: 7.78 m/s (28 km/h)
   - Range: 100-120 km
   - Passengers: 2 adults + 1 kid

4. **Default_EV**
   - Battery: 35000 Wh
   - Weight: 1830 kg
   - Max Speed: 13.9 m/s (50 km/h)
   - High capacity reference vehicle

### Non-Electric Vehicles
5. **Non_EV**
   - Standard passenger car (HBEFA3/PC_G_EU4)
   - Max Speed: 50.0 m/s (180 km/h)
   - No battery device

## Route Details

### R1: Palbari → Dhormotola (Partial)
**Path**: E3 → E3.189
**Description**: Short route from Palbari through partial Dhormotola path
**Vehicles**: 5 (all types covered)
- R1_Easybike_ER-02B (depart: 1.00s)
- R1_Small_Easybike_V12 (depart: 3.00s)
- R1_Electric_Rickshaw_V8 (depart: 5.00s)
- R1_Default_EV (depart: 7.00s)
- R1_Non_EV (depart: 9.00s)

### R2: Palbari → Monihar (via Dhormotola, Muroli)
**Path**: E3 → E3.189 → E5 → E6 → E7
**Description**: Extended route covering major junctions to Monihar
**Vehicles**: 5 (all types covered)
- R2_Easybike_ER-02B (depart: 11.00s)
- R2_Small_Easybike_V12 (depart: 13.00s)
- R2_Electric_Rickshaw_V8 (depart: 15.00s)
- R2_Default_EV (depart: 17.00s)
- R2_Non_EV (depart: 19.00s)

### R3: Palbari → Dhormotola (Direct)
**Path**: E3 → E9
**Description**: Direct route from Palbari to Dhormotola via E9
**Vehicles**: 5 (all types covered)
- R3_Easybike_ER-02B (depart: 21.00s)
- R3_Small_Easybike_V12 (depart: 23.00s)
- R3_Electric_Rickshaw_V8 (depart: 25.00s)
- R3_Default_EV (depart: 27.00s)
- R3_Non_EV (depart: 29.00s)

### R4: Chachra → Doratana
**Path**: E4
**Description**: Single edge from Chachra to Doratana
**Vehicles**: 5 (all types covered)
- R4_Easybike_ER-02B (depart: 31.00s)
- R4_Small_Easybike_V12 (depart: 33.00s)
- R4_Electric_Rickshaw_V8 (depart: 35.00s)
- R4_Default_EV (depart: 37.00s)
- R4_Non_EV (depart: 39.00s)

### R5: Chachra → Muroli
**Path**: E4 → E5
**Description**: Route from Chachra through Doratana to Muroli
**Vehicles**: 5 (all types covered)
- R5_Easybike_ER-02B (depart: 41.00s)
- R5_Small_Easybike_V12 (depart: 43.00s)
- R5_Electric_Rickshaw_V8 (depart: 45.00s)
- R5_Default_EV (depart: 47.00s)
- R5_Non_EV (depart: 49.00s)

### R6: Palbari → New Market
**Path**: E2
**Description**: Direct route from Palbari to New Market
**Vehicles**: 5 (all types covered)
- R6_Easybike_ER-02B (depart: 51.00s)
- R6_Small_Easybike_V12 (depart: 53.00s)
- R6_Electric_Rickshaw_V8 (depart: 55.00s)
- R6_Default_EV (depart: 57.00s)
- R6_Non_EV (depart: 59.00s)

### R7: Via Monihar Area
**Path**: E8
**Description**: Route through Monihar area
**Vehicles**: 5 (all types covered)
- R7_Easybike_ER-02B (depart: 61.00s)
- R7_Small_Easybike_V12 (depart: 63.00s)
- R7_Electric_Rickshaw_V8 (depart: 65.00s)
- R7_Default_EV (depart: 67.00s)
- R7_Non_EV (depart: 69.00s)

## Coverage Matrix

| Route | Easybike_ER-02B | Small_Easybike_V12 | Electric_Rickshaw_V8 | Default_EV | Non_EV |
|-------|-----------------|-------------------|---------------------|------------|--------|
| R1    | ✅              | ✅                | ✅                  | ✅         | ✅     |
| R2    | ✅              | ✅                | ✅                  | ✅         | ✅     |
| R3    | ✅              | ✅                | ✅                  | ✅         | ✅     |
| R4    | ✅              | ✅                | ✅                  | ✅         | ✅     |
| R5    | ✅              | ✅                | ✅                  | ✅         | ✅     |
| R6    | ✅              | ✅                | ✅                  | ✅         | ✅     |
| R7    | ✅              | ✅                | ✅                  | ✅         | ✅     |

## Verification Results
✅ **100% Coverage Achieved**
- All 7 routes have all 5 vehicle types assigned
- Total: 35 vehicles configured
- Staggered departure times (2-second intervals) for realistic traffic flow
- Route file: `CustomRoadNetwork.rou.xml`

### SUMO Validation
✅ **Simulation Test Passed**
```
Simulation ended at time: 80.00
Vehicles:
 Inserted: 35
 Running: 35
 Waiting: 0
```
All 35 vehicles successfully loaded and running without errors.

## Key Features
1. **Comprehensive Testing**: Every route can now be tested with all vehicle types
2. **EV Optimization**: 4 different EV types with varying battery capacities for comparison
3. **Non-EV Baseline**: Non_EV vehicles provide comparison data for EV efficiency
4. **Realistic Simulation**: Staggered departures prevent simultaneous starts
5. **Complete vType Definitions**: All vehicle parameters properly defined (battery, weight, speed, etc.)

## Next Steps
You can now:
1. Run simulations with `sumo-gui CustomRoadNetwork.sumocfg`
2. Compare energy consumption across all vehicle types on each route
3. Use RSU simulation (`traCI_rsu.py`) to collect EV data
4. Analyze which vehicle type performs best on which route
5. Identify optimal charging strategies for different EV types

## Files Modified
- ✅ `CustomRoadNetwork.rou.xml` - Updated with complete vehicle coverage
- 📝 `populate_route_vehicles.py` - Script used to generate vehicles
- 📊 `R1-R7_COVERAGE_REPORT.md` - This documentation

---
**Generated**: 2024
**Status**: ✅ Complete - All routes covered with all vehicle types
