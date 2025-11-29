"""
Export Enhanced Traffic Density Data from RSU Buffers
Saves the buffered traffic data to JSON format with all enhanced fields
"""

import json
import time
import traci
from datetime import datetime
from traCI_rsu import setup_rsu_network

def export_buffered_rsu_data():
    """
    Export the buffered RSU data with enhanced traffic density fields
    """
    print("="*60)
    print("EXPORTING ENHANCED TRAFFIC DENSITY DATA")
    print("="*60)
    
    # Setup RSU network (this loads the existing buffered data)
    rsu_network = setup_rsu_network()
    
    all_data = []
    total_records = 0
    
    # Collect data from all RSUs
    for rsu in rsu_network.rsus:
        rsu_data = {
            'rsu_id': rsu.rsu_id,
            'rsu_position': rsu.position,
            'connected_vehicles': len(rsu.connected_vehicles),
            'buffered_records': len(rsu.vehicle_buffer),
            'vehicle_data': rsu.vehicle_buffer
        }
        
        all_data.append(rsu_data)
        total_records += len(rsu.vehicle_buffer)
        
        print(f"RSU {rsu.rsu_id}: {len(rsu.vehicle_buffer)} records")
    
    # Save to JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f'enhanced_traffic_density_data_{timestamp}.json'
    
    with open(json_file, 'w') as f:
        json.dump(all_data, f, indent=2, default=str)
    
    # Save flattened CSV data
    csv_file = f'enhanced_traffic_density_flat_{timestamp}.csv'
    
    # Extract all vehicle records and flatten them
    flat_records = []
    for rsu_data in all_data:
        for record in rsu_data['vehicle_data']:
            flat_record = {
                'rsu_id': rsu_data['rsu_id'],
                'rsu_position_x': rsu_data['rsu_position'][0],
                'rsu_position_y': rsu_data['rsu_position'][1],
                **record  # Spread all vehicle data fields
            }
            flat_records.append(flat_record)
    
    # Save to CSV
    if flat_records:
        import pandas as pd
        df = pd.DataFrame(flat_records)
        df.to_csv(csv_file, index=False)
        
        print("\n" + "="*60)
        print("ENHANCED DATA EXPORT SUMMARY")
        print("="*60)
        print(f"Total Records Exported: {len(flat_records)}")
        print(f"Active RSUs: {len([r for r in all_data if r['buffered_records'] > 0])}")
        print(f"Enhanced Fields Included:")
        print("  • vehicle_id, vehicle_type")
        print("  • edge_id, lane_id, lane_position")
        print("  • vehicles_ahead_count")
        print("  • same_direction_ahead") 
        print("  • distance_to_traffic_light")
        print("  • time_to_red_light")
        print("  • next_traffic_light")
        print("  • traffic_light_state")
        print("  • edge_occupancy_percentage")
        print("  • speed, battery_charge, battery_percentage")
        print("  • sim_time, position")
        
        if len(flat_records) > 0:
            sample_record = flat_records[0]
            print(f"\nSample Record Fields: {list(sample_record.keys())}")
            
            print(f"\nData Ranges:")
            print(f"  Vehicles Ahead: {df['vehicles_ahead_count'].min()}-{df['vehicles_ahead_count'].max()}")
            print(f"  Same Direction: {df['same_direction_ahead'].min()}-{df['same_direction_ahead'].max()}")
            print(f"  Edge Occupancy: {df['edge_occupancy_percentage'].min():.2f}%-{df['edge_occupancy_percentage'].max():.2f}%")
        
        print("="*60)
        print("FILES CREATED:")
        print(f"  • {json_file} (Structured JSON with RSU hierarchy)")
        print(f"  • {csv_file} (Flat CSV for analysis)")
        print("="*60)
        print("\n✅ Enhanced traffic density data export complete!")
        
        return csv_file, json_file
    else:
        print("❌ No data found to export")
        return None, None

if __name__ == "__main__":
    try:
        export_buffered_rsu_data()
    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()