"""
RSU-based TraCI Implementation
Vehicles communicate with RSUs which then forward data to the server
"""

import os
import time
import requests
import traci
import json
from datetime import datetime
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

def get_traffic_density_ahead(vehicle_id, edge_id, lane_id, vehicle_position):
    """
    Calculate traffic density ahead of the vehicle on the same road
    
    Args:
        vehicle_id: ID of the requesting vehicle
        edge_id: Current edge ID
        lane_id: Current lane ID  
        vehicle_position: Position on the lane
        
    Returns:
        Dictionary with traffic density information
    """
    try:
        # Get all vehicles on the current edge
        vehicles_on_edge = traci.edge.getLastStepVehicleIDs(edge_id)
        
        # Get vehicles on the same lane
        vehicles_on_lane = []
        if lane_id and ":" not in lane_id:  # Valid lane (not internal lane)
            try:
                vehicles_on_lane = traci.lane.getLastStepVehicleIDs(lane_id)
            except:
                vehicles_on_lane = []
        
        # Count vehicles ahead in the same direction
        vehicles_ahead = 0
        same_direction_ahead = 0
        
        for vid in vehicles_on_edge:
            if vid == vehicle_id:
                continue
                
            try:
                # Get other vehicle's position on the lane
                other_lane_id = traci.vehicle.getLaneID(vid)
                other_position = traci.vehicle.getLanePosition(vid)
                
                # Check if vehicle is ahead (higher lane position)
                if other_position > vehicle_position:
                    vehicles_ahead += 1
                    
                    # Check if on same lane (same direction)
                    if other_lane_id == lane_id:
                        same_direction_ahead += 1
                        
            except:
                continue
        
        # Find next traffic light and calculate actual distance
        try:
            next_tls_id = 'none'
            tls_state = 'none'
            distance_to_tls = -1
            
            # Get vehicle's route and current position
            vehicle_route = traci.vehicle.getRoute(vehicle_id)
            route_index = traci.vehicle.getRouteIndex(vehicle_id)
            vehicle_lane_position = traci.vehicle.getLanePosition(vehicle_id)
            
            # Define traffic lights and their controlled edges
            traffic_light_edges = {
                'J1': ['E4', '-E5', 'E3.189', 'E3'],
                'J2': ['-E9', '-E3', 'E3'], 
                'J3': ['-E1', 'E7', '-E4', 'E9', 'E0'],
                'J4': ['E6', '-E7', '-E8'],
                'J5': ['E5', '-E6'],
                'J6': ['E8', 'E1', 'E2'],
                'J7': ['-E2', '-E0', '-E30']
            }
            
            # Look for next traffic light on the route
            for i in range(route_index, len(vehicle_route)):
                upcoming_edge = vehicle_route[i]
                
                # Check if this edge has a traffic light
                for tls_id, controlled_edges in traffic_light_edges.items():
                    if upcoming_edge in controlled_edges:
                        next_tls_id = tls_id
                        tls_state = traci.trafficlight.getRedYellowGreenState(tls_id)
                        
                        # Calculate distance to traffic light
                        if i == route_index:  # Traffic light on current edge
                            try:
                                current_lane_length = traci.lane.getLength(lane_id)
                                distance_to_tls = max(0, current_lane_length - vehicle_lane_position)
                            except:
                                distance_to_tls = 50.0  # Fallback estimate
                        else:  # Traffic light on future edge
                            distance_to_tls = 0
                            # Add remaining distance on current edge
                            try:
                                current_lane_length = traci.lane.getLength(lane_id)
                                distance_to_tls += max(0, current_lane_length - vehicle_lane_position)
                            except:
                                distance_to_tls += 50.0
                            
                            # Add lengths of intermediate edges
                            for j in range(route_index + 1, i):
                                intermediate_edge = vehicle_route[j]
                                try:
                                    # Use lane 0 as representative lane for edge length
                                    intermediate_lane = f"{intermediate_edge}_0"
                                    edge_length = traci.lane.getLength(intermediate_lane)
                                    distance_to_tls += edge_length
                                except:
                                    distance_to_tls += 100.0  # Fallback estimate
                        
                        # Round to reasonable precision
                        distance_to_tls = round(distance_to_tls, 1)
                        break
                
                if next_tls_id != 'none':
                    break
            
            # If no traffic light found in route, check if current edge has one
            if next_tls_id == 'none':
                current_edge = traci.vehicle.getRoadID(vehicle_id)
                for tls_id, controlled_edges in traffic_light_edges.items():
                    if current_edge in controlled_edges:
                        next_tls_id = tls_id
                        tls_state = traci.trafficlight.getRedYellowGreenState(tls_id)
                        try:
                            current_lane_length = traci.lane.getLength(lane_id)
                            distance_to_tls = max(0, current_lane_length - vehicle_lane_position)
                            distance_to_tls = round(distance_to_tls, 1)
                        except:
                            distance_to_tls = 50.0
                        break
                        
        except Exception as e:
            # Fallback to original simple approach if calculation fails
            try:
                tls_list = traci.trafficlight.getIDList()
                if tls_list:
                    next_tls_id = tls_list[0]
                    tls_state = traci.trafficlight.getRedYellowGreenState(next_tls_id)
                    distance_to_tls = 100.0  # Fallback
                else:
                    next_tls_id = 'none'
                    tls_state = 'none'
                    distance_to_tls = -1
            except:
                next_tls_id = 'error'
                tls_state = 'unknown'
                distance_to_tls = -1
        
        # Calculate edge occupancy percentage
        try:
            # Use lane length since there's no edge.getLength()
            if lane_id and ":" not in lane_id:  # Valid lane (not internal)
                edge_length = traci.lane.getLength(lane_id)
            else:
                edge_length = 100.0  # Default fallback
        except:
            edge_length = 100.0  # Default fallback
        edge_occupancy = min(100.0, (len(vehicles_on_edge) / max(1, edge_length / 7.5)) * 100)  # Assume 7.5m per vehicle
        
        return {
            'vehicles_ahead': vehicles_ahead,
            'same_direction_ahead': same_direction_ahead,
            'distance_to_tls': distance_to_tls,
            'next_tls_id': next_tls_id,
            'tls_state': tls_state,
            'edge_occupancy': round(edge_occupancy, 2),
            'total_vehicles_on_edge': len(vehicles_on_edge)
        }
        
    except Exception as e:
        print(f"Error calculating traffic density for {vehicle_id}: {e}")
        return {
            'vehicles_ahead': 0,
            'same_direction_ahead': 0,
            'distance_to_tls': -1,
            'next_tls_id': 'unknown',
            'tls_state': 'unknown',
            'edge_occupancy': 0.0,
            'total_vehicles_on_edge': 0
        }


