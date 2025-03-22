@echo off
echo =====================================
echo A-MEM MCP Connection Test
echo =====================================
echo.

echo This script will test the MCP connection with the wrapper.
echo Ensure the server and connector are running first.
echo.

set PORT=%1
if "%PORT%"=="" set PORT=8767

echo Using port: %PORT%
echo.

echo Starting connection test...
echo This will run several tests to verify the connection works properly.
echo.

python mcp_connection_test.py | python connector_mcp_wrapper.py

echo.
echo Test complete. Check the output for any errors.
echo.
pause
