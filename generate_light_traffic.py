"""
Lightweight traffic generator for testing on slower systems
Reduces vehicle count for better performance
"""

import xml.etree.ElementTree as ET
from collections import Counter

def generate_light_traffic():
    """Generate reduced traffic for performance testing"""
    
    # Parse the current route file
    tree = ET.parse('CustomRoadNetwork.rou.xml')
    root = tree.getroot()

    # Remove all existing traffic vehicles (keep test vehicles and vTypes)
    vehicles_to_remove = []
    for vehicle in root.findall('vehicle'):
        if vehicle.get('id').startswith('r'):  # Traffic vehicles start with 'r'
            vehicles_to_remove.append(vehicle)

    for vehicle in vehicles_to_remove:
        root.remove(vehicle)

    # Define routes
    routes = {
        'r1': {'edges': 'E0', 'name': 'Route 1 (E0)'},
        'r2': {'edges': 'E3 E9', 'name': 'Route 2 (E3 E9)'},
        'r3': {'edges': 'E3 E3.189 -E4', 'name': 'Route 3 (E3 E3.189 -E4)'},
        'r4': {'edges': 'E2 -E1', 'name': 'Route 4 (E2 -E1)'},
        'r5': {'edges': 'E2 -E8 E7', 'name': 'Route 5 (E2 -E8 E7)'}
    }

    # Reduced vehicle types - only essential ones
    ev_types = ['Easybike_ER-02B', 'Small_Easybike_V12']  # Only 2 EV types
    non_ev_types = ['Private_Car', 'Bus']  # Only 2 Non-EV types

    # Generate ONLY 5 vehicles per route (25 total) for performance testing
    vehicle_count = 0
    ev_counter = 0
    non_ev_counter = 0

    for route_id, route_info in routes.items():
        # Add comment
        comment = ET.Comment(f" {route_info['name']} Light Traffic (5 vehicles) ")
        root.append(comment)
        
        for i in range(1, 6):  # Only 5 vehicles per route
            vehicle_id = f"{route_id}_v{i}"
            
            # Pattern: EV, EV, Non-EV, Non-EV, EV (40% EV, 60% Non-EV)
            if i in [1, 2, 5]:  # Positions 1, 2, 5 are EVs
                v_type = ev_types[ev_counter % len(ev_types)]
                ev_counter += 1
            else:  # Positions 3, 4 are Non-EVs
                v_type = non_ev_types[non_ev_counter % len(non_ev_types)]
                non_ev_counter += 1
            
            # Spread departure times: 10, 15, 20, 25, 30 seconds
            depart_time = f"{10 + (i * 5):.2f}"
            
            vehicle = ET.Element('vehicle')
            vehicle.set('id', vehicle_id)
            vehicle.set('type', v_type)
            vehicle.set('depart', depart_time)
            
            route_elem = ET.SubElement(vehicle, 'route')
            route_elem.set('edges', route_info['edges'])
            
            root.append(vehicle)
            vehicle_count += 1

    # Count EVs vs Non-EVs
    all_vehicles = root.findall('vehicle')
    traffic_vehicles = [v for v in all_vehicles if v.get('id').startswith('r')]
    ev_count = sum(1 for v in traffic_vehicles if v.get('type') in ev_types)
    non_ev_count = sum(1 for v in traffic_vehicles if v.get('type') in non_ev_types)

    print(f"🚀 Generated LIGHT traffic for performance testing:")
    print(f"   📊 Total traffic vehicles: {vehicle_count} (instead of 200)")
    print(f"   ⚡ EVs: {ev_count} ({ev_count/vehicle_count*100:.0f}%)")
    print(f"   🚗 Non-EVs: {non_ev_count} ({non_ev_count/vehicle_count*100:.0f}%)")

    # Sort all vehicles by departure time
    vehicles = root.findall('vehicle')
    vehicles_sorted = sorted(vehicles, key=lambda v: float(v.get('depart', '0.0')))

    # Remove all vehicles from root
    for vehicle in vehicles:
        root.remove(vehicle)

    # Find the position to insert (after the last vType)
    insert_index = len(root)
    for i, elem in enumerate(root):
        if elem.tag == 'vehicle':
            insert_index = i
            break

    # Re-add sorted vehicles
    for vehicle in vehicles_sorted:
        root.insert(insert_index, vehicle)
        insert_index += 1

    # Save updated file
    tree.write('CustomRoadNetwork.rou.xml', encoding='UTF-8', xml_declaration=True)
    
    print(f"\\n✅ Light traffic saved to route file")
    print(f"📈 Performance improvement: {(200-vehicle_count)/200*100:.0f}% fewer vehicles")
    print(f"\\n🎯 Test with: python traCI_rsu.py")
    print(f"💡 Restore full traffic with: python generate_traffic.py")

if __name__ == "__main__":
    generate_light_traffic()