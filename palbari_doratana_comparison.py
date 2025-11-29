"""
Palbari to Doratana Route Comparison Analysis
Tests 5 different routes for charge optimization
"""

import traci
import json
from datetime import datetime

# Test vehicle IDs for Palbari to Doratana routes
TEST_VEHICLES = [
    "test_route1_direct",      # E0: Direct (24.1 km)
    "test_route2_dhormotola",  # E3 E9: Via Dhormotola (34.2 km)
    "test_route3_chachra",     # E3 E3.189 -E4: Via Dhormotola & Chachra (69.6 km)
    "test_route4_newmarket",   # E2 -E1: Via New Market (36.2 km)
    "test_route5_monihar",     # E2 -E8 E7: Via New Market & Monihar (57.0 km)
]

# Route descriptions
ROUTES = {
    "test_route1_direct": {"name": "Route 1: Direct", "path": "Palbari → Doratana", "edges": "E0", "distance_km": 2.41},
    "test_route2_dhormotola": {"name": "Route 2: Via Dhormotola", "path": "Palbari → Dhormotola → Doratana", "edges": "E3 E9", "distance_km": 3.42},
    "test_route3_chachra": {"name": "Route 3: Via Dhormotola & Chachra", "path": "Palbari → Dhormotola → Chachra → Doratana", "edges": "E3 E3.189 -E4", "distance_km": 6.96},
    "test_route4_newmarket": {"name": "Route 4: Via New Market", "path": "Palbari → New Market → Doratana", "edges": "E2 -E1", "distance_km": 3.62},
    "test_route5_monihar": {"name": "Route 5: Via New Market & Monihar", "path": "Palbari → New Market → Monihar → Doratana", "edges": "E2 -E8 E7", "distance_km": 5.70},
}

