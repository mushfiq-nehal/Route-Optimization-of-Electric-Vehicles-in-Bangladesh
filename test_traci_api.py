"""
Test TraCI API functions to debug traffic density calculation
"""
import traci
import sys

def test_traci_api():
    """Test various TraCI API calls to find the correct methods"""
    
    try:
        # Start SUMO
        sumo_cmd = ["sumo", "-c", "CustomRoadNetwork.sumocfg", "--no-step-log"]
        traci.start(sumo_cmd)
        
        print("SUMO started successfully")
        
        # Run a few steps to get vehicles
        for i in range(10):
            traci.simulationStep()
        
        # Get vehicles
        vehicles = traci.vehicle.getIDList()
        print(f"Found {len(vehicles)} vehicles")
        
        if vehicles:
            vid = vehicles[0]
            print(f"\nTesting with vehicle: {vid}")
            
            # Test vehicle info
            try:
                edge_id = traci.vehicle.getRoadID(vid)
                lane_id = traci.vehicle.getLaneID(vid)
                print(f"Vehicle on edge: {edge_id}, lane: {lane_id}")
            except Exception as e:
                print(f"Error getting vehicle road/lane: {e}")
            
            # Test edge methods
            if edge_id:
                print(f"\nTesting edge methods for: {edge_id}")
                
                try:
                    vehicles_on_edge = traci.edge.getLastStepVehicleIDs(edge_id)
                    print(f"Vehicles on edge: {len(vehicles_on_edge)}")
                except Exception as e:
                    print(f"Error getting vehicles on edge: {e}")
                
                # Check available edge methods
                print("Available edge methods:")
                for attr in dir(traci.edge):
                    if not attr.startswith('_'):
                        print(f"  - {attr}")
                
                # Test lane methods
                if lane_id and ":" not in lane_id:
                    print(f"\nTesting lane methods for: {lane_id}")
                    try:
                        lane_length = traci.lane.getLength(lane_id)
                        print(f"Lane length: {lane_length}m")
                    except Exception as e:
                        print(f"Error getting lane length: {e}")
                    
                    try:
                        vehicles_on_lane = traci.lane.getLastStepVehicleIDs(lane_id)
                        print(f"Vehicles on lane: {len(vehicles_on_lane)}")
                    except Exception as e:
                        print(f"Error getting vehicles on lane: {e}")
        
        # Test traffic light methods
        print(f"\nTesting traffic light methods:")
        try:
            tls_list = traci.trafficlight.getIDList()
            print(f"Traffic lights found: {tls_list}")
            
            if tls_list:
                tls_id = tls_list[0]
                state = traci.trafficlight.getRedYellowGreenState(tls_id)
                print(f"Traffic light {tls_id} state: {state}")
        except Exception as e:
            print(f"Error getting traffic lights: {e}")
        
        traci.close()
        print("\nTraCI test completed successfully")
        
    except Exception as e:
        print(f"TraCI test failed: {e}")
        try:
            traci.close()
        except:
            pass


if __name__ == "__main__":
    test_traci_api()