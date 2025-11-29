"""
Quick script to verify mixed traffic composition in route file
"""
import xml.etree.ElementTree as ET
from collections import Counter

# Parse route file
tree = ET.parse('CustomRoadNetwork.rou.xml')
root = tree.getroot()

# Get all vehicle types
all_vehicles = root.findall('vehicle')

# Separate test and traffic vehicles
test_vehicles = [v for v in all_vehicles if v.get('id').startswith('test_')]
traffic_vehicles = [v for v in all_vehicles if v.get('id').startswith('r')]

# Count vehicle types
ev_types = ['Default_EV', 'Easybike_ER-02B', 'Small_Easybike_V12', 'Electric_Rickshaw_V8']
non_ev_types = ['Private_Car', 'CNG_Rickshaw', 'Bus', 'Truck', 'Motorcycle']

# Analyze traffic composition
traffic_type_counts = Counter([v.get('type') for v in traffic_vehicles])

# Count EVs vs Non-EVs
ev_count = sum(count for vtype, count in traffic_type_counts.items() if vtype in ev_types)
non_ev_count = sum(count for vtype, count in traffic_type_counts.items() if vtype in non_ev_types)

print("=" * 70)
print("              TRAFFIC COMPOSITION VERIFICATION")
print("=" * 70)
print(f"\n📊 OVERALL STATISTICS:")
print(f"   Total Vehicles: {len(all_vehicles)}")
print(f"   ├─ Test Vehicles: {len(test_vehicles)} (all EVs)")
print(f"   └─ Traffic Vehicles: {len(traffic_vehicles)}")
print(f"      ├─ EVs: {ev_count} ({ev_count/len(traffic_vehicles)*100:.1f}%)")
print(f"      └─ Non-EVs: {non_ev_count} ({non_ev_count/len(traffic_vehicles)*100:.1f}%)")

print(f"\n⚡ ELECTRIC VEHICLE BREAKDOWN:")
for vtype in ev_types:
    count = traffic_type_counts.get(vtype, 0)
    if count > 0:
        print(f"   {vtype:25s}: {count:3d} vehicles")

print(f"\n🚗 NON-EV VEHICLE BREAKDOWN:")
for vtype in non_ev_types:
    count = traffic_type_counts.get(vtype, 0)
    if count > 0:
        print(f"   {vtype:25s}: {count:3d} vehicles")

# Analyze by route
print(f"\n🛣️  VEHICLES PER ROUTE:")
routes = {
    'r1': 'Route 1 (E0 - Direct)',
    'r2': 'Route 2 (E3 E9 - Dhormotola)',
    'r3': 'Route 3 (E3 E3.189 -E4 - Chachra)',
    'r4': 'Route 4 (E2 -E1 - NewMarket)',
    'r5': 'Route 5 (E2 -E8 E7 - Monihar)'
}

for route_id, route_name in routes.items():
    route_vehicles = [v for v in traffic_vehicles if v.get('id').startswith(f"{route_id}_")]
    route_evs = sum(1 for v in route_vehicles if v.get('type') in ev_types)
    route_non_evs = len(route_vehicles) - route_evs
    print(f"   {route_name:40s}: {len(route_vehicles):3d} vehicles (EVs: {route_evs}, Non-EVs: {route_non_evs})")

print(f"\n🎯 RSU DATA COLLECTION TARGET:")
total_evs = len(test_vehicles) + ev_count
total_vehicles = len(all_vehicles)
print(f"   EVs to track: {total_evs} ({total_evs/total_vehicles*100:.1f}% of all vehicles)")
print(f"   Non-EVs to ignore: {non_ev_count} ({non_ev_count/total_vehicles*100:.1f}% of all vehicles)")
print(f"   Data reduction: {non_ev_count/total_vehicles*100:.1f}% fewer data points")

print(f"\n✅ VERIFICATION:")
if ev_count > 0 and non_ev_count > 0:
    ratio = ev_count / (ev_count + non_ev_count)
    if 0.35 <= ratio <= 0.45:  # Target is 40%, allow 35-45%
        print(f"   ✅ Traffic mix is realistic (EVs: {ratio*100:.1f}%)")
    else:
        print(f"   ⚠️  Traffic mix unusual (EVs: {ratio*100:.1f}%, expected ~40%)")
    
    if len(set(traffic_type_counts.keys()) & set(ev_types)) > 0:
        print(f"   ✅ EV types present: {len(set(traffic_type_counts.keys()) & set(ev_types))} types")
    
    if len(set(traffic_type_counts.keys()) & set(non_ev_types)) > 0:
        print(f"   ✅ Non-EV types present: {len(set(traffic_type_counts.keys()) & set(non_ev_types))} types")
else:
    print(f"   ❌ ERROR: Missing vehicle types!")

print("=" * 70)
