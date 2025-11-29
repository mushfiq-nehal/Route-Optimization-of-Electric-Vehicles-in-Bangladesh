"""
Test traffic density calculation with a simpler approach
"""
import traci

def simple_traffic_test():
    """Simplified test to validate basic traffic counting"""
    
    try:
        # Start SUMO
        sumo_cmd = ["sumo", "-c", "CustomRoadNetwork.sumocfg", "--no-step-log"]
        traci.start(sumo_cmd)
        print("SUMO started")
        
        # Run simulation for a bit
        for step in range(20):
            traci.simulationStep()
            
            vehicles = traci.vehicle.getIDList()
            print(f"Step {step}: {len(vehicles)} vehicles")
            
            if vehicles and step == 10:
                # Test with first vehicle
                vid = vehicles[0]
                print(f"\nTesting with vehicle: {vid}")
                
                try:
                    # Basic info
                    edge_id = traci.vehicle.getRoadID(vid)
                    lane_id = traci.vehicle.getLaneID(vid)
                    lane_pos = traci.vehicle.getLanePosition(vid)
                    
                    print(f"Vehicle position: edge={edge_id}, lane={lane_id}, pos={lane_pos}")
                    
                    # Count vehicles on same edge
                    if edge_id:
                        edge_vehicles = traci.edge.getLastStepVehicleIDs(edge_id)
                        print(f"Vehicles on edge {edge_id}: {len(edge_vehicles)} - {edge_vehicles}")
                        
                        # Count ahead
                        ahead_count = 0
                        for other_vid in edge_vehicles:
                            if other_vid != vid:
                                try:
                                    other_pos = traci.vehicle.getLanePosition(other_vid)
                                    if other_pos > lane_pos:
                                        ahead_count += 1
                                        print(f"  {other_vid} ahead at position {other_pos}")
                                except:
                                    pass
                        
                        print(f"Vehicles ahead: {ahead_count}")
                        
                        # Test lane info
                        if lane_id and ":" not in lane_id:
                            try:
                                lane_length = traci.lane.getLength(lane_id)
                                print(f"Lane {lane_id} length: {lane_length}m")
                            except Exception as e:
                                print(f"Error getting lane length: {e}")
                        
                except Exception as e:
                    print(f"Error testing vehicle {vid}: {e}")
        
        traci.close()
        print("\nTest completed successfully")
        
    except Exception as e:
        print(f"Test failed: {e}")
        try:
            traci.close()
        except:
            pass

if __name__ == "__main__":
    simple_traffic_test()