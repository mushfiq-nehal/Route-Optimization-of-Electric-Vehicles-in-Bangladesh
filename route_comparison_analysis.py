"""
Route Comparison Analysis for EV Charge Optimization
Tracks test vehicles across different routes to determine the most charge-efficient path
"""

import traci
import time
import json
from datetime import datetime

# Test vehicle IDs for comparison
TEST_VEHICLES = [
    "test_route1",  # E3 -> E9
    "test_route2",  # E4
    "test_route3",  # E8
    "test_route4",  # E4 -> E5
    "test_route5",  # E2
    "test_route6",  # E3 -> E3.189
    "test_route7",  # E3 -> E3.189 -> E5 -> E6 -> E7
    "test_route8",  # E1
]

# Route descriptions
ROUTE_INFO = {
    "test_route1": {"name": "Route 1", "edges": "E3 → E9"},
    "test_route2": {"name": "Route 2", "edges": "E4"},
    "test_route3": {"name": "Route 3", "edges": "E8"},
    "test_route4": {"name": "Route 4", "edges": "E4 → E5"},
    "test_route5": {"name": "Route 5", "edges": "E2"},
    "test_route6": {"name": "Route 6", "edges": "E3 → E3.189"},
    "test_route7": {"name": "Route 7", "edges": "E3 → E3.189 → E5 → E6 → E7"},
    "test_route8": {"name": "Route 8", "edges": "E1"},
}

