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
RSU_BATCH_SIZE = 50  # Number of records each RSU sends per batch
LOG_INTERVAL = 5  # Log data every 5 seconds (reduced for faster feedback)
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

def is_electric_vehicle(vehicle_id):
    """
    Check if a vehicle is an electric vehicle by checking for battery device
    
    Args:
        vehicle_id: ID of the vehicle to check
        
    Returns:
        True if vehicle has battery device (is EV), False otherwise
    """
    try:
        # Check if vehicle has battery device flag
        has_battery = traci.vehicle.getParameter(vehicle_id, "has.battery.device")
        if has_battery and has_battery.lower() == "true":
            return True
        else:
            return False
    except:
        # If we can't get battery parameters, it's not an EV
        return False

def collect_vehicle_data_via_rsu(sim_time):
    """
    Collect vehicle data and route it through the RSU network
    Only collects data from Electric Vehicles (EVs)
    
    Args:
        sim_time: Current simulation time
    """
    vehicle_ids = traci.vehicle.getIDList()
    
    if not vehicle_ids:
        return
    
    # Filter to only EVs
    ev_ids = [vid for vid in vehicle_ids if is_electric_vehicle(vid)]
    non_ev_count = len(vehicle_ids) - len(ev_ids)
    
    print(f"[Sim Time: {sim_time}s] Active vehicles: {len(vehicle_ids)} (EVs: {len(ev_ids)}, Non-EVs: {non_ev_count})")
    
    if not ev_ids:
        print("  No EVs active at this time.")
        return
    
    print(f"  Collecting data from {len(ev_ids)} EVs...")
    
    for vid in ev_ids:
        try:
            # Get vehicle position
            position = traci.vehicle.getPosition(vid)
            
            # Get vehicle type
            v_type = traci.vehicle.getTypeID(vid)
            
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
                'vehicle_type': v_type,
                'speed': speed,
                'battery_charge': battery_charge,
                'battery_capacity': battery_capacity,
                'battery_percentage': battery_percentage,
                'sim_time': sim_time,
                'position': position
            }
            
            # Send data to nearest RSU (only EVs)
            rsu_network.collect_vehicle_data(vid, position, vehicle_data, is_ev=True)
            
        except Exception as e:
            print(f"Error collecting data for EV {vid}: {e}")
    
    # Send data from all RSUs to server
    rsu_network.send_all_data(RSU_BATCH_SIZE)

def run_simulation():
    """Run simulation and collect data via RSU network"""
    last_log_time = 0
    step_count = 0
    sim_time = 0  # Initialize sim_time
    status_interval = 50  # Print RSU status every 50 steps (more frequent)
    all_vehicles_seen = set()
    ev_vehicles_seen = set()
    total_ev_data_collected = 0
    min_steps = 100  # Reduced for faster testing
    max_sim_time = 200  # Reduced for light traffic (3+ minutes)
    max_steps = 1000  # Maximum steps to prevent infinite loops
    
    print("Starting simulation loop...\n")
    print("⚡ RSU Network configured to collect data ONLY from Electric Vehicles\n")
    
    while (traci.simulation.getMinExpectedNumber() > 0 or step_count < min_steps) and sim_time < max_sim_time and step_count < max_steps:
        try:
            traci.simulationStep()
            sim_time = traci.simulation.getTime()
            step_count += 1
            
            # Early logging to debug vehicle spawning
            if step_count <= 20 or step_count % 50 == 0:
                current_vehicles = traci.vehicle.getIDList()
                expected_vehicles = traci.simulation.getMinExpectedNumber()
                print(f"[Step {step_count:3d}] Time: {sim_time:5.1f}s | Active: {len(current_vehicles):2d} | Expected: {expected_vehicles:2d}")
                
                if current_vehicles and step_count <= 20:
                    print(f"              Vehicles: {list(current_vehicles)}")
            
            # Track all vehicles seen during simulation
            current_vehicles = traci.vehicle.getIDList()
            if current_vehicles:
                new_vehicles = set(current_vehicles) - all_vehicles_seen
                if new_vehicles:
                    # Check which are EVs
                    new_evs = [vid for vid in new_vehicles if is_electric_vehicle(vid)]
                    new_non_evs = len(new_vehicles) - len(new_evs)
                    if new_evs:
                        print(f"[Step {step_count}] New vehicles appeared: {len(new_vehicles)} (EVs: {len(new_evs)}, Non-EVs: {new_non_evs})")
                        ev_vehicles_seen.update(new_evs)
                    else:
                        print(f"[Step {step_count}] New non-EV vehicles appeared: {len(new_vehicles)}")
                all_vehicles_seen.update(current_vehicles)
            
            # Log data at regular intervals
            if sim_time - last_log_time >= LOG_INTERVAL:
                if current_vehicles:
                    collect_vehicle_data_via_rsu(sim_time)
                    current_evs = [vid for vid in current_vehicles if is_electric_vehicle(vid)]
                    total_ev_data_collected += len(current_evs)
                    print(f"  📊 Total seen: {len(all_vehicles_seen)} vehicles ({len(ev_vehicles_seen)} EVs), EV data points collected: {total_ev_data_collected}")
                else:
                    print(f"[Step {step_count}, Time: {sim_time}s] No active vehicles (Total seen: {len(all_vehicles_seen)}, EVs: {len(ev_vehicles_seen)})")
                last_log_time = sim_time
            
            # Print RSU network status periodically
            if step_count % status_interval == 0:
                rsu_network.print_network_status()
                print(f"Progress: Step {step_count}/{max_steps}, Time {sim_time:.1f}s/{max_sim_time}s")
            
            # Break if we've seen vehicles but none are left and passed minimum steps
            if step_count > min_steps and len(all_vehicles_seen) > 0 and len(current_vehicles) == 0:
                print(f"\n[Step {step_count}] All vehicles completed their routes. Ending simulation.")
                break
                
        except Exception as e:
            print(f"Error during simulation step: {e}")
            import traceback
            traceback.print_exc()
    
    # Check why simulation ended
    if sim_time >= max_sim_time:
        print(f"\n⚠️  Simulation ended due to time limit ({max_sim_time}s)")
    elif step_count >= max_steps:
        print(f"\n⚠️  Simulation ended due to step limit ({max_steps} steps)")
    else:
        print(f"\n✅ Simulation completed successfully")
    
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
    print(f"Simulation Time: {sim_time:.1f} seconds ({sim_time/60:.1f} minutes)")
    print(f"Total Vehicles Seen: {len(all_vehicles_seen)}")
    print(f"EVs Tracked: {len(ev_vehicles_seen)}")
    print(f"EV Data Points Collected: {total_ev_data_collected}")
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
