cd D:\MCP\A-mem
Write-Host "Running Python diagnostic checks..." -ForegroundColor Green

Write-Host "Python environment:" -ForegroundColor Yellow
$pythonPath = "C:\Users\zsun2\AppData\Local\Programs\Python\Python312\python.exe"
& $pythonPath -c "import sys; print('Python version:', sys.version); print('Executable:', sys.executable); print('Path:', sys.path)"

Write-Host "`nChecking for required modules:" -ForegroundColor Yellow
$modules = @("fastapi", "uvicorn", "pydantic", "dotenv", "nltk", "openai", "sentence_transformers", "chromadb")
foreach ($module in $modules) {
    try {
        & $pythonPath -c "import $module; print(f'Module {$module} is available, version:', getattr($module, '__version__', 'unknown'))"
    }
    catch {
        Write-Host "Module $module could not be imported" -ForegroundColor Red
    }
}

Write-Host "`nChecking if server.py exists:" -ForegroundColor Yellow
if (Test-Path "server.py") {
    Write-Host "server.py exists" -ForegroundColor Green
    $content = Get-Content "server.py" -Raw
    Write-Host "First 100 characters of server.py:" -ForegroundColor Yellow
    Write-Host $content.Substring(0, [Math]::Min(100, $content.Length))
}
else {
    Write-Host "server.py does not exist!" -ForegroundColor Red
}

Write-Host "`nListing directory contents:" -ForegroundColor Yellow
Get-ChildItem

Write-Host "`nAttempting to start the server with verbose logging..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
& $pythonPath -m uvicorn server:app --host 0.0.0.0 --port 8000 --log-level debug
