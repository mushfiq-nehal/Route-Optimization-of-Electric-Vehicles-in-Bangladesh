"""
RSU-based TraCI Implementation
Vehicles communicate with RSUs which then forward data to the server
"""

import os
import time
import requests
import traci
from rsu import RSUNetwork

# Constants
SERVER_URL = "http://127.0.0.1:8000"  # Change to your server IP:port if remote
RSU_BATCH_SIZE = 100  # Number of records each RSU sends per batch
LOG_INTERVAL = 10  # Log data every 10 seconds
RSU_COVERAGE_RADIUS = 500.0  # RSU coverage radius in meters

# URL to clear data from the FastAPI server
CLEAR_DATA_URL = f"{SERVER_URL}/clear_data"

# Initialize RSU Network
rsu_network = RSUNetwork(SERVER_URL)

def setup_rsu_network():
    """
    Setup RSU network based on road network junctions
    Place RSUs at strategic locations (intersections)
    """
    print("Setting up RSU Network...")
    
    # Define RSU positions based on the road network
    # These positions correspond to major junctions in the CustomRoadNetwork
    rsu_positions = {
        'RSU_Chachra': (-165.47, -199.59),
        'RSU_Dhormotola': (-194.59, 27.16),
        'RSU_Doratana': (-44.04, 49.98),
        'RSU_Monihar': (79.98, -8.38),
        'RSU_Muroli': (223.72, -213.15),
        'RSU_NewMarket': (2.93, 170.72),
        'RSU_Palbari': (-218.70, 214.90),
    }
    
    # Add RSUs to the network
    for rsu_id, position in rsu_positions.items():
        rsu_network.add_rsu(rsu_id, position, RSU_COVERAGE_RADIUS)
    
    print(f"RSU Network setup complete with {len(rsu_positions)} RSUs\n")
    return rsu_network

def clear_data_before_run():
    """Clear data from the server before starting the simulation"""
    try:
        response = requests.delete(CLEAR_DATA_URL)
        response.raise_for_status()
        print("Data cleared successfully before the run.\n")
    except requests.exceptions.RequestException as e:
        print(f"Error clearing data: {e}\n")

def start_simulation():
    """Start SUMO connection"""
    traci.start(["sumo-gui", "-c", "CustomRoadNetwork.sumocfg"])
    print("SUMO simulation started\n")

def collect_vehicle_data_via_rsu(sim_time):
    """
    Collect vehicle data and route it through the RSU network
    
    Args:
        sim_time: Current simulation time
    """
    vehicle_ids = traci.vehicle.getIDList()
    
    if not vehicle_ids:
        return
    
    print(f"[Sim Time: {sim_time}s] Collecting data from {len(vehicle_ids)} vehicles...")
    
    for vid in vehicle_ids:
        try:
            # Get vehicle position
            position = traci.vehicle.getPosition(vid)
            
            # Get vehicle speed
            speed = traci.vehicle.getSpeed(vid)
            if traci.vehicle.getWaitingTime(vid) > 0:
                speed = 0.0
            
            # Get battery parameters
            battery_capacity = float(traci.vehicle.getParameter(vid, "device.battery.capacity"))
            battery_charge = float(traci.vehicle.getParameter(vid, "device.battery.actualBatteryCapacity"))
            
            # Calculate battery percentage
            battery_percentage = (battery_charge / battery_capacity * 100.0) if battery_capacity > 0 else 0.0
            
            # Prepare vehicle data
            vehicle_data = {
                'vehicle_id': vid,
                'speed': speed,
                'battery_charge': battery_charge,
                'battery_capacity': battery_capacity,
                'battery_percentage': battery_percentage,
                'sim_time': sim_time,
                'position': position
            }
            
            # Send data to nearest RSU
            rsu_network.collect_vehicle_data(vid, position, vehicle_data)
            
        except Exception as e:
            print(f"Error collecting data for vehicle {vid}: {e}")
    
    # Send data from all RSUs to server
    rsu_network.send_all_data(RSU_BATCH_SIZE)

