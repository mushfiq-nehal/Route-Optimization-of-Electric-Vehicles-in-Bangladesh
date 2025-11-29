import xml.etree.ElementTree as ET

# Parse the current route file
tree = ET.parse('CustomRoadNetwork.rou.xml')
root = tree.getroot()

# Vehicle types to cycle through
v_types = ['Easybike_ER-02B', 'Small_Easybike_V12', 'Electric_Rickshaw_V8', 'Default_EV']

# Find the last r1 vehicle to know where to start numbering
r1_vehicles = [v for v in root.findall('vehicle') if v.get('id', '').startswith('r1_v')]
max_r1_num = max([int(v.get('id').split('_v')[1]) for v in r1_vehicles])
print(f"Current Route 1 vehicles: {len(r1_vehicles)} (r1_v1 to r1_v{max_r1_num})")

# Add 100 more vehicles to Route 1 (E0)
new_vehicles = []
for i in range(max_r1_num + 1, max_r1_num + 101):  # Add 100 more
    vehicle_id = f"r1_v{i}"
    v_type = v_types[i % len(v_types)]
    # Spread them from 90s to 290s (every 2 seconds)
    depart_time = f"{90 + ((i - max_r1_num - 1) * 2):.2f}"
    
    vehicle = ET.Element('vehicle')
    vehicle.set('id', vehicle_id)
    vehicle.set('type', v_type)
    vehicle.set('depart', depart_time)
    
    route_elem = ET.SubElement(vehicle, 'route')
    route_elem.set('edges', 'E0')
    
    new_vehicles.append((float(depart_time), vehicle))

print(f"Adding 100 more vehicles to Route 1 (E0): r1_v{max_r1_num + 1} to r1_v{max_r1_num + 100}")
print(f"Depart times: 90s to {90 + (100 - 1) * 2}s")

# Get all existing vehicles with their depart times
all_vehicles = [(float(v.get('depart', '0.0')), v) for v in root.findall('vehicle')]
all_vehicles.extend(new_vehicles)

# Sort by depart time
all_vehicles.sort(key=lambda x: x[0])

# Remove all vehicles from root
for vehicle in root.findall('vehicle'):
    root.remove(vehicle)

# Find the insertion point (after last vType or comment)
insert_index = len(root)
for i, elem in enumerate(root):
    if elem.tag in ['vehicle', 'flow']:
        insert_index = i
        break

# Re-add all sorted vehicles
for _, vehicle in all_vehicles:
    root.insert(insert_index, vehicle)
    insert_index += 1

# Save updated file
tree.write('CustomRoadNetwork.rou.xml', encoding='UTF-8', xml_declaration=True)
print(f"\n✅ Route file updated!")
print(f"📊 Total vehicles on Route 1 (E0): {len([v for _, v in all_vehicles if 'r1_' in v.get('id', '')])}")
print(f"📊 Total vehicles in simulation: {len(all_vehicles)}")
