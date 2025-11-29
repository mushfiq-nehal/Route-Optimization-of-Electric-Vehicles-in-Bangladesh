"""
Quick Route Comparison - Real-time tracking with snapshot results
Captures battery consumption data even for vehicles still in transit
"""

import traci
import json
from datetime import datetime

# Test vehicle IDs
TEST_VEHICLES = [
    "test_route1", "test_route2", "test_route3", "test_route4",
    "test_route5", "test_route6", "test_route7", "test_route8"
]

# Route descriptions
ROUTES = {
    "test_route1": "E3 → E9",
    "test_route2": "E4",
    "test_route3": "E8",
    "test_route4": "E4 → E5",
    "test_route5": "E2",
    "test_route6": "E3 → E3.189",
    "test_route7": "E3 → E3.189 → E5 → E6 → E7",
    "test_route8": "E1",
}

def main():
    print("=" * 80)
    print("ROUTE COMPARISON ANALYSIS - REAL-TIME TRACKING")
    print("=" * 80)
    print()
    
    # Start SUMO
    print("Starting SUMO...")
    sumo_cmd = ["sumo-gui", "-c", "CustomRoadNetwork.sumocfg", "--start", "--quit-on-end"]
    traci.start(sumo_cmd)
    print("✓ SUMO started\n")
    
    vehicle_data = {}
    step = 0
    max_steps = 500  # Run for 500 steps (500 seconds)
    
    print(f"Running simulation for {max_steps} steps...")
    print("-" * 80)
    
    while step < max_steps:
        traci.simulationStep()
        step += 1
        
        # Track each test vehicle
        for vid in TEST_VEHICLES:
            if vid in traci.vehicle.getIDList():
                if vid not in vehicle_data:
                    # Initialize tracking
                    try:
                        initial_battery = float(traci.vehicle.getParameter(vid, "device.battery.actualBatteryCapacity"))
                    except:
                        initial_battery = 3000.0
                    
                    vehicle_data[vid] = {
                        "route": ROUTES[vid],
                        "initial_battery": initial_battery,
                        "start_step": step,
                        "positions": []
                    }
                    print(f"🚗 {vid} started | Initial Battery: {initial_battery:.2f} Wh | Route: {ROUTES[vid]}")
                
                # Update current status
                try:
                    current_battery = float(traci.vehicle.getParameter(vid, "device.battery.actualBatteryCapacity"))
                    position = traci.vehicle.getPosition(vid)
                    speed = traci.vehicle.getSpeed(vid)
                    edge = traci.vehicle.getRoadID(vid)
                    
                    vehicle_data[vid]["current_battery"] = current_battery
                    vehicle_data[vid]["current_step"] = step
                    vehicle_data[vid]["speed"] = speed
                    vehicle_data[vid]["edge"] = edge
                    vehicle_data[vid]["positions"].append(position)
                except Exception as e:
                    pass
        
        # Progress update
        if step % 100 == 0:
            active = sum(1 for vid in TEST_VEHICLES if vid in traci.vehicle.getIDList())
            print(f"⏱  Step {step}/{max_steps} | Active vehicles: {active}/{len(TEST_VEHICLES)}")
    
    print("-" * 80)
    print(f"\n✓ Simulation completed ({step} steps)\n")
    
    # Calculate results
    print("=" * 80)
    print("ROUTE COMPARISON RESULTS")
    print("=" * 80)
    print()
    
    results = []
    for vid in TEST_VEHICLES:
        if vid in vehicle_data:
            data = vehicle_data[vid]
            
            # Calculate metrics
            battery_consumed = data["initial_battery"] - data.get("current_battery", data["initial_battery"])
            battery_percent = (battery_consumed / data["initial_battery"]) * 100
            time_elapsed = data.get("current_step", step) - data["start_step"]
            
            # Calculate distance
            distance = 0.0
            positions = data.get("positions", [])
            for i in range(1, len(positions)):
                dx = positions[i][0] - positions[i-1][0]
                dy = positions[i][1] - positions[i-1][1]
                distance += (dx**2 + dy**2)**0.5
            
            avg_speed = (distance / time_elapsed) if time_elapsed > 0 else 0
            efficiency = (battery_consumed / (distance/1000)) if distance > 0 else 0
            
            results.append({
                "vehicle": vid,
                "route": data["route"],
                "battery_consumed_wh": battery_consumed,
                "battery_consumed_percent": battery_percent,
                "distance_m": distance,
                "distance_km": distance / 1000,
                "time_s": time_elapsed,
                "avg_speed_ms": avg_speed,
                "avg_speed_kmh": avg_speed * 3.6,
                "efficiency_wh_per_km": efficiency,
                "initial_battery": data["initial_battery"],
                "final_battery": data.get("current_battery", data["initial_battery"])
            })
    
    # Sort by battery consumption (most efficient first)
    results.sort(key=lambda x: x["battery_consumed_wh"])
    
    # Display results
    print("📊 RANKING BY CHARGE EFFICIENCY (Least Battery Consumption):")
    print("-" * 80)
    print(f"{'Rank':<6} {'Vehicle':<16} {'Route':<25} {'Battery':<15} {'Distance':<12} {'Time'}")
    print(f"{'':6} {'':16} {'':25} {'Used (Wh/%)':<15} {'(m)':<12} {'(s)'}")
    print("-" * 80)
    
    for rank, r in enumerate(results, 1):
        prefix = "🏆" if rank == 1 else "  "
        battery_str = f"{r['battery_consumed_wh']:.2f} ({r['battery_consumed_percent']:.1f}%)"
        print(f"{prefix} {rank:<4} {r['vehicle']:<16} {r['route']:<25} {battery_str:<15} {r['distance_m']:<12.2f} {r['time_s']:.0f}")
    
    print("\n" + "=" * 80)
    print("DETAILED ANALYSIS")
    print("=" * 80)
    
    for rank, r in enumerate(results, 1):
        print(f"\n#{rank} - {r['vehicle']} ({r['route']})")
        print(f"  ├─ Initial Battery:    {r['initial_battery']:.2f} Wh")
        print(f"  ├─ Final Battery:      {r['final_battery']:.2f} Wh")
        print(f"  ├─ Battery Consumed:   {r['battery_consumed_wh']:.2f} Wh ({r['battery_consumed_percent']:.2f}%)")
        print(f"  ├─ Distance Traveled:  {r['distance_m']:.2f} m ({r['distance_km']:.3f} km)")
        print(f"  ├─ Travel Time:        {r['time_s']:.2f} s ({r['time_s']/60:.2f} min)")
        print(f"  ├─ Average Speed:      {r['avg_speed_ms']:.2f} m/s ({r['avg_speed_kmh']:.2f} km/h)")
        if r['efficiency_wh_per_km'] > 0:
            print(f"  └─ Energy Efficiency:  {r['efficiency_wh_per_km']:.2f} Wh/km")
        else:
            print(f"  └─ Energy Efficiency:  N/A (insufficient distance)")
    
    # Recommendations
    if results:
        print("\n" + "=" * 80)
        print("🎯 RECOMMENDATIONS")
        print("=" * 80)
        
        best = results[0]
        worst = results[-1]
        
        print(f"\n✅ MOST CHARGE-EFFICIENT ROUTE:")
        print(f"   {best['vehicle']}: {best['route']}")
        print(f"   Battery Consumption: {best['battery_consumed_wh']:.2f} Wh ({best['battery_consumed_percent']:.2f}%)")
        if best['efficiency_wh_per_km'] > 0:
            print(f"   Efficiency: {best['efficiency_wh_per_km']:.2f} Wh/km")
        
        if len(results) > 1:
            savings = worst['battery_consumed_wh'] - best['battery_consumed_wh']
            savings_pct = (savings / worst['battery_consumed_wh']) * 100 if worst['battery_consumed_wh'] > 0 else 0
            
            print(f"\n⚠️  LEAST EFFICIENT ROUTE:")
            print(f"   {worst['vehicle']}: {worst['route']}")
            print(f"   Battery Consumption: {worst['battery_consumed_wh']:.2f} Wh ({worst['battery_consumed_percent']:.2f}%)")
            print(f"   \n   💡 Energy Savings: Choosing best route saves {savings:.2f} Wh ({savings_pct:.1f}% more efficient)")
    
    print("\n" + "=" * 80)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"route_comparison_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"💾 Results saved to: {filename}")
    
    traci.close()
    print("\n✓ Analysis complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        try:
            traci.close()
        except:
            pass
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            traci.close()
        except:
            pass