def run_simulation():
    """Run simulation and collect data via RSU network"""
    last_log_time = 0
    step_count = 0
    status_interval = 100  # Print RSU status every 100 steps
    vehicles_seen = set()
    total_data_collected = 0
    min_steps = 500  # Run for at least 500 steps to ensure data collection
    
    print("Starting simulation loop...\n")
    
    while traci.simulation.getMinExpectedNumber() > 0 or step_count < min_steps:
        try:
            traci.simulationStep()
            sim_time = traci.simulation.getTime()
            step_count += 1
            
            # Track all vehicles seen during simulation
            current_vehicles = traci.vehicle.getIDList()
            if current_vehicles:
                new_vehicles = set(current_vehicles) - vehicles_seen
                if new_vehicles:
                    print(f"[Step {step_count}] New vehicles appeared: {len(new_vehicles)}")
                vehicles_seen.update(current_vehicles)
            
            # Log data at regular intervals
            if sim_time - last_log_time >= LOG_INTERVAL:
                if current_vehicles:
                    collect_vehicle_data_via_rsu(sim_time)
                    total_data_collected += len(current_vehicles)
                    print(f"  Active vehicles: {len(current_vehicles)}, Total seen: {len(vehicles_seen)}, Data points: {total_data_collected}")
                else:
                    print(f"[Step {step_count}, Time: {sim_time}s] No active vehicles (Total seen: {len(vehicles_seen)})")
                last_log_time = sim_time
            
            # Print RSU network status periodically
            if step_count % status_interval == 0:
                rsu_network.print_network_status()
            
            # Break if we've seen vehicles but none are left and passed minimum steps
            if step_count > min_steps and len(vehicles_seen) > 0 and len(current_vehicles) == 0:
                print(f"\n[Step {step_count}] All vehicles completed their routes.")
                break
                
        except Exception as e:
            print(f"Error during simulation step: {e}")
            import traceback
            traceback.print_exc()
    
    # Final data transmission
    print("\nSimulation ended. Sending remaining data...")
    rsu_network.send_all_data(RSU_BATCH_SIZE)
    
    # Print final RSU network status
    print("\nFinal RSU Network Status:")
    rsu_network.print_network_status()
    
    # Print simulation summary
    print("\n" + "="*60)
    print("SIMULATION SUMMARY")
    print("="*60)
    print(f"Total Steps: {step_count}")
    print(f"Total Vehicles Seen: {len(vehicles_seen)}")
    print(f"Total Data Points Collected: {total_data_collected}")
    print("="*60)
    
    # Print final statistics
    try:
        response = requests.get(f"{SERVER_URL}/rsu_stats")
        if response.status_code == 200:
            stats = response.json()
            print("\n" + "="*60)
            print("SERVER-SIDE RSU STATISTICS")
            print("="*60)
            for rsu_stat in stats.get('rsu_stats', []):
                print(f"RSU: {rsu_stat['rsu_id']}")
                print(f"  Total Vehicles Served: {rsu_stat['total_vehicles']}")
                print(f"  Total Records Sent: {rsu_stat['total_records']}")
                print(f"  Last Update: {rsu_stat['last_update']}")
            print("="*60 + "\n")
    except Exception as e:
        print(f"Error fetching RSU statistics: {e}")

def main():
    """Main function"""
    try:
        print("="*60)
        print("RSU-BASED VEHICLE-TO-INFRASTRUCTURE COMMUNICATION SYSTEM")
        print("="*60 + "\n")
        
        # Setup RSU network
        setup_rsu_network()
        
        # Clear old data from the server
        clear_data_before_run()
        
        # Start the simulation
        start_simulation()
        
        # Run the simulation with RSU-based data collection
        run_simulation()
        
        print("\nSimulation completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        traci.close()
        print("SUMO connection closed.")

if __name__ == "__main__":
    main()
