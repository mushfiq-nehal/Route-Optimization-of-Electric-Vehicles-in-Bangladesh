"""
Longer test to see battery discharge over time
"""
import traci
from rsu import RSUNetwork
import requests
import pandas as pd
import sqlite3

SERVER_URL = "http://127.0.0.1:8000"
RSU_COVERAGE_RADIUS = 500.0

def setup_rsu_network():
    """Setup RSU network"""
    rsu_network = RSUNetwork(SERVER_URL)
    
    rsu_positions = {
        'RSU_Chachra': (-165.47, -199.59),
        'RSU_Dhormotola': (-194.59, 27.16),
        'RSU_Doratana': (-44.04, 49.98),
        'RSU_Monihar': (79.98, -8.38),
        'RSU_Muroli': (223.72, -213.15),
        'RSU_NewMarket': (2.93, 170.72),
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
    print("EXTENDED TEST - Monitoring Battery Discharge")
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
    print("\n Starting SUMO for 500 steps...")
    traci.start(["sumo", "-c", "CustomRoadNetwork.sumocfg", "--no-warnings"])
    
    # Run for 500 steps
    total_vehicles_seen = set()
    
    try:
        for step in range(500):
            traci.simulationStep()
            
            vehicle_ids = traci.vehicle.getIDList()
            if vehicle_ids:
                total_vehicles_seen.update(vehicle_ids)
            
            # Collect data every 10 steps
            if step % 10 == 0:
                sim_time = traci.simulation.getTime()
                count = collect_data(rsu_network, sim_time)
                if count > 0 and step % 50 == 0:
                    print(f"Step {step}: {count} vehicles active")
                
                # Send to server every 100 steps
                if step % 100 == 0 and step > 0:
                    sent = rsu_network.send_all_data()
        
        # Send final data
        final_sent = rsu_network.send_all_data()
        
    finally:
        traci.close()
    
    print("\n" + "="*60)
    print("ANALYZING BATTERY DISCHARGE")
    print("="*60)
    
    # Read from database and analyze
    conn = sqlite3.connect('telemetry.db')
    df = pd.read_sql_query("""
        SELECT vehicle_id, sim_time, battery_charge, battery_capacity, battery_percentage
        FROM rsu_vehicle_logs
        ORDER BY vehicle_id, sim_time
    """, conn)
    conn.close()
    
    # Show battery discharge for first few vehicles
    print("\nBattery Discharge Over Time (Sample Vehicles):")
    print("-" * 80)
    
    for vid in df['vehicle_id'].unique()[:3]:
        vehicle_data = df[df['vehicle_id'] == vid].sort_values('sim_time')
        if len(vehicle_data) > 1:
            first = vehicle_data.iloc[0]
            last = vehicle_data.iloc[-1]
            discharge = first['battery_charge'] - last['battery_charge']
            pct_discharge = first['battery_percentage'] - last['battery_percentage']
            
            print(f"\n{vid}:")
            print(f"  Capacity: {first['battery_capacity']:.0f} Wh")
            print(f"  Start: {first['battery_charge']:.2f} Wh ({first['battery_percentage']:.2f}%) at {first['sim_time']:.0f}s")
            print(f"  End:   {last['battery_charge']:.2f} Wh ({last['battery_percentage']:.2f}%) at {last['sim_time']:.0f}s")
            print(f"  Discharged: {discharge:.2f} Wh ({pct_discharge:.2f}%)")
    
    print("\n" + "="*60)
    print("✓ Extended test completed!")
    print("="*60)

if __name__ == "__main__":
    main()
