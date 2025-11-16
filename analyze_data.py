"""
Analyze RSU-based telemetry data
Generates statistics and visualizations
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

DB_PATH = "telemetry.db"

def analyze_data():
    """Perform comprehensive data analysis"""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        print("="*60)
        print("RSU TELEMETRY DATA ANALYSIS")
        print("="*60)
        print()
        
        # Analysis 1: Vehicle Statistics by RSU
        print("1️⃣  VEHICLE STATISTICS BY RSU")
        print("-" * 60)
        df_by_rsu = pd.read_sql_query("""
            SELECT 
                rsu_id,
                COUNT(DISTINCT vehicle_id) as unique_vehicles,
                COUNT(*) as total_records,
                AVG(speed) as avg_speed,
                MAX(speed) as max_speed,
                MIN(speed) as min_speed,
                AVG(battery_charge) as avg_battery,
                MIN(battery_charge) as min_battery
            FROM rsu_vehicle_logs
            GROUP BY rsu_id
            ORDER BY total_records DESC
        """, conn)
        
        if len(df_by_rsu) > 0:
            print(df_by_rsu.to_string(index=False))
            print()
        else:
            print("No data available.\n")
            return
        
        # Analysis 2: RSU Performance
        print("2️⃣  RSU PERFORMANCE METRICS")
        print("-" * 60)
        rsu_perf = pd.read_sql_query("""
            SELECT 
                rsu_id,
                SUM(vehicle_count) as total_vehicles_served,
                SUM(data_records) as total_transmissions,
                COUNT(*) as transmission_events,
                AVG(data_records) as avg_batch_size
            FROM rsu_status
            GROUP BY rsu_id
            ORDER BY total_transmissions DESC
        """, conn)
        print(rsu_perf.to_string(index=False))
        print()
        
        # Analysis 3: Vehicle-specific Analysis
        print("3️⃣  VEHICLE TRAJECTORY ANALYSIS")
        print("-" * 60)
        vehicle_stats = pd.read_sql_query("""
            SELECT 
                vehicle_id,
                COUNT(DISTINCT rsu_id) as rsus_visited,
                COUNT(*) as data_points,
                MIN(battery_charge) as min_battery,
                MAX(battery_charge) as max_battery,
                (MAX(battery_charge) - MIN(battery_charge)) as battery_consumed,
                AVG(speed) as avg_speed,
                MIN(sim_time) as first_seen,
                MAX(sim_time) as last_seen,
                (MAX(sim_time) - MIN(sim_time)) as travel_time
            FROM rsu_vehicle_logs
            GROUP BY vehicle_id
            ORDER BY data_points DESC
            LIMIT 10
        """, conn)
        print("Top 10 Vehicles by Data Points:")
        print(vehicle_stats.to_string(index=False))
        print()
        
        # Analysis 4: Time-based Analysis
        print("4️⃣  TEMPORAL ANALYSIS")
        print("-" * 60)
        time_stats = pd.read_sql_query("""
            SELECT 
                CAST(sim_time / 60 AS INTEGER) as minute,
                COUNT(*) as records,
                COUNT(DISTINCT vehicle_id) as active_vehicles,
                AVG(speed) as avg_speed,
                AVG(battery_charge) as avg_battery
            FROM rsu_vehicle_logs
            GROUP BY minute
            ORDER BY minute
        """, conn)
        print(f"Data collected over {len(time_stats)} minute intervals")
        if len(time_stats) > 0:
            print(f"Peak activity at minute {time_stats.loc[time_stats['records'].idxmax(), 'minute']} with {time_stats['records'].max()} records")
            print()
        
        # Generate Visualizations
        print("5️⃣  GENERATING VISUALIZATIONS")
        print("-" * 60)
        
        # Plot 1: Records per RSU
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Chart 1: Records per RSU
        df_by_rsu.plot(x='rsu_id', y='total_records', kind='bar', ax=axes[0, 0], color='steelblue')
        axes[0, 0].set_title('Total Records Collected per RSU', fontweight='bold')
        axes[0, 0].set_xlabel('RSU ID')
        axes[0, 0].set_ylabel('Number of Records')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # Chart 2: Average Speed per RSU
        df_by_rsu.plot(x='rsu_id', y='avg_speed', kind='bar', ax=axes[0, 1], color='coral')
        axes[0, 1].set_title('Average Vehicle Speed per RSU', fontweight='bold')
        axes[0, 1].set_xlabel('RSU ID')
        axes[0, 1].set_ylabel('Speed (m/s)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # Chart 3: Battery levels per RSU
        df_by_rsu.plot(x='rsu_id', y='avg_battery', kind='bar', ax=axes[1, 0], color='green')
        axes[1, 0].set_title('Average Battery Charge per RSU', fontweight='bold')
        axes[1, 0].set_xlabel('RSU ID')
        axes[1, 0].set_ylabel('Battery Charge')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(axis='y', alpha=0.3)
        
        # Chart 4: Activity over time
        if len(time_stats) > 0:
            axes[1, 1].plot(time_stats['minute'], time_stats['active_vehicles'], 
                           marker='o', linewidth=2, markersize=6, color='purple')
            axes[1, 1].set_title('Active Vehicles Over Time', fontweight='bold')
            axes[1, 1].set_xlabel('Simulation Time (minutes)')
            axes[1, 1].set_ylabel('Number of Active Vehicles')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_file = f'rsu_analysis_{timestamp}.png'
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        print(f"✅ Charts saved to {chart_file}")
        
        # Plot 2: Battery discharge for top vehicles
        top_vehicles = vehicle_stats.head(5)['vehicle_id'].tolist()
        
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        
        for vehicle in top_vehicles:
            df_vehicle = pd.read_sql_query(f"""
                SELECT sim_time, battery_charge
                FROM rsu_vehicle_logs
                WHERE vehicle_id = '{vehicle}'
                ORDER BY sim_time
            """, conn)
            
            if len(df_vehicle) > 0:
                ax2.plot(df_vehicle['sim_time'], df_vehicle['battery_charge'], 
                        marker='o', markersize=4, label=vehicle, linewidth=2)
        
        ax2.set_title('Battery Discharge Over Time (Top 5 Vehicles)', fontweight='bold', fontsize=14)
        ax2.set_xlabel('Simulation Time (s)', fontsize=12)
        ax2.set_ylabel('Battery Charge', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        plt.tight_layout()
        
        battery_file = f'battery_discharge_{timestamp}.png'
        plt.savefig(battery_file, dpi=300, bbox_inches='tight')
        print(f"✅ Battery chart saved to {battery_file}")
        
        # Export summary report
        report_file = f'analysis_report_{timestamp}.txt'
        with open(report_file, 'w') as f:
            f.write("="*60 + "\n")
            f.write("RSU TELEMETRY DATA ANALYSIS REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            f.write("VEHICLE STATISTICS BY RSU\n")
            f.write("-" * 60 + "\n")
            f.write(df_by_rsu.to_string(index=False) + "\n\n")
            
            f.write("RSU PERFORMANCE METRICS\n")
            f.write("-" * 60 + "\n")
            f.write(rsu_perf.to_string(index=False) + "\n\n")
            
            f.write("TOP 10 VEHICLES\n")
            f.write("-" * 60 + "\n")
            f.write(vehicle_stats.to_string(index=False) + "\n\n")
        
        print(f"✅ Report saved to {report_file}")
        
        print()
        print("="*60)
        print("ANALYSIS COMPLETE!")
        print("="*60)
        
        conn.close()
        plt.show()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_data()
