import os
import time
import requests
import pandas as pd
import traci

# Constants
INGEST_URL = "http://127.0.0.1:8000/ingest"  # Change to your server IP:port if remote
BATCH_SIZE = 200
log_data, send_buffer = [], []

# URL to clear data from the FastAPI server
clear_data_url = "http://127.0.0.1:8000/clear_data"

# Function to send a batch of data to the server
def send_batch(rows):
    """Send a batch to the server; return True on success, False on failure."""
    if not rows:
        return True
    payload = [
        {
            "vehicle_id": r["Vehicle ID"],
            "speed": r["Speed (m/s)"],
            "battery_charge": r["Battery Charge"],
            "battery_capacity": str(r["Battery Capacity"]) if r["Battery Capacity"] is not None else None,
            "sim_time": r["Time (s)"]
        } for r in rows
    ]
    try:
        r = requests.post(INGEST_URL, json=payload, timeout=5)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"[WARN] Failed to send batch ({len(rows)} rows): {e}")
        return False

# Function to clear data from the server (called before the simulation starts)
def clear_data_before_run():
    try:
        # Send DELETE request to the server to clear previous data
        response = requests.delete(clear_data_url)
        response.raise_for_status()  # Ensure there were no errors
        print("Data cleared successfully before the run.")  # Confirm successful clearing
    except requests.exceptions.RequestException as e:
        print(f"Error clearing data: {e}")  # Print error if the request fails

# Start SUMO connection
def start_simulation():
    traci.start(["sumo-gui", "-c", "CustomRoadNetwork.sumocfg"])  # Use sumo-gui to open the simulation window

# Function to run simulation steps
def run_simulation():
    global log_data, send_buffer
    last_log_time = 0  # Track the last time we logged data
    
    while traci.simulation.getMinExpectedNumber() > 0:
        try:
            traci.simulationStep()
            sim_time = traci.simulation.getTime()

            # Log data every 10 seconds
            if sim_time - last_log_time >= 10:  # Check if 10 seconds have passed
                vehicle_ids = traci.vehicle.getIDList()

                for vid in vehicle_ids:
                    speed = traci.vehicle.getSpeed(vid)
                    if traci.vehicle.getWaitingTime(vid) > 0:
                        speed = 0.0

                    # Get battery parameters
                    battery_capacity = traci.vehicle.getParameter(vid, "device.battery.capacity")
                    battery_charge = float(traci.vehicle.getParameter(vid, "device.battery.actualBatteryCapacity"))

                    # Simple consumption model
                    consumption_rate = 0.01
                    battery_charge = max(0.0, battery_charge - speed * consumption_rate)

                    # Log the row data
                    row = {
                        'Vehicle ID': vid,
                        'Speed (m/s)': speed,
                        'Battery Charge': battery_charge,
                        'Battery Capacity': battery_capacity,
                        'Time (s)': sim_time
                    }

                    log_data.append(row)
                    send_buffer.append(row)

                    # Send when we reach BATCH_SIZE
                    if len(send_buffer) >= BATCH_SIZE:
                        if send_batch(send_buffer):
                            send_buffer.clear()  # Sent successfully
                        else:
                            # Keep the buffer; we’ll retry next time (don’t clear)
                            pass

                # Update the last log time to the current time
                last_log_time = sim_time

        except Exception as e:
            print(f"Error during simulation step: {e}")

    # After the loop, try to flush any remaining rows
    if send_buffer:
        if send_batch(send_buffer):
            send_buffer.clear()

    # Fallback: if anything remained unsent, export to Excel so you don’t lose data
    if send_buffer:
        print("[WARN] Some data could not be sent; writing fallback Excel file.")
        df = pd.DataFrame(log_data)
        df.to_excel("vehicle_data_log_fallback.xlsx", index=False)
    else:
        print("All data sent to server successfully.")

# Main function
def main():
    try:
        # Clear old data from the server before starting the simulation
        clear_data_before_run()  # Clear data from the server

        start_simulation()  # Start the simulation
        run_simulation()    # Run the simulation and collect data
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        traci.close()  # Close the SUMO connection

if __name__ == "__main__":
    main()
