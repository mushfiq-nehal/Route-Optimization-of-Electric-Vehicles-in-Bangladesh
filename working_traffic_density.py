"""
Working version of traffic density calculation
"""

def get_traffic_density_ahead_working(vehicle_id, edge_id, lane_id, vehicle_position):
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
        # Initialize with safe defaults
        vehicles_ahead = 0
        same_direction_ahead = 0
        distance_to_tls = -1
        next_tls_id = 'none'
        tls_state = 'unknown'
        edge_occupancy = 0.0
        total_vehicles_on_edge = 0
        
        # Get all vehicles on the current edge
        if edge_id:
            try:
                vehicles_on_edge = traci.edge.getLastStepVehicleIDs(edge_id)
                total_vehicles_on_edge = len(vehicles_on_edge)
                
                # Count vehicles ahead in the same direction
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
                                
                    except Exception as e:
                        # Skip vehicles with errors
                        continue
                        
            except Exception as e:
                # Edge access failed
                pass
        
        # Calculate edge occupancy percentage
        try:
            if lane_id and ":" not in lane_id:  # Valid lane (not internal)
                edge_length = traci.lane.getLength(lane_id)
            else:
                edge_length = 100.0  # Default fallback
        except:
            edge_length = 100.0  # Default fallback
            
        if edge_length > 0:
            edge_occupancy = min(100.0, (total_vehicles_on_edge / max(1, edge_length / 7.5)) * 100)
        
        # Try to find next traffic light
        try:
            # Get traffic light IDs 
            tls_list = traci.trafficlight.getIDList()
            if tls_list:
                next_tls_id = tls_list[0]  # Use first one as example
                tls_state = traci.trafficlight.getRedYellowGreenState(next_tls_id)
                distance_to_tls = 50.0  # Placeholder distance
        except:
            pass
        
        return {
            'vehicles_ahead': vehicles_ahead,
            'same_direction_ahead': same_direction_ahead, 
            'distance_to_tls': distance_to_tls,
            'next_tls_id': next_tls_id,
            'tls_state': tls_state,
            'edge_occupancy': round(edge_occupancy, 2),
            'total_vehicles_on_edge': total_vehicles_on_edge
        }
        
    except Exception as e:
        print(f"Error calculating traffic density for {vehicle_id}: {e}")
        # Return safe defaults
        return {
            'vehicles_ahead': 0,
            'same_direction_ahead': 0,
            'distance_to_tls': -1,
            'next_tls_id': 'unknown',
            'tls_state': 'unknown',
            'edge_occupancy': 0.0,
            'total_vehicles_on_edge': 0
        }