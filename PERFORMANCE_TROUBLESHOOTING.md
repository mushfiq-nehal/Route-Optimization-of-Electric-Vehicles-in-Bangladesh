# 🐛 Simulation Hanging - Troubleshooting Guide

## 🔍 Problem Analysis

Your simulation is hanging/freezing, which typically happens due to:

1. **Too many vehicles (205)** overwhelming your laptop's resources
2. **RSU data collection** creating processing bottleneck  
3. **SUMO GUI** consuming extra memory and CPU
4. **Long simulation time** (800+ seconds with current settings)

---

## ⚡ Quick Fixes (Try These First)

### Fix 1: Use Optimized Simulation
I've already optimized `traCI_rsu.py` with:
- ✅ Reduced time limits (800s max, 5000 steps max)
- ✅ Faster logging (5s intervals instead of 10s)
- ✅ Better exit conditions
- ✅ Progress indicators

### Fix 2: Generate Light Traffic
```bash
python generate_light_traffic.py
```
This creates only **25 vehicles** (instead of 205) for testing:
- 5 vehicles per route
- Much faster simulation
- Same EV/Non-EV ratio
- Perfect for testing RSU functionality

### Fix 3: Use No-GUI Mode
Edit `traCI_rsu.py`, line 59, change:
```python
# FROM:
traci.start(["sumo-gui", "-c", "CustomRoadNetwork.sumocfg"])

# TO:
traci.start(["sumo", "-c", "CustomRoadNetwork.sumocfg"])
```

---

## 🧪 Diagnostic Steps

### Step 1: Test Basic SUMO Performance
```bash
python check_system.py
```
This will tell you if your laptop can handle the simulation.

### Step 2: Test Light Traffic
```bash
python generate_light_traffic.py
python traCI_rsu.py
```
Should run smoothly with only 25 vehicles.

### Step 3: Test Without RSU
Create simple test:
```bash
python quick_test.py
```

---

## 💻 System Requirements Check

### Minimum Requirements for Full Simulation (205 vehicles):
- **RAM**: 4GB+ available
- **CPU**: Dual-core 2.0GHz+
- **Disk**: Fast SSD preferred

### Signs Your Laptop Needs Optimization:
- ❌ Simulation takes >10 seconds to start
- ❌ Each simulation step takes >1 second
- ❌ System becomes unresponsive
- ❌ High memory usage (>80% RAM)

---

## 🚀 Performance Solutions

### Solution 1: Reduce Vehicle Count
```bash
# Light traffic (25 vehicles)
python generate_light_traffic.py

# Medium traffic (100 vehicles) - edit generate_traffic.py:
# Change: for i in range(1, 41) 
# To:     for i in range(1, 21)
```

### Solution 2: Optimize SUMO Settings
Edit `CustomRoadNetwork.sumocfg`:
```xml
<time>
    <step-length value="1.0"/>  <!-- Larger time steps -->
    <end value="600"/>          <!-- Shorter simulation -->
</time>
```

### Solution 3: Use Batch Mode
```bash
# No GUI, maximum speed
python -c "
import traci
traci.start(['sumo', '-c', 'CustomRoadNetwork.sumocfg', '--no-warnings'])
for i in range(100):
    traci.simulationStep()
    if i % 10 == 0:
        print(f'Step {i}: {len(traci.vehicle.getIDList())} vehicles')
traci.close()
"
```

---

## 🎯 Recommended Testing Sequence

### 1. Start with Light Traffic
```bash
python generate_light_traffic.py    # Generate 25 vehicles
python traCI_rsu.py                 # Test RSU with light load
```
**Expected**: Should complete in 2-3 minutes

### 2. If Light Traffic Works
```bash
python generate_traffic.py          # Restore full traffic
# Edit traCI_rsu.py: change sumo-gui to sumo
python traCI_rsu.py                 # Test without GUI
```

### 3. If Still Hanging
Your laptop needs a lighter configuration:
- Use light traffic permanently
- Reduce RSU count
- Increase step-length
- Use batch processing

---

## 📊 Expected Performance

### Light Traffic (25 vehicles):
- Start time: 5-10 seconds
- Total runtime: 2-3 minutes
- Memory usage: <1GB
- CPU usage: 10-30%

### Full Traffic (205 vehicles):
- Start time: 10-20 seconds
- Total runtime: 5-10 minutes
- Memory usage: 1-3GB
- CPU usage: 30-80%

### Performance Thresholds:
- **Good**: >10 simulation steps/second
- **Acceptable**: 5-10 steps/second  
- **Poor**: <5 steps/second (use light traffic)

---

## 🔧 Emergency Solutions

### If Everything Hangs:

#### Option 1: Minimal Test
```bash
# Create minimal_test.py
import traci
traci.start(['sumo', '-c', 'CustomRoadNetwork.sumocfg', '--start', '--quit-on-end'])
for i in range(10):
    traci.simulationStep()
    print(f"Step {i}: OK")
traci.close()
```

#### Option 2: Use Pre-recorded Data
If simulation won't run, use existing result files:
- `palbari_doratana_comparison_*.csv`
- Show these results in your presentation
- Explain simulation methodology theoretically

#### Option 3: Cloud/Remote Execution
- Run on friend's more powerful laptop
- Use university computer lab
- Cloud computing service (AWS/Google Cloud)

---

## 🎓 For Your Thesis Defense

### If Simulation Runs Successfully:
1. Demonstrate real-time EV tracking
2. Show RSU data collection
3. Highlight mixed traffic benefits

### If Simulation is Slow/Hangs:
1. Use light traffic for demonstration (25 vehicles)
2. Explain full simulation results from saved files
3. Discuss scalability and optimization strategies

### Backup Plan:
1. Show verification results: `python verify_traffic_mix.py`
2. Present saved CSV/JSON files
3. Screenshots of SUMO GUI
4. Explain technical architecture

---

## 📁 Quick Commands Reference

```bash
# DIAGNOSIS
python check_system.py              # Check laptop performance
python verify_traffic_mix.py        # Verify traffic composition

# LIGHT TRAFFIC TESTING  
python generate_light_traffic.py    # Create 25-vehicle test
python traCI_rsu.py                 # Run optimized simulation

# RESTORE FULL TRAFFIC
python generate_traffic.py          # Back to 205 vehicles

# EMERGENCY SIMPLE TEST
python quick_test.py                # Minimal RSU test
```

---

## 💡 Pro Tips

1. **Close other programs** (browsers, editors) before simulation
2. **Use SSD** if available for faster file I/O
3. **Monitor Task Manager** during simulation
4. **Start with light traffic** always
5. **Use non-GUI mode** for production runs
6. **Save results immediately** when simulation completes

---

## 🆘 If Nothing Works

Contact options:
1. **Use saved results** - You already have excellent data
2. **Borrow powerful laptop** - Run simulation elsewhere
3. **Simplify demo** - Focus on methodology, not live simulation
4. **Academic support** - University computer lab

**Remember**: Your research methodology is solid. Live simulation is a bonus, not a requirement for successful thesis defense.

---

**Status**: 🛠️ Troubleshooting tools ready  
**Next Step**: Run `python generate_light_traffic.py` and test  
**Backup Plan**: Use existing result files for defense