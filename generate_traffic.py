import xml.etree.ElementTree as ET

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

# Vehicle types to cycle through - Mix of EVs (40%) and Non-EVs (60%)
# Pattern: 2 EVs, 3 Non-EVs, repeating for realistic traffic
ev_types = ['Easybike_ER-02B', 'Small_Easybike_V12', 'Electric_Rickshaw_V8', 'Default_EV']
non_ev_types = ['Private_Car', 'CNG_Rickshaw', 'Bus', 'Truck', 'Motorcycle']

# Generate 40 vehicles per route (200 total) with mixed EV/Non-EV traffic
vehicle_count = 0
ev_counter = 0
non_ev_counter = 0

for route_id, route_info in routes.items():
    # Add comment
    comment = ET.Comment(f" {route_info['name']} Traffic (Mixed EV/Non-EV) ")
    root.append(comment)
    
    for i in range(1, 41):  # 40 vehicles per route
        vehicle_id = f"{route_id}_v{i}"
        
        # Realistic mix: 40% EV, 60% Non-EV
        # Pattern: EV, EV, Non-EV, Non-EV, Non-EV (repeats every 5 vehicles)
        if i % 5 in [1, 2]:  # Positions 1, 2 in each group of 5
            v_type = ev_types[ev_counter % len(ev_types)]
            ev_counter += 1
        else:  # Positions 3, 4, 5 in each group of 5
            v_type = non_ev_types[non_ev_counter % len(non_ev_types)]
            non_ev_counter += 1
        
        depart_time = f"{5 + (i * 2):.2f}"  # Stagger: 5, 7, 9, 11... up to 83 seconds
        
        vehicle = ET.Element('vehicle')
        vehicle.set('id', vehicle_id)
        vehicle.set('type', v_type)
        vehicle.set('depart', depart_time)
        
        route_elem = ET.SubElement(vehicle, 'route')
        route_elem.set('edges', route_info['edges'])
        
        root.append(vehicle)
        vehicle_count += 1

# Count EVs vs Non-EVs
ev_count = sum(1 for v in root.findall('vehicle') if v.get('id').startswith('r') and v.get('type') in ev_types)
non_ev_count = sum(1 for v in root.findall('vehicle') if v.get('id').startswith('r') and v.get('type') in non_ev_types)

print(f"✅ Generated {vehicle_count} traffic vehicles (40 per route)")
print(f"   📊 EVs: {ev_count} ({ev_count/vehicle_count*100:.0f}%)")
print(f"   📊 Non-EVs: {non_ev_count} ({non_ev_count/vehicle_count*100:.0f}%)")

# Sort all vehicles by departure time
vehicles = root.findall('vehicle')
vehicles_sorted = sorted(vehicles, key=lambda v: float(v.get('depart', '0.0')))

# Remove all vehicles from root
for vehicle in vehicles:
    root.remove(vehicle)

# Find the position to insert (after the last vType or comment about traffic)
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
print("\n✅ Route file updated with realistic mixed traffic")
print(f"📊 Total vehicles: 5 test (EV) + {vehicle_count} traffic = {5 + vehicle_count} vehicles")
print(f"🚗 Traffic composition: {ev_count + 5} EVs, {non_ev_count} Non-EVs")
print("\n⚠️  RSU will only collect data from EV vehicles (those with battery devices)")
