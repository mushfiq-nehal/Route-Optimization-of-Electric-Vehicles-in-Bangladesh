@echo off
echo =====================================================
echo RSU-Based Vehicle Tracking System - Complete Test
echo =====================================================
echo.

echo Step 1: Starting FastAPI Server...
start "RSU Server" cmd /k python server.py
timeout /t 3 /nobreak > nul
echo Server started!
echo.

echo Step 2: Running SUMO Simulation with RSU Data Collection...
echo (SUMO GUI will open - vehicles should appear at simulation start)
echo.
python traCI_rsu.py
echo.

echo Step 3: Extracting collected data...
python extract_data.py
echo.

echo =====================================================
echo Test Complete!
echo =====================================================
echo.
echo Check the following:
echo - Excel file: rsu_data_*.xlsx
echo - CSV files: rsu_vehicle_logs_*.csv, rsu_status_*.csv
echo.
pause
