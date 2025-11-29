import xml.etree.ElementTree as ET

tree = ET.parse('CustomRoadNetwork.net.xml')
root = tree.getroot()

edges = ['E0', 'E1', 'E2', 'E3', 'E3.189', 'E4', 'E7', 'E8', 'E9']

print("Current Lane Configuration:")
print("-" * 40)
for edge_id in edges:
    edge = root.find(f".//edge[@id='{edge_id}']")
    if edge:
        lanes = edge.findall('lane')
        print(f"{edge_id}: {len(lanes)} lanes")
    else:
        print(f"{edge_id}: NOT FOUND")
