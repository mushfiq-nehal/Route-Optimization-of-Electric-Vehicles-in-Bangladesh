"""
Quick Test Script - Optimized for speed and debugging hangs
"""
import traci
from rsu import RSUNetwork
import requests

SERVER_URL = "http://127.0.0.1:8000"
RSU_COVERAGE_RADIUS = 500.0

def is_electric_vehicle(vehicle_id):
    """Check if vehicle is EV"""
    try:
        has_battery = traci.vehicle.getParameter(vehicle_id, "has.battery.device")
        return has_battery and has_battery.lower() == "true"
    except:
        return False

def setup_rsu_network():
    """Setup minimal RSU network"""
    rsu_network = RSUNetwork(SERVER_URL)
    
    # Only 3 RSUs for faster testing
    rsu_positions = {
        'RSU_Palbari': (-218.70, 214.90),
        'RSU_Doratana': (-44.04, 49.98),
        'RSU_NewMarket': (2.93, 170.72),
    }
        'RSU_Palbari': (-218.70, 214.90),
    }
    
    for rsu_id, position in rsu_positions.items():
        rsu_network.add_rsu(rsu_id, position, RSU_COVERAGE_RADIUS)
    
    return rsu_network

def collect_data(rsu_network, sim_time):
    """Collect vehicle data and send via RSU"""
    vehicle_ids = traci.vehicle.getIDList()
    
    if not vehicle_ids:
        return 0
    
    for vid in vehicle_ids:
        try:
            position = traci.vehicle.getPosition(vid)
            speed = traci.vehicle.getSpeed(vid)
            battery_capacity = float(traci.vehicle.getParameter(vid, "device.battery.capacity"))
            battery_charge = float(traci.vehicle.getParameter(vid, "device.battery.actualBatteryCapacity"))
            
            # Calculate battery percentage
            battery_percentage = (battery_charge / battery_capacity * 100.0) if battery_capacity > 0 else 0.0
            
            vehicle_data = {
                'vehicle_id': vid,
                'speed': speed,
                'battery_charge': battery_charge,
                'battery_capacity': battery_capacity,
                'battery_percentage': battery_percentage,
                'sim_time': sim_time,
                'position': position
            }
            
            rsu_network.collect_vehicle_data(vid, position, vehicle_data)
        except Exception as e:
            print(f"Error collecting data for {vid}: {e}")
    
    return len(vehicle_ids)

def main():
    print("="*60)
    print("QUICK TEST - Non-GUI mode")
    print("="*60)
    
    # Setup
    rsu_network = setup_rsu_network()
    print(f"✓ RSU Network ready with {len(rsu_network.rsus)} RSUs")
    
    # Clear old data
    try:
        requests.delete(f"{SERVER_URL}/clear_data")
        print("✓ Cleared old data from server")
    except:
        print("⚠ Could not clear old data (server may not be running)")
    
    # Start SUMO in non-GUI mode
    print("\n Starting SUMO...")
    traci.start(["sumo", "-c", "CustomRoadNetwork.sumocfg", "--no-warnings"])
    
    # Run for 100 steps
    total_vehicles_seen = set()
    total_data_points = 0
    
    try:
        for step in range(100):
            traci.simulationStep()
            
            vehicle_ids = traci.vehicle.getIDList()
            if vehicle_ids:
                total_vehicles_seen.update(vehicle_ids)
            
            # Collect data every 10 steps
            if step % 10 == 0:
                sim_time = traci.simulation.getTime()
                count = collect_data(rsu_network, sim_time)
                if count > 0:
                    total_data_points += count
                    print(f"Step {step}: {count} vehicles, Total seen: {len(total_vehicles_seen)}")
                
                # Send to server every 50 steps
                if step % 50 == 0 and step > 0:
                    sent = rsu_network.send_all_data()
                    print(f"  → Sent {sent} records to server")
        
        # Send final data
        final_sent = rsu_network.send_all_data()
        print(f"\n✓ Final batch: {final_sent} records sent")
        
    finally:
        traci.close()
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Total unique vehicles seen: {len(total_vehicles_seen)}")
    print(f"Total data points collected: {total_data_points}")
    
    # Check server
    try:
        response = requests.get(f"{SERVER_URL}/rsu_stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"\nServer received data from {len(stats.get('rsu_stats', []))} RSUs")
            for rsu_stat in stats.get('rsu_stats', []):
                print(f"  {rsu_stat['rsu_id']}: {rsu_stat['total_records']} records")
    except Exception as e:
        print(f"\nCould not fetch server stats: {e}")
    
    print("\n✓ Test completed! You can now run extract_data.py to get the results.")
    print("="*60)

if __name__ == "__main__":
    main()
