@echo off
REM Start the FastAPI server for RSU-based V2I system
echo ============================================================
echo Starting FastAPI Server for RSU-based V2I System
echo ============================================================
echo.
echo Server will start on http://127.0.0.1:8000
echo.
echo API Documentation: http://127.0.0.1:8000/docs
echo RSU Statistics: http://127.0.0.1:8000/rsu_stats
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

uvicorn server:app --reload --host 127.0.0.1 --port 8000
