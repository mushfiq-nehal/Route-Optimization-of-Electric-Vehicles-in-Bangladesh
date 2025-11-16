"""
Quick test to verify the RSU system is working
This script checks all components and shows what needs to be done
"""

import os
import sqlite3

def check_database():
    """Check if database exists and has data"""
    print("="*60)
    print("CHECKING DATABASE")
    print("="*60)
    
    if not os.path.exists('telemetry.db'):
        print("❌ Database does not exist yet")
        print("   → Run the simulation first to create it")
        return False
    
    print("✅ Database file exists")
    
    conn = sqlite3.connect('telemetry.db')
    cur = conn.cursor()
    
    # Check each table
    tables = ['rsu_vehicle_logs', 'rsu_status', 'vehicle_logs']
    has_data = False
    
    for table in tables:
        try:
            cur.execute(f'SELECT COUNT(*) FROM {table}')
            count = cur.fetchone()[0]
            if count > 0:
                print(f"✅ {table}: {count} records")
                has_data = True
            else:
                print(f"⚠️  {table}: 0 records (empty)")
        except sqlite3.Error as e:
            print(f"❌ {table}: Error - {e}")
    
    conn.close()
    print()
    return has_data

def check_files():
    """Check if all required files exist"""
    print("="*60)
    print("CHECKING REQUIRED FILES")
    print("="*60)
    
    required_files = {
        'rsu.py': 'RSU module',
        'server.py': 'FastAPI server',
        'traCI_rsu.py': 'RSU-based simulation script',
        'CustomRoadNetwork.sumocfg': 'SUMO configuration'
    }
    
    all_present = True
    for file, desc in required_files.items():
        if os.path.exists(file):
            print(f"✅ {file:<30} ({desc})")
        else:
            print(f"❌ {file:<30} ({desc}) - MISSING!")
            all_present = False
    
    print()
    return all_present

def check_dependencies():
    """Check if required Python packages are installed"""
    print("="*60)
    print("CHECKING PYTHON PACKAGES")
    print("="*60)
    
    packages = {
        'fastapi': 'FastAPI web framework',
        'uvicorn': 'ASGI server',
        'pydantic': 'Data validation',
        'requests': 'HTTP library',
        'pandas': 'Data analysis',
        'openpyxl': 'Excel support',
        'matplotlib': 'Plotting',
        'traci': 'SUMO interface'
    }
    
    missing = []
    for package, desc in packages.items():
        try:
            __import__(package)
            print(f"✅ {package:<15} ({desc})")
        except ImportError:
            print(f"❌ {package:<15} ({desc}) - NOT INSTALLED!")
            missing.append(package)
    
    print()
    
    if missing:
        print("⚠️  Missing packages. Install with:")
        print(f"   pip install {' '.join(missing)}")
        print()
    
    return len(missing) == 0

def show_instructions():
    """Show what to do next"""
    print("="*60)
    print("WHAT TO DO NEXT")
    print("="*60)
    print()
    print("The database is EMPTY because the simulation hasn't been run yet.")
    print()
    print("To collect data, follow these steps:")
    print()
    print("STEP 1: Start the Server (in a separate terminal)")
    print("   PowerShell Terminal 1:")
    print("   > uvicorn server:app --reload")
    print()
    print("   OR use the batch file:")
    print("   > .\\start_server.bat")
    print()
    print("   You should see: 'Uvicorn running on http://127.0.0.1:8000'")
    print()
    print("STEP 2: Run the RSU Simulation (in another terminal)")
    print("   PowerShell Terminal 2:")
    print("   > python traCI_rsu.py")
    print()
    print("   OR use the batch file:")
    print("   > .\\run_simulation.bat")
    print()
    print("   This will:")
    print("   • Setup 7 RSUs at intersections")
    print("   • Open SUMO GUI with the simulation")
    print("   • Collect vehicle data every 10 seconds")
    print("   • Send data to server via RSUs")
    print()
    print("STEP 3: Let the simulation run")
    print("   • Watch vehicles move in SUMO GUI")
    print("   • Monitor console for data collection messages")
    print("   • Wait for simulation to complete or stop it manually")
    print()
    print("STEP 4: Extract your data")
    print("   > python extract_data.py")
    print()
    print("   This creates Excel/CSV files with all collected data")
    print()
    print("="*60)
    print()

def main():
    print()
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "RSU SYSTEM STATUS CHECK" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    print()
    
    # Check all components
    files_ok = check_files()
    deps_ok = check_dependencies()
    has_data = check_database()
    
    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    
    if not files_ok:
        print("❌ Some required files are missing")
    elif not deps_ok:
        print("❌ Some Python packages need to be installed")
    elif not has_data:
        print("⚠️  System is ready but NO DATA has been collected yet")
        print()
        show_instructions()
    else:
        print("✅ System is ready and has data!")
        print()
        print("You can now run:")
        print("   > python extract_data.py")
        print("   > python analyze_data.py")
    
    print("="*60)

if __name__ == "__main__":
    main()