def get_next_traffic_light(vehicle_id, edge_id, vehicle_position):
    """
    Find the next traffic light ahead of the vehicle
    
    Args:
        vehicle_id: ID of the vehicle
        edge_id: Current edge ID
        vehicle_position: Current position on edge
        
    Returns:
        Dictionary with next traffic light information
    """
    try:
        # Get vehicle route to find upcoming edges
        route_edges = traci.vehicle.getRoute(vehicle_id)
        current_route_index = traci.vehicle.getRouteIndex(vehicle_id)
        
        # Known traffic light junctions from network (using SUMO IDs)
        traffic_lights = {
            'J1': {'edges': ['E4', '-E5', 'E3.189'], 'name': 'Chachra'},
            'J2': {'edges': ['-E9', '-E3', 'E3'], 'name': 'Dhormotola'},  
            'J3': {'edges': ['-E1', 'E7', '-E4', 'E9', 'E0'], 'name': 'Doratana'},
            'J4': {'edges': ['E6', '-E7', '-E8'], 'name': 'Monihar'},
            'J5': {'edges': ['E5', '-E6'], 'name': 'Muroli'},
            'J6': {'edges': ['E8', 'E1', 'E2'], 'name': 'New_Market'},
            'J7': {'edges': ['-E2', '-E0', '-E30'], 'name': 'Palbari'}
        }
        
        # Check upcoming edges for traffic lights
        for i in range(current_route_index, len(route_edges)):
            upcoming_edge = route_edges[i]
            
            for tls_name, tls_data in traffic_lights.items():
                if upcoming_edge in tls_data['edges']:
                    # Calculate distance
                    if i == current_route_index:  # Same edge
                        try:
                            # Get current vehicle's lane
                            current_lane = traci.vehicle.getLaneID(vehicle_id)
                            if current_lane and ":" not in current_lane:
                                edge_length = traci.lane.getLength(current_lane)
                            else:
                                edge_length = 100.0
                        except:
                            edge_length = 100.0
                        distance = edge_length - vehicle_position
                    else:  # Future edge
                        distance = 0
                        for j in range(current_route_index, i + 1):
                            if j == current_route_index:
                                try:
                                    current_lane = traci.vehicle.getLaneID(vehicle_id)
                                    if current_lane and ":" not in current_lane:
                                        edge_length = traci.lane.getLength(current_lane)
                                    else:
                                        edge_length = 100.0
                                except:
                                    edge_length = 100.0
                                distance += edge_length - vehicle_position
                            else:
                                try:
                                    # Try to get first lane from the edge to calculate length
                                    lane_name = f"{route_edges[j]}_0"
                                    distance += traci.lane.getLength(lane_name)
                                except:
                                    distance += 100.0  # Default fallback
                    
                    # Get traffic light state
                    try:
                        tls_state = traci.trafficlight.getRedYellowGreenState(tls_name)
                    except:
                        tls_state = 'unknown'
                    
                    return {
                        'tls_id': tls_name,
                        'distance': round(distance, 2),
                        'state': tls_state
                    }
        
        # No traffic light found
        return {
            'tls_id': 'none',
            'distance': -1,
            'state': 'none'
        }
        
    except Exception as e:
        return {
            'tls_id': 'error',
            'distance': -1,
            'state': 'unknown'
        }


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
            
            # Get current edge and lane
            edge_id = traci.vehicle.getRoadID(vid)
            lane_id = traci.vehicle.getLaneID(vid)
            lane_position = traci.vehicle.getLanePosition(vid)
            
            # Get traffic density data
            traffic_data = get_traffic_density_ahead(vid, edge_id, lane_id, lane_position)
            
            # Get battery parameters
            battery_capacity = float(traci.vehicle.getParameter(vid, "device.battery.capacity"))
            battery_charge = float(traci.vehicle.getParameter(vid, "device.battery.actualBatteryCapacity"))
            
            # Calculate battery percentage
            battery_percentage = (battery_charge / battery_capacity * 100.0) if battery_capacity > 0 else 0.0
            
            # Prepare vehicle data with consistent field names
            vehicle_data = {
                'vehicle_id': vid,
                'vehicle_type': v_type,
                'speed': speed,
                'edge_id': edge_id,
                'lane_id': lane_id,
                'lane_position': lane_position,
                'vehicles_ahead_count': traffic_data['vehicles_ahead'],
                'same_direction_ahead': traffic_data['same_direction_ahead'],
                'distance_to_traffic_light': traffic_data['distance_to_tls'],
                'next_traffic_light': traffic_data['next_tls_id'],
                'traffic_light_state': traffic_data['tls_state'],
                'edge_occupancy_percentage': traffic_data['edge_occupancy'],
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

def export_enhanced_data_locally(rsu_network, step_count, sim_time, total_vehicles, total_evs, data_points):
    """
    Export enhanced traffic density data locally to JSON and CSV files
    """
    print("\n" + "="*60)
    print("EXPORTING ENHANCED TRAFFIC DENSITY DATA LOCALLY")
    print("="*60)
    
    all_data = []
    total_records = 0
    
    # Collect data from all RSUs
    for rsu in rsu_network.rsus:
        if rsu.vehicle_buffer:  # Only include RSUs with data
            rsu_data = {
                'rsu_id': rsu.rsu_id,
                'rsu_position': rsu.position,
                'connected_vehicles': len(rsu.connected_vehicles),
                'buffered_records': len(rsu.vehicle_buffer),
                'vehicle_data': rsu.vehicle_buffer
            }
            all_data.append(rsu_data)
            total_records += len(rsu.vehicle_buffer)
            print(f"RSU {rsu.rsu_id}: {len(rsu.vehicle_buffer)} enhanced records")
    
    if total_records == 0:
        print("❌ No enhanced data found in RSU buffers")
        return None, None
    
    # Save to JSON file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f'enhanced_traffic_density_data_{timestamp}.json'
    
    # Create summary metadata
    metadata = {
        "export_timestamp": datetime.now().isoformat(),
        "simulation_summary": {
            "total_steps": step_count,
            "simulation_time_seconds": sim_time,
            "total_vehicles_seen": total_vehicles,
            "total_evs_tracked": total_evs,
            "data_points_collected": data_points
        },
        "rsu_data": all_data
    }
    
    with open(json_file, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    # Create flattened CSV for easy analysis
    csv_file = f'enhanced_traffic_density_flat_{timestamp}.csv'
    flat_records = []
    
    for rsu_data in all_data:
        for record in rsu_data['vehicle_data']:
            flat_record = {
                'rsu_id': rsu_data['rsu_id'],
                'rsu_position_x': rsu_data['rsu_position'][0],
                'rsu_position_y': rsu_data['rsu_position'][1],
                **record  # Spread all vehicle data fields
            }
            flat_records.append(flat_record)
    
    # Save flattened data to CSV
    if flat_records:
        try:
            import pandas as pd
            df = pd.DataFrame(flat_records)
            df.to_csv(csv_file, index=False)
            
            print(f"\n✅ Successfully exported {total_records} enhanced records!")
            print(f"📊 Enhanced Traffic Data Summary:")
            print(f"  • Total Records: {len(flat_records)}")
            print(f"  • Active RSUs: {len(all_data)}")
            print(f"  • Data Fields: {len(flat_records[0].keys()) if flat_records else 0}")
            
            if 'vehicles_ahead_count' in flat_records[0]:
                print(f"  • Vehicles Ahead Range: {df['vehicles_ahead_count'].min()}-{df['vehicles_ahead_count'].max()}")
            if 'same_direction_ahead' in flat_records[0]:
                print(f"  • Same Direction Range: {df['same_direction_ahead'].min()}-{df['same_direction_ahead'].max()}")
            if 'edge_occupancy_percentage' in flat_records[0]:
                print(f"  • Edge Occupancy Range: {df['edge_occupancy_percentage'].min():.2f}%-{df['edge_occupancy_percentage'].max():.2f}%")
            
        except ImportError:
            # Fallback to manual CSV writing if pandas not available
            with open(csv_file, 'w') as f:
                if flat_records:
                    # Write header
                    f.write(','.join(flat_records[0].keys()) + '\n')
                    # Write data
                    for record in flat_records:
                        f.write(','.join(str(v) for v in record.values()) + '\n')
            print(f"\n✅ Successfully exported {total_records} enhanced records (without pandas)!")
    
    print("="*60)
    print("ENHANCED DATA FILES CREATED:")
    print(f"  • {json_file} (Complete structured data)")
    print(f"  • {csv_file} (Flat CSV for analysis)")
    print("="*60)
    
    return json_file, csv_file

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
    
    # Export enhanced data locally before ending
    export_enhanced_data_locally(rsu_network, step_count, sim_time, len(all_vehicles_seen), len(ev_vehicles_seen), total_ev_data_collected)
    
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
