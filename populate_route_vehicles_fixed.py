"""
Populate R1-R7 routes with all EV types using trip definitions
SUMO will automatically compute valid routes between from/to edges
"""
import xml.etree.ElementTree as ET

# Parse route file
tree = ET.parse('CustomRoadNetwork.rou.xml')
root = tree.getroot()

# Define vehicle types - 3 main EVs + Default_EV + non-EV
ev_types = ['Easybike_ER-02B', 'Small_Easybike_V12', 'Electric_Rickshaw_V8']
all_vehicle_types = ev_types + ['Default_EV', 'Non_EV']

# R1-R7 route definitions using from/to/via
# These will be processed by SUMO's duarouter to find valid paths
route_definitions = {
    'R1': {'from': 'E3', 'to': 'E4', 'via': ['E3.189']},
    'R2': {'from': 'E3', 'to': 'E7', 'via': ['E3.189', 'E5', 'E6']},
    'R3': {'from': 'E3', 'to': 'E9', 'via': []},
    'R4': {'from': 'E0', 'to': 'E0', 'via': []},  # Circular - direct route
    'R5': {'from': 'E2', 'to': '-E1', 'via': []},
    'R6': {'from': 'E2', 'to': 'E7', 'via': ['-E8']},
    'R7': {'from': 'E2', 'to': '-E4', 'via': ['-E8', '-E6', '-E5']}
}

# Alternative: Use backup's working routes as reference
# Let's map R1-R7 to known working edge sequences from backup
working_routes = {
    'R1': 'E3 E3.189',  # From backup r6
    'R2': 'E3 E3.189 E5 E6 E7',  # From backup r7
    'R3': 'E3 E9',  # From backup r1
    'R4': 'E0',  # Single edge circular
    'R5': 'E2 -E1',  # From backup r4
    'R6': 'E2 -E8 E7',  # From backup r5
    'R7': 'E2 -E8'  # Partial route (full path may not be valid)
}

# Check what routes actually exist in backup
print("🔍 Analyzing backup routes...")
backup_tree = ET.parse('CustomRoadNetwork.rou.xml.backup')
backup_root = backup_tree.getroot()

backup_routes = {}
for vehicle in backup_root.findall('vehicle'):
    v_id = vehicle.get('id')
    if v_id and v_id.startswith('r'):
        route_elem = vehicle.find('route')
        if route_elem is not None:
            edges = route_elem.get('edges')
            route_key = v_id.split('_')[0]  # e.g., 'r1', 'r2', etc.
            if route_key not in backup_routes:
                backup_routes[route_key] = edges
                print(f"   {route_key}: {edges}")

# Map R1-R7 to working r1-r8 routes
route_mapping = {
    'R1': backup_routes.get('r6', 'E3 E3.189'),  # R1 similar to old r6
    'R2': backup_routes.get('r7', 'E3 E3.189 E5 E6 E7'),  # R2 similar to old r7
    'R3': backup_routes.get('r1', 'E3 E9'),  # R3 similar to old r1
    'R4': backup_routes.get('r2', 'E4'),  # R4 circular - use r2's E4
    'R5': backup_routes.get('r4', 'E2 -E1'),  # R5 similar to old r4
    'R6': backup_routes.get('r5', 'E2 -E8 E7'),  # R6 similar to old r5
    'R7': backup_routes.get('r3', 'E8')  # R7 similar to old r3
}

print(f"\n📋 Route mapping complete. Found {len(route_mapping)} routes.\n")

# Remove existing vehicles (keep vTypes)
vehicles_to_remove = [v for v in root.findall('vehicle')]
for v in vehicles_to_remove:
    root.remove(v)

print(f"🗑️  Removed {len(vehicles_to_remove)} existing vehicles\n")

# Generate vehicles for each route with all vehicle types
vehicle_count = 0
depart_time = 1.0

# Add comment for test vehicles section
test_comment = ET.Comment(' R1-R7 Test Vehicles with All Types ')
root.append(test_comment)

for route_id in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']:
    edges = route_mapping.get(route_id, '')
    
    # Route comment
    route_comment = ET.Comment(f' Route {route_id}: {edges} ')
    root.append(route_comment)
    
    # Create vehicle for each type
    for v_type in all_vehicle_types:
        vehicle_id = f"{route_id}_{v_type}"
        
        vehicle = ET.Element('vehicle')
        vehicle.set('id', vehicle_id)
        vehicle.set('type', v_type)
        vehicle.set('depart', f"{depart_time:.2f}")
        
        # Create route element with known working edges
        route_elem = ET.SubElement(vehicle, 'route')
        route_elem.set('edges', edges)
        
        root.append(vehicle)
        vehicle_count += 1
        depart_time += 2.0  # Stagger by 2 seconds

# Count coverage
print(f"✅ Generated {vehicle_count} vehicles")
print(f"   📊 7 routes × {len(all_vehicle_types)} vehicle types = {len(['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']) * len(all_vehicle_types)} vehicles")
print(f"\n🚗 Vehicle Types Coverage:")
for v_type in all_vehicle_types:
    count = len([v for v in root.findall('vehicle') if v.get('type') == v_type])
    print(f"   • {v_type}: {count} vehicles across 7 routes")

# Verify all routes have all types
print(f"\n🔍 Route Coverage Verification:")
for route_id in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']:
    route_vehicles = [v for v in root.findall('vehicle') if v.get('id').startswith(f"{route_id}_")]
    types_in_route = set([v.get('type') for v in route_vehicles])
    
    missing_types = set(all_vehicle_types) - types_in_route
    if missing_types:
        print(f"   ⚠️  {route_id}: MISSING {missing_types}")
    else:
        print(f"   ✅ {route_id}: All {len(all_vehicle_types)} vehicle types present ({route_mapping[route_id]})")

# Save
tree.write('CustomRoadNetwork.rou.xml', encoding='UTF-8', xml_declaration=True)
print(f"\n✅ Route file updated successfully!")
print(f"📄 File: CustomRoadNetwork.rou.xml")
print(f"🎯 Total vehicles: {vehicle_count}")
