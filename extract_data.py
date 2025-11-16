"""
Extract data from RSU-based telemetry database
Exports data to Excel files for analysis
"""

import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "telemetry.db"

def extract_all_data():
    """Extract all data from the database"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        
        print("="*60)
        print("EXTRACTING DATA FROM RSU TELEMETRY DATABASE")
        print("="*60)
        print()
        
        # Extract RSU-based vehicle logs
        print("Extracting RSU vehicle logs...")
        df_rsu_logs = pd.read_sql_query("""
            SELECT * FROM rsu_vehicle_logs
            ORDER BY sim_time, rsu_id
        """, conn)
        
        # Extract RSU status
        print("Extracting RSU status data...")
        df_rsu_status = pd.read_sql_query("""
            SELECT * FROM rsu_status
            ORDER BY ts_utc
        """, conn)
        
        # Extract legacy vehicle logs (if any)
        print("Extracting legacy vehicle logs...")
        df_legacy_logs = pd.read_sql_query("""
            SELECT * FROM vehicle_logs
            ORDER BY sim_time
        """, conn)
        
        # Save to Excel with multiple sheets
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = f'rsu_telemetry_data_{timestamp}.xlsx'
        
        print(f"\nSaving data to {excel_file}...")
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df_rsu_logs.to_excel(writer, sheet_name='RSU_Vehicle_Logs', index=False)
            df_rsu_status.to_excel(writer, sheet_name='RSU_Status', index=False)
            if len(df_legacy_logs) > 0:
                df_legacy_logs.to_excel(writer, sheet_name='Legacy_Logs', index=False)
        
        # Also save as CSV files
        csv_file_logs = f'rsu_vehicle_logs_{timestamp}.csv'
        csv_file_status = f'rsu_status_{timestamp}.csv'
        
        df_rsu_logs.to_csv(csv_file_logs, index=False)
        df_rsu_status.to_csv(csv_file_status, index=False)
        
        # Print summary statistics
        print("\n" + "="*60)
        print("DATA EXTRACTION SUMMARY")
        print("="*60)
        print(f"Total RSU Vehicle Records: {len(df_rsu_logs)}")
        print(f"Total RSU Status Records: {len(df_rsu_status)}")
        print(f"Total Legacy Records: {len(df_legacy_logs)}")
        print()
        
        if len(df_rsu_logs) > 0:
            print("Records per RSU:")
            print(df_rsu_logs.groupby('rsu_id').size().to_string())
            print()
            
            print("Unique Vehicles Tracked:", df_rsu_logs['vehicle_id'].nunique())
            print()
            
            print("Simulation Time Range:")
            print(f"  Start: {df_rsu_logs['sim_time'].min():.2f}s")
            print(f"  End: {df_rsu_logs['sim_time'].max():.2f}s")
            print(f"  Duration: {df_rsu_logs['sim_time'].max() - df_rsu_logs['sim_time'].min():.2f}s")
            print()
            
            print("Average Speed per RSU:")
            avg_speed = df_rsu_logs.groupby('rsu_id')['speed'].mean()
            print(avg_speed.to_string())
            print()
            
            print("Average Battery Charge per RSU:")
            avg_battery = df_rsu_logs.groupby('rsu_id')['battery_charge'].mean()
            print(avg_battery.to_string())
            print()
            
            if 'battery_percentage' in df_rsu_logs.columns:
                print("Average Battery Percentage per RSU:")
                avg_battery_pct = df_rsu_logs.groupby('rsu_id')['battery_percentage'].mean()
                print(avg_battery_pct.to_string())
                print()
                
                print("Battery Statistics:")
                print(f"  Minimum Battery %: {df_rsu_logs['battery_percentage'].min():.2f}%")
                print(f"  Maximum Battery %: {df_rsu_logs['battery_percentage'].max():.2f}%")
                print(f"  Average Battery %: {df_rsu_logs['battery_percentage'].mean():.2f}%")
                print()
        
        print("="*60)
        print("FILES CREATED:")
        print(f"  • {excel_file} (Excel with multiple sheets)")
        print(f"  • {csv_file_logs} (Vehicle logs CSV)")
        print(f"  • {csv_file_status} (RSU status CSV)")
        print("="*60)
        print("\n✅ Data extraction complete!")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    extract_all_data()
