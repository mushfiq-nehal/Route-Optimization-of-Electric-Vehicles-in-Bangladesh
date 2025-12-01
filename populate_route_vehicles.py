"""
Populate R1-R7 routes with all EV types (3 types + Default_EV) and non-EV vehicles
Ensures comprehensive testing of all vehicle types across all routes
"""
import xml.etree.ElementTree as ET

# Parse route file
tree = ET.parse('CustomRoadNetwork.rou.xml')
root = tree.getroot()

# Define vehicle types - 3 main EVs + Default_EV + non-EV
ev_types = ['Easybike_ER-02B', 'Small_Easybike_V12', 'Electric_Rickshaw_V8']
all_vehicle_types = ev_types + ['Default_EV', 'Non_EV']

# R1-R7 routes from current file
routes = {
    'R1': {'from': 'E3', 'to': 'E4', 'via': 'E3.189'},
    'R2': {'from': 'E3', 'to': 'E7', 'via': 'E3.189 E5 E6'},
    'R3': {'from': 'E3', 'to': 'E9', 'via': None},
    'R4': {'from': 'E0', 'to': 'E0', 'via': None},
    'R5': {'from': 'E2', 'to': '-E1', 'via': None},
    'R6': {'from': 'E2', 'to': 'E7', 'via': '-E8'},
    'R7': {'from': 'E2', 'to': '-E4', 'via': '-E8 -E6 -E5'}
}

# First, add Non_EV vType definition if not present
non_ev_type = """  <vType id="Non_EV" vClass="passenger" accel="2.6" decel="4.5" sigma="0.5" length="4.5" width="1.8" maxSpeed="50.0" guiShape="passenger" emissionClass="HBEFA3/PC_G_EU4">
    <param key="has.battery.device" value="false" />
  </vType>"""

# Check if vType definitions exist, if not add them from backup
vtypes_exist = any(elem.tag == 'vType' for elem in root)

if not vtypes_exist:
    print("⚠️  No vType definitions found. Adding from backup...")
    # Read vTypes from backup
    backup_tree = ET.parse('CustomRoadNetwork.rou.xml.backup')
    backup_root = backup_tree.getroot()
    
    # Insert comment
    comment = ET.Comment(' Vehicle Type Definitions ')
    root.insert(0, comment)
    
    # Copy all vType elements
    insert_pos = 1
    for vtype in backup_root.findall('vType'):
        root.insert(insert_pos, vtype)
        insert_pos += 1
    
    # Add Non_EV type
    non_ev_elem = ET.fromstring(non_ev_type)
    root.insert(insert_pos, non_ev_elem)
    print(f"✅ Added {insert_pos} vType definitions")

# Remove existing R1-R7 trip definitions (they'll be replaced with vehicle elements)
trips_to_remove = []
for trip in root.findall('trip'):
    if trip.get('id') in routes.keys():
        trips_to_remove.append(trip)

for trip in trips_to_remove:
    root.remove(trip)
    
if trips_to_remove:
    print(f"🗑️  Removed {len(trips_to_remove)} trip definitions (converting to vehicles)")

# Generate vehicles for each route with all vehicle types
vehicle_count = 0
depart_time = 1.0

# Add comment for test vehicles section
test_comment = ET.Comment(' R1-R7 Test Vehicles with All Types ')
root.append(test_comment)

for route_id, route_info in routes.items():
    # Route comment
    route_comment = ET.Comment(f' Route {route_id}: {route_info["from"]} → {route_info["to"]} ')
    root.append(route_comment)
    
    # Create vehicle for each type
    for v_type in all_vehicle_types:
        vehicle_id = f"{route_id}_{v_type}"
        
        vehicle = ET.Element('vehicle')
        vehicle.set('id', vehicle_id)
        vehicle.set('type', v_type)
        vehicle.set('depart', f"{depart_time:.2f}")
        
        # Create route element
        route_elem = ET.SubElement(vehicle, 'route')
        
        # Build edges string from from/to/via
        if route_info['via']:
            edges = f"{route_info['from']} {route_info['via']} {route_info['to']}"
        else:
            edges = f"{route_info['from']} {route_info['to']}"
        
        # For circular route R4, just use from edge
        if route_info['from'] == route_info['to']:
            edges = route_info['from']
        
        route_elem.set('edges', edges)
        
        root.append(vehicle)
        vehicle_count += 1
        depart_time += 2.0  # Stagger by 2 seconds

# Count coverage
print(f"\n✅ Generated {vehicle_count} vehicles")
print(f"   📊 {len(routes)} routes × {len(all_vehicle_types)} vehicle types = {len(routes) * len(all_vehicle_types)} vehicles")
print(f"\n🚗 Vehicle Types Coverage:")
for v_type in all_vehicle_types:
    count = len([v for v in root.findall('vehicle') if v.get('type') == v_type])
    routes_covered = len([r for r in routes.keys()])
    print(f"   • {v_type}: {count} vehicles across {routes_covered} routes")

# Verify all routes have all types
print(f"\n🔍 Route Coverage Verification:")
for route_id in routes.keys():
    route_vehicles = [v for v in root.findall('vehicle') if v.get('id').startswith(f"{route_id}_")]
    types_in_route = set([v.get('type') for v in route_vehicles])
    
    missing_types = set(all_vehicle_types) - types_in_route
    if missing_types:
        print(f"   ⚠️  {route_id}: MISSING {missing_types}")
    else:
        print(f"   ✅ {route_id}: All {len(all_vehicle_types)} vehicle types present")

# Save
tree.write('CustomRoadNetwork.rou.xml', encoding='UTF-8', xml_declaration=True)
print(f"\n✅ Route file updated successfully!")
print(f"📄 File: CustomRoadNetwork.rou.xml")
print(f"🎯 Total vehicles: {vehicle_count}")