def main():
    print("=" * 90)
    print("PALBARI TO DORATANA - ROUTE COMPARISON FOR CHARGE OPTIMIZATION")
    print("=" * 90)
    print()
    
    # Start SUMO
    print("Starting SUMO simulation...")
    sumo_cmd = ["sumo-gui", "-c", "CustomRoadNetwork.sumocfg", "--start", "--quit-on-end"]
    traci.start(sumo_cmd)
    print("✓ SUMO started\n")
    
    vehicle_data = {}
    step = 0
    max_steps = 6000  # Increased for heavy traffic (200 vehicles)
    
    print(f"Running simulation for up to {max_steps} steps...")
    print("-" * 90)
    
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
                    
                    try:
                        initial_distance = traci.vehicle.getDistance(vid)
                    except:
                        initial_distance = 0.0
                    
                    vehicle_data[vid] = {
                        "route_name": ROUTES[vid]["name"],
                        "path": ROUTES[vid]["path"],
                        "edges": ROUTES[vid]["edges"],
                        "expected_distance_km": ROUTES[vid]["distance_km"],
                        "initial_battery": initial_battery,
                        "initial_distance": initial_distance,
                        "start_step": step,
                        "positions": []
                    }
                    print(f"🚗 {ROUTES[vid]['name']} started")
                    print(f"   Path: {ROUTES[vid]['path']}")
                    print(f"   Initial Battery: {initial_battery:.2f} Wh")
                    print(f"   Expected Distance: {ROUTES[vid]['distance_km']} km\n")
                
                # Update current status
                try:
                    current_battery = float(traci.vehicle.getParameter(vid, "device.battery.actualBatteryCapacity"))
                    current_distance = traci.vehicle.getDistance(vid)
                    position = traci.vehicle.getPosition(vid)
                    speed = traci.vehicle.getSpeed(vid)
                    
                    vehicle_data[vid]["current_battery"] = current_battery
                    vehicle_data[vid]["current_distance"] = current_distance
                    vehicle_data[vid]["current_step"] = step
                    vehicle_data[vid]["speed"] = speed
                    vehicle_data[vid]["positions"].append(position)
                except Exception:
                    pass
            else:
                # Check if vehicle finished
                if vid in vehicle_data and "completed" not in vehicle_data[vid]:
                    vehicle_data[vid]["completed"] = True
                    vehicle_data[vid]["end_step"] = step
                    print(f"✓ {ROUTES[vid]['name']} completed at step {step}")
        
        # Progress update
        if step % 200 == 0:
            active = sum(1 for vid in TEST_VEHICLES if vid in traci.vehicle.getIDList())
            completed = sum(1 for vid in TEST_VEHICLES if vid in vehicle_data and "completed" in vehicle_data[vid])
            print(f"⏱  Step {step}/{max_steps} | Active: {active} | Completed: {completed}/{len(TEST_VEHICLES)}")
        
        # Check if all completed
        if all(vid in vehicle_data and "completed" in vehicle_data[vid] for vid in TEST_VEHICLES):
            print("\n✓ All test vehicles completed their routes!")
            break
    
    print("-" * 90)
    print(f"\n✓ Simulation finished at step {step}\n")
    
    # Calculate results
    print("=" * 90)
    print("ROUTE COMPARISON RESULTS")
    print("=" * 90)
    print()
    
    results = []
    for vid in TEST_VEHICLES:
        if vid in vehicle_data:
            data = vehicle_data[vid]
            
            # Calculate metrics
            battery_consumed = data["initial_battery"] - data.get("current_battery", data["initial_battery"])
            battery_percent = (battery_consumed / data["initial_battery"]) * 100
            time_elapsed = data.get("current_step", step) - data["start_step"]
            
            # Calculate actual distance traveled using SUMO's odometer
            distance = data.get("current_distance", data.get("initial_distance", 0)) - data.get("initial_distance", 0)
            
            avg_speed = (distance / time_elapsed) if time_elapsed > 0 else 0
            efficiency = (battery_consumed / (distance/1000)) if distance > 0 else 0
            completed = "completed" in data
            
            results.append({
                "vehicle": vid,
                "route_name": data["route_name"],
                "path": data["path"],
                "edges": data["edges"],
                "expected_distance_km": data["expected_distance_km"],
                "actual_distance_m": distance,
                "actual_distance_km": distance / 1000,
                "battery_consumed_wh": battery_consumed,
                "battery_consumed_percent": battery_percent,
                "time_s": time_elapsed,
                "time_min": time_elapsed / 60,
                "avg_speed_ms": avg_speed,
                "avg_speed_kmh": avg_speed * 3.6,
                "efficiency_wh_per_km": efficiency,
                "initial_battery": data["initial_battery"],
                "final_battery": data.get("current_battery", data["initial_battery"]),
                "completed": completed
            })
    
    # Sort by battery consumption (most efficient first)
    results.sort(key=lambda x: x["battery_consumed_wh"])
    
    # Display results
    print("📊 RANKING BY CHARGE EFFICIENCY (Least Battery Consumption):")
    print("-" * 90)
    print(f"{'Rank':<6} {'Route':<30} {'Battery':<18} {'Distance':<15} {'Time':<12} {'Status'}")
    print(f"{'':6} {'':30} {'Used (Wh/%)':<18} {'(km)':<15} {'(min)':<12}")
    print("-" * 90)
    
    for rank, r in enumerate(results, 1):
        prefix = "🏆" if rank == 1 else "  "
        status = "✓ Done" if r["completed"] else "⚠ In Progress"
        battery_str = f"{r['battery_consumed_wh']:.2f} ({r['battery_consumed_percent']:.1f}%)"
        print(f"{prefix} {rank:<4} {r['route_name']:<30} {battery_str:<18} {r['actual_distance_km']:<15.2f} {r['time_min']:<12.1f} {status}")
    
    print("\n" + "=" * 90)
    print("DETAILED ANALYSIS")
    print("=" * 90)
    
    for rank, r in enumerate(results, 1):
        print(f"\n{'='*90}")
        print(f"#{rank} - {r['route_name']}")
        print(f"{'='*90}")
        print(f"Path:                  {r['path']}")
        print(f"Edges:                 {r['edges']}")
        print(f"Expected Distance:     {r['expected_distance_km']:.1f} km")
        print(f"Actual Distance:       {r['actual_distance_m']:.2f} m ({r['actual_distance_km']:.2f} km)")
        print(f"Initial Battery:       {r['initial_battery']:.2f} Wh")
        print(f"Final Battery:         {r['final_battery']:.2f} Wh")
        print(f"Battery Consumed:      {r['battery_consumed_wh']:.2f} Wh ({r['battery_consumed_percent']:.2f}%)")
        print(f"Travel Time:           {r['time_s']:.2f} s ({r['time_min']:.2f} min)")
        print(f"Average Speed:         {r['avg_speed_ms']:.2f} m/s ({r['avg_speed_kmh']:.2f} km/h)")
        if r['efficiency_wh_per_km'] > 0:
            print(f"Energy Efficiency:     {r['efficiency_wh_per_km']:.2f} Wh/km")
        print(f"Status:                {'Completed' if r['completed'] else 'In Progress'}")
    
    # Recommendations
    if results:
        print("\n" + "=" * 90)
        print("🎯 RECOMMENDATIONS FOR PALBARI TO DORATANA")
        print("=" * 90)
        
        best = results[0]
        worst = results[-1]
        
        print(f"\n✅ MOST CHARGE-EFFICIENT ROUTE:")
        print(f"   {best['route_name']}")
        print(f"   Path: {best['path']}")
        print(f"   Battery Consumption: {best['battery_consumed_wh']:.2f} Wh ({best['battery_consumed_percent']:.2f}%)")
        print(f"   Distance: {best['actual_distance_km']:.2f} km")
        print(f"   Travel Time: {best['time_min']:.1f} minutes")
        if best['efficiency_wh_per_km'] > 0:
            print(f"   Efficiency: {best['efficiency_wh_per_km']:.2f} Wh/km")
        
        if len(results) > 1:
            savings = worst['battery_consumed_wh'] - best['battery_consumed_wh']
            savings_pct = (savings / worst['battery_consumed_wh']) * 100 if worst['battery_consumed_wh'] > 0 else 0
            time_diff = worst['time_min'] - best['time_min']
            
            print(f"\n⚠️  LEAST EFFICIENT ROUTE:")
            print(f"   {worst['route_name']}")
            print(f"   Path: {worst['path']}")
            print(f"   Battery Consumption: {worst['battery_consumed_wh']:.2f} Wh ({worst['battery_consumed_percent']:.2f}%)")
            print(f"   Distance: {worst['actual_distance_km']:.2f} km")
            print(f"   Travel Time: {worst['time_min']:.1f} minutes")
            
            print(f"\n💡 COMPARISON:")
            print(f"   Energy Savings: {savings:.2f} Wh ({savings_pct:.1f}% more efficient)")
            print(f"   Time Difference: {time_diff:.1f} minutes")
            print(f"   \n   Recommendation: Use {best['route_name']} for optimal charge efficiency")
    
    print("\n" + "=" * 90)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_filename = f"palbari_doratana_comparison_{timestamp}.json"
    with open(json_filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"💾 Results saved to: {json_filename}")
    
    # Save CSV
    import csv
    csv_filename = f"palbari_doratana_comparison_{timestamp}.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    print(f"📊 CSV table saved to: {csv_filename}")
    
    # Save formatted table
    table_filename = f"palbari_doratana_comparison_{timestamp}.txt"
    with open(table_filename, 'w', encoding='utf-8') as f:
        f.write("=" * 120 + "\n")
        f.write("PALBARI TO DORATANA ROUTE COMPARISON - DETAILED TABLE\n")
        f.write("=" * 120 + "\n\n")
        
        # Comparison table
        f.write("COMPARISON TABLE:\n")
        f.write("-" * 120 + "\n")
        f.write(f"{'Rank':<6} {'Route Name':<35} {'Battery Used':<15} {'Distance':<12} {'Time':<10} {'Efficiency':<15} {'Status'}\n")
        f.write(f"{'':6} {'':35} {'(Wh / %)':<15} {'(km)':<12} {'(min)':<10} {'(Wh/km)':<15}\n")
        f.write("-" * 120 + "\n")
        
        for rank, r in enumerate(results, 1):
            prefix = "🏆 " if rank == 1 else "   "
            battery_str = f"{r['battery_consumed_wh']:.2f} / {r['battery_consumed_percent']:.1f}%"
            status = "✓ Completed" if r['completed'] else "⚠ In Progress"
            eff_str = f"{r['efficiency_wh_per_km']:.2f}" if r['efficiency_wh_per_km'] > 0 else "N/A"
            
            f.write(f"{prefix}{rank:<4} {r['route_name']:<35} {battery_str:<15} {r['actual_distance_km']:<12.2f} {r['time_min']:<10.2f} {eff_str:<15} {status}\n")
        
        f.write("\n\n")
        
        # Detailed breakdown
        f.write("DETAILED BREAKDOWN BY ROUTE:\n")
        f.write("=" * 120 + "\n\n")
        
        for rank, r in enumerate(results, 1):
            f.write(f"RANK #{rank} - {r['route_name']}\n")
            f.write("-" * 120 + "\n")
            f.write(f"  Route Path:              {r['path']}\n")
            f.write(f"  Edges:                   {r['edges']}\n")
            f.write(f"  Expected Distance:       {r['expected_distance_km']:.2f} km\n")
            f.write(f"  Actual Distance:         {r['actual_distance_m']:.2f} m ({r['actual_distance_km']:.2f} km)\n")
            f.write(f"  Initial Battery:         {r['initial_battery']:.2f} Wh\n")
            f.write(f"  Final Battery:           {r['final_battery']:.2f} Wh\n")
            f.write(f"  Battery Consumed:        {r['battery_consumed_wh']:.2f} Wh ({r['battery_consumed_percent']:.2f}%)\n")
            f.write(f"  Travel Time:             {r['time_s']:.2f} seconds ({r['time_min']:.2f} minutes)\n")
            f.write(f"  Average Speed:           {r['avg_speed_ms']:.2f} m/s ({r['avg_speed_kmh']:.2f} km/h)\n")
            if r['efficiency_wh_per_km'] > 0:
                f.write(f"  Energy Efficiency:       {r['efficiency_wh_per_km']:.2f} Wh/km\n")
            f.write(f"  Status:                  {'Completed' if r['completed'] else 'In Progress'}\n")
            f.write("\n")
        
        # Summary statistics
        f.write("=" * 120 + "\n")
        f.write("SUMMARY STATISTICS:\n")
        f.write("=" * 120 + "\n\n")
        
        best = results[0]
        worst = results[-1]
        
        f.write(f"Best Route:              {best['route_name']}\n")
        f.write(f"  Battery Used:          {best['battery_consumed_wh']:.2f} Wh ({best['battery_consumed_percent']:.2f}%)\n")
        f.write(f"  Travel Time:           {best['time_min']:.2f} minutes\n")
        f.write(f"  Efficiency:            {best['efficiency_wh_per_km']:.2f} Wh/km\n\n")
        
        f.write(f"Worst Route:             {worst['route_name']}\n")
        f.write(f"  Battery Used:          {worst['battery_consumed_wh']:.2f} Wh ({worst['battery_consumed_percent']:.2f}%)\n")
        f.write(f"  Travel Time:           {worst['time_min']:.2f} minutes\n")
        f.write(f"  Efficiency:            {worst['efficiency_wh_per_km']:.2f} Wh/km\n\n")
        
        savings = worst['battery_consumed_wh'] - best['battery_consumed_wh']
        savings_pct = (savings / worst['battery_consumed_wh']) * 100 if worst['battery_consumed_wh'] > 0 else 0
        time_diff = worst['time_min'] - best['time_min']
        
        f.write(f"Energy Savings:          {savings:.2f} Wh ({savings_pct:.1f}% more efficient)\n")
        f.write(f"Time Savings:            {time_diff:.2f} minutes\n")
        
    print(f"📄 Text table saved to: {table_filename}")
    
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
