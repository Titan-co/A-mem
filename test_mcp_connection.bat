@echo off
echo =====================================
echo A-MEM MCP Connection Test
echo =====================================
echo.

echo This script will test the MCP connection with the wrapper.
echo Ensure the server is running first (start_server.bat).
echo.

set SERVER_PORT=8903
set PORT=%1
if "%PORT%"=="" set PORT=8767

echo Using server port: %SERVER_PORT%
echo Using connector port: %PORT%
echo.

echo Starting connection test...
echo This will run several tests to verify the connection works properly.
echo.

:: Set environment variables for the connector
set PYTHONUNBUFFERED=1
set PYTHONPATH=%CD%
set MCP_KEEP_ALIVE=true
set SERVER_PORT=%SERVER_PORT%

:: Run the test
python mcp_connection_test.py | python connector_mcp_wrapper.py

echo.
echo Test complete. Check the output above for any errors.
if %ERRORLEVEL% EQU 0 (
  echo TEST PASSED: MCP connection is working properly.
) else (
  echo TEST FAILED: MCP connection has issues (error code %ERRORLEVEL%).
  echo See logs for details.
)
echo.
pause
