import sqlite3
import pandas as pd

conn = sqlite3.connect('telemetry.db')

# Get sample data
df = pd.read_sql_query("""
    SELECT vehicle_id, speed, battery_charge, battery_capacity, battery_percentage, sim_time
    FROM rsu_vehicle_logs
    ORDER BY sim_time
    LIMIT 10
""", conn)

print("="*80)
print("SAMPLE DATA - Battery Information")
print("="*80)
print(df.to_string(index=False))
print()

# Get statistics by vehicle type
print("="*80)
print("BATTERY STATISTICS BY VEHICLE TYPE")
print("="*80)

df_all = pd.read_sql_query("""
    SELECT vehicle_id, battery_charge, battery_capacity, battery_percentage
    FROM rsu_vehicle_logs
""", conn)

for vid in df_all['vehicle_id'].unique()[:5]:
    vehicle_data = df_all[df_all['vehicle_id'] == vid]
    print(f"\n{vid}:")
    print(f"  Battery Capacity: {vehicle_data['battery_capacity'].iloc[0]:.0f} Wh")
    print(f"  Current Charge: {vehicle_data['battery_charge'].iloc[0]:.0f} Wh")
    print(f"  Battery %: {vehicle_data['battery_percentage'].iloc[0]:.2f}%")

conn.close()