class RouteComparison:
    def __init__(self):
        self.vehicle_data = {}
        self.step_count = 0
        self.start_time = None
        
        # Initialize tracking for each test vehicle
        for vid in TEST_VEHICLES:
            self.vehicle_data[vid] = {
                "route": ROUTE_INFO[vid]["name"],
                "edges": ROUTE_INFO[vid]["edges"],
                "initial_battery": None,
                "final_battery": None,
                "battery_consumed_wh": None,
                "battery_consumed_percent": None,
                "distance_traveled": 0.0,
                "travel_time": None,
                "avg_speed": None,
                "max_speed": 0.0,
                "min_speed": float('inf'),
                "completed": False,
                "start_time": None,
                "end_time": None,
                "efficiency_wh_per_km": None,
                "positions": []
            }
    
    def connect_sumo(self):
        """Connect to SUMO simulation"""
        print("Connecting to SUMO...")
        sumo_binary = "sumo-gui"  # Use "sumo" for non-GUI mode
        sumo_cmd = [
            sumo_binary,
            "-c", "CustomRoadNetwork.sumocfg",
            "--start",
            "--quit-on-end"
        ]
        traci.start(sumo_cmd)
        print("✓ Connected to SUMO\n")
    
    def track_vehicle(self, vid):
        """Track individual vehicle metrics"""
        try:
            if vid not in traci.vehicle.getIDList():
                return
            
            data = self.vehicle_data[vid]
            
            # Record start time
            if data["start_time"] is None:
                data["start_time"] = self.step_count
                # Get initial battery
                try:
                    data["initial_battery"] = traci.vehicle.getParameter(vid, "device.battery.actualBatteryCapacity")
                    data["initial_battery"] = float(data["initial_battery"])
                except:
                    data["initial_battery"] = 3000.0  # Default for Easybike_ER-02B
                print(f"🚗 {vid} started - Initial Battery: {data['initial_battery']:.2f} Wh")
            
            # Track position and speed
            position = traci.vehicle.getPosition(vid)
            speed = traci.vehicle.getSpeed(vid)
            
            data["positions"].append(position)
            data["max_speed"] = max(data["max_speed"], speed)
            if speed > 0:
                data["min_speed"] = min(data["min_speed"], speed)
            
            # Calculate distance (incremental)
            if len(data["positions"]) > 1:
                prev_pos = data["positions"][-2]
                curr_pos = data["positions"][-1]
                dist = ((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)**0.5
                data["distance_traveled"] += dist
            
        except traci.exceptions.TraCIException:
            pass
    
    def check_completion(self, vid):
        """Check if vehicle has completed its route"""
        data = self.vehicle_data[vid]
        
        if data["completed"]:
            return
        
        # Check if vehicle is still in simulation
        if vid in traci.vehicle.getIDList():
            # Update current battery level
            try:
                current_battery = float(traci.vehicle.getParameter(vid, "device.battery.actualBatteryCapacity"))
                data["final_battery"] = current_battery
            except:
                pass
        else:
            # Vehicle has left the simulation
            if data["start_time"] is not None:
                data["completed"] = True
                data["end_time"] = self.step_count
                
                # Calculate metrics
                if data["final_battery"] is None:
                    data["final_battery"] = data["initial_battery"]
                
                data["battery_consumed_wh"] = data["initial_battery"] - data["final_battery"]
                data["battery_consumed_percent"] = (data["battery_consumed_wh"] / data["initial_battery"]) * 100
                data["travel_time"] = data["end_time"] - data["start_time"]
                data["avg_speed"] = (data["distance_traveled"] / data["travel_time"]) if data["travel_time"] > 0 else 0
                
                if data["distance_traveled"] > 0:
                    data["efficiency_wh_per_km"] = (data["battery_consumed_wh"] / data["distance_traveled"]) * 1000
                
                print(f"✓ {vid} completed!")
                print(f"   Battery Used: {data['battery_consumed_wh']:.2f} Wh ({data['battery_consumed_percent']:.2f}%)")
                print(f"   Distance: {data['distance_traveled']:.2f} m")
                print(f"   Time: {data['travel_time']:.2f} s")
                print(f"   Avg Speed: {data['avg_speed']:.2f} m/s")
                if data["efficiency_wh_per_km"]:
                    print(f"   Efficiency: {data['efficiency_wh_per_km']:.2f} Wh/km\n")
    
    def run_simulation(self, max_steps=1000):
        """Run the simulation and track all test vehicles"""
        print("=" * 70)
        print("ROUTE COMPARISON ANALYSIS - EV CHARGE OPTIMIZATION")
        print("=" * 70)
        print(f"Tracking {len(TEST_VEHICLES)} test vehicles across different routes\n")
        
        self.start_time = time.time()
        
        while self.step_count < max_steps:
            traci.simulationStep()
            self.step_count += 1
            
            # Track all test vehicles
            for vid in TEST_VEHICLES:
                self.track_vehicle(vid)
                self.check_completion(vid)
            
            # Check if all vehicles completed
            all_completed = all(data["completed"] for data in self.vehicle_data.values())
            if all_completed:
                print("\n✓ All test vehicles completed their routes!")
                break
            
            # Progress indicator every 50 steps
            if self.step_count % 50 == 0:
                active = sum(1 for data in self.vehicle_data.values() if not data["completed"])
                print(f"⏱ Step {self.step_count} - Active vehicles: {active}/{len(TEST_VEHICLES)}")
        
        traci.close()
        print(f"\nSimulation completed in {time.time() - self.start_time:.2f} seconds\n")
    
    def analyze_results(self):
        """Analyze and compare route performance"""
        print("=" * 70)
        print("ROUTE COMPARISON RESULTS")
        print("=" * 70)
        print()
        
        # Filter only completed routes
        completed_routes = [(vid, data) for vid, data in self.vehicle_data.items() if data["completed"]]
        
        if not completed_routes:
            print("⚠️  No vehicles completed their routes in the simulation time.")
            print("   Try increasing max_steps or checking route configuration.")
            return
        
        # Sort by battery consumption (ascending = most efficient)
        sorted_routes = sorted(
            completed_routes,
            key=lambda x: x[1]["battery_consumed_wh"]
        )
        
        print("📊 RANKING BY ENERGY EFFICIENCY (Most Efficient First):")
        print("-" * 70)
        print(f"{'Rank':<6} {'Vehicle':<15} {'Route':<10} {'Battery':<12} {'Distance':<12} {'Time':<10} {'Efficiency'}")
        print(f"{'':6} {'':15} {'':10} {'Used (Wh)':<12} {'(m)':<12} {'(s)':<10} {'(Wh/km)'}")
        print("-" * 70)
        
        for rank, (vid, data) in enumerate(sorted_routes, 1):
            battery_str = f"{data['battery_consumed_wh']:.2f}"
            dist_str = f"{data['distance_traveled']:.2f}"
            time_str = f"{data['travel_time']:.2f}"
            eff_str = f"{data['efficiency_wh_per_km']:.2f}" if data['efficiency_wh_per_km'] else "N/A"
            
            # Highlight best route
            prefix = "🏆 " if rank == 1 else "   "
            print(f"{prefix}{rank:<4} {vid:<15} {data['route']:<10} {battery_str:<12} {dist_str:<12} {time_str:<10} {eff_str}")
        
        print()
        print("=" * 70)
        print("DETAILED COMPARISON TABLE")
        print("=" * 70)
        print()
        
        for vid, data in sorted_routes:
            print(f"\n{data['route']} ({vid})")
            print(f"  Path: {data['edges']}")
            print(f"  ├─ Initial Battery: {data['initial_battery']:.2f} Wh")
            print(f"  ├─ Final Battery: {data['final_battery']:.2f} Wh")
            print(f"  ├─ Battery Consumed: {data['battery_consumed_wh']:.2f} Wh ({data['battery_consumed_percent']:.2f}%)")
            print(f"  ├─ Distance: {data['distance_traveled']:.2f} m ({data['distance_traveled']/1000:.3f} km)")
            print(f"  ├─ Travel Time: {data['travel_time']:.2f} s ({data['travel_time']/60:.2f} min)")
            print(f"  ├─ Avg Speed: {data['avg_speed']:.2f} m/s ({data['avg_speed']*3.6:.2f} km/h)")
            print(f"  ├─ Max Speed: {data['max_speed']:.2f} m/s ({data['max_speed']*3.6:.2f} km/h)")
            if data['efficiency_wh_per_km']:
                print(f"  └─ Energy Efficiency: {data['efficiency_wh_per_km']:.2f} Wh/km")
        
        print("\n" + "=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)
        
        # Find best route
        best_route = sorted_routes[0]
        worst_route = sorted_routes[-1] if len(sorted_routes) > 1 else None
        
        print(f"\n✅ MOST CHARGE-EFFICIENT ROUTE: {best_route[1]['route']}")
        print(f"   Path: {best_route[1]['edges']}")
        print(f"   Battery Consumption: {best_route[1]['battery_consumed_wh']:.2f} Wh")
        if best_route[1]['efficiency_wh_per_km']:
            print(f"   Energy Efficiency: {best_route[1]['efficiency_wh_per_km']:.2f} Wh/km")
        
        if worst_route and worst_route != best_route:
            savings = worst_route[1]['battery_consumed_wh'] - best_route[1]['battery_consumed_wh']
            savings_pct = (savings / worst_route[1]['battery_consumed_wh']) * 100
            print(f"\n⚠️  LEAST EFFICIENT ROUTE: {worst_route[1]['route']}")
            print(f"   Battery Consumption: {worst_route[1]['battery_consumed_wh']:.2f} Wh")
            print(f"   Energy Savings vs Best Route: {savings:.2f} Wh ({savings_pct:.1f}% more efficient)")
        
        print("\n" + "=" * 70)
    
    def save_results(self, filename=None):
        """Save results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"route_comparison_{timestamp}.json"
        
        # Prepare data for JSON (remove non-serializable items)
        export_data = {}
        for vid, data in self.vehicle_data.items():
            export_data[vid] = {k: v for k, v in data.items() if k != "positions"}
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")


def main():
    """Main execution function"""
    analyzer = RouteComparison()
    
    try:
        # Connect to SUMO
        analyzer.connect_sumo()
        
        # Run simulation
        analyzer.run_simulation(max_steps=2000)
        
        # Analyze and display results
        analyzer.analyze_results()
        
        # Save results
        analyzer.save_results()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation interrupted by user")
        traci.close()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            traci.close()
        except:
            pass


if __name__ == "__main__":
    main()
