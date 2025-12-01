"""
Add realistic traffic with buses, trucks, private cars, CNG rickshaws, and motorcycles
Creates mixed traffic to simulate real-world conditions in Bangladesh
"""
import xml.etree.ElementTree as ET
import random

# Parse route file
tree = ET.parse('CustomRoadNetwork.rou.xml')
root = tree.getroot()

# Get all available routes from existing vehicles
existing_routes = {}
for vehicle in root.findall('vehicle'):
    route_elem = vehicle.find('route')
    if route_elem is not None:
        edges = route_elem.get('edges')
        if edges not in existing_routes.values():
            existing_routes[vehicle.get('id').split('_')[0]] = edges

print(f"📍 Found {len(existing_routes)} unique routes")

# Define new non-EV vehicle types
new_vtypes = [
    {
        'id': 'Private_Car',
        'vClass': 'passenger',
        'accel': '2.6',
        'decel': '4.5',
        'sigma': '0.5',
        'length': '4.5',
        'width': '1.8',
        'maxSpeed': '30.0',  # ~108 km/h
        'guiShape': 'passenger',
        'emissionClass': 'HBEFA3/PC_G_EU4',
        'color': '1,1,0'  # Yellow
    },
    {
        'id': 'Bus',
        'vClass': 'bus',
        'accel': '1.2',
        'decel': '3.5',
        'sigma': '0.5',
        'length': '12.0',
        'width': '2.5',
        'maxSpeed': '22.0',  # ~79 km/h
        'guiShape': 'bus',
        'emissionClass': 'HBEFA3/Bus',
        'color': '0,1,0'  # Green
    },
    {
        'id': 'Truck',
        'vClass': 'truck',
        'accel': '1.0',
        'decel': '3.0',
        'sigma': '0.5',
        'length': '8.0',
        'width': '2.4',
        'maxSpeed': '20.0',  # ~72 km/h
        'guiShape': 'truck',
        'emissionClass': 'HBEFA3/HDV',
        'color': '0.5,0.5,0.5'  # Gray
    },
    {
        'id': 'CNG_Rickshaw',
        'vClass': 'taxi',
        'accel': '1.5',
        'decel': '3.0',
        'sigma': '0.7',
        'length': '2.8',
        'width': '1.3',
        'maxSpeed': '11.0',  # ~40 km/h
        'guiShape': 'taxi',
        'emissionClass': 'HBEFA3/LDV_G_EU4',
        'color': '0,1,1'  # Cyan
    },
    {
        'id': 'Motorcycle',
        'vClass': 'motorcycle',
        'accel': '3.0',
        'decel': '5.0',
        'sigma': '0.8',
        'length': '2.2',
        'width': '0.8',
        'maxSpeed': '25.0',  # ~90 km/h
        'guiShape': 'motorcycle',
        'emissionClass': 'HBEFA3/LDV_G_EU4',
        'color': '1,0,0'  # Red
    }
]

# Check if these vTypes already exist
existing_vtype_ids = [vt.get('id') for vt in root.findall('vType')]

# Add new vTypes if they don't exist
insert_pos = len([elem for elem in root if elem.tag == 'vType'])
added_vtypes = 0

for vtype_def in new_vtypes:
    if vtype_def['id'] not in existing_vtype_ids:
        vtype = ET.Element('vType')
        for key, value in vtype_def.items():
            vtype.set(key, value)
        
        # Add has.battery.device param
        param = ET.SubElement(vtype, 'param')
        param.set('key', 'has.battery.device')
        param.set('value', 'false')
        
        root.insert(insert_pos, vtype)
        insert_pos += 1
        added_vtypes += 1
        print(f"   ✅ Added vType: {vtype_def['id']}")

print(f"\n🚗 Added {added_vtypes} new vehicle types")

# Add traffic comment
traffic_comment = ET.Comment(' Mixed Traffic Vehicles ')
root.append(traffic_comment)

# Generate traffic vehicles
traffic_types = ['Private_Car', 'Bus', 'Truck', 'CNG_Rickshaw', 'Motorcycle']
vehicles_per_type_per_route = 10  # 10 of each type on each route

depart_time = 100.0  # Start after test vehicles
vehicle_count = 0

# Traffic distribution weights (realistic for Bangladesh)
# Private cars: 30%, CNG: 25%, Motorcycle: 25%, Bus: 15%, Truck: 5%
traffic_weights = {
    'Private_Car': 0.30,
    'CNG_Rickshaw': 0.25,
    'Motorcycle': 0.25,
    'Bus': 0.15,
    'Truck': 0.05
}

for route_id, edges in existing_routes.items():
    route_comment = ET.Comment(f' Traffic on {route_id} route ')
    root.append(route_comment)
    
    for v_type in traffic_types:
        count = int(vehicles_per_type_per_route * traffic_weights[v_type] * 2)  # Multiply by 2 for more traffic
        
        for i in range(1, count + 1):
            vehicle_id = f"traffic_{route_id}_{v_type}_{i}"
            
            vehicle = ET.Element('vehicle')
            vehicle.set('id', vehicle_id)
            vehicle.set('type', v_type)
            vehicle.set('depart', f"{depart_time:.2f}")
            
            # Create route element
            route_elem = ET.SubElement(vehicle, 'route')
            route_elem.set('edges', edges)
            
            root.append(vehicle)
            vehicle_count += 1
            depart_time += random.uniform(1.0, 3.0)  # Random spacing 1-3 seconds

print(f"\n✅ Generated {vehicle_count} traffic vehicles")
print(f"   📊 Distribution:")
for v_type in traffic_types:
    count = len([v for v in root.findall('vehicle') if v.get('type') == v_type])
    percentage = (count / vehicle_count * 100) if vehicle_count > 0 else 0
    print(f"      • {v_type}: {count} vehicles ({percentage:.1f}%)")

# Count totals
total_vehicles = len(root.findall('vehicle'))
total_ev = len([v for v in root.findall('vehicle') if v.get('type') in ['Easybike_ER-02B', 'Small_Easybike_V12', 'Electric_Rickshaw_V8', 'Default_EV']])
total_non_ev = total_vehicles - total_ev

print(f"\n📊 Total Summary:")
print(f"   🔋 EV vehicles: {total_ev}")
print(f"   🚗 Non-EV vehicles: {total_non_ev}")
print(f"   🎯 Total vehicles: {total_vehicles}")

# Save
tree.write('CustomRoadNetwork.rou.xml', encoding='UTF-8', xml_declaration=True)
print(f"\n✅ Route file updated with traffic vehicles!")
print(f"📄 File: CustomRoadNetwork.rou.xml")
