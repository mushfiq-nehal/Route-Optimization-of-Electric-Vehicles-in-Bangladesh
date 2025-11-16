@echo off
REM Run the RSU-based SUMO simulation
echo ============================================================
echo Starting RSU-based Vehicle-to-Infrastructure Simulation
echo ============================================================
echo.
echo Make sure the FastAPI server is running in another terminal!
echo.
echo This will:
echo   - Setup RSU network at 7 intersections
echo   - Clear old data from the server
echo   - Start SUMO simulation
echo   - Collect vehicle data via RSUs
echo   - Send data to server in batches
echo.
echo ============================================================
echo.

python traCI_rsu.py

echo.
echo ============================================================
echo Simulation Complete!
echo ============================================================
echo.
pause
