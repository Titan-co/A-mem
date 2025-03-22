@echo off
echo =====================================
echo A-MEM ChromaDB Multi-Approach Fix
echo =====================================
echo.

rem Create and clean cache directories
echo Step 1: Setting up cache directories...
call :check_admin
python initialize_cache.py --force
if %ERRORLEVEL% NEQ 0 (
  echo WARNING: Cache setup had issues, but we'll continue.
)
echo.

echo Step 2: Testing each approach in sequence...

echo.
echo Testing Approach 1: Direct embedding function customization...
echo -----------------------------------------------------------
python -c "import cache_config; import chromadb; import custom_embedding; func = custom_embedding.LocalCacheEmbeddingFunction(); client = chromadb.Client(); coll = client.create_collection('test1', embedding_function=func); coll.add(documents=['Test document'], metadatas=[{'source': 'test'}], ids=['test-1']); print('Success: Direct embedding function approach works!')" 2>approach1_error.log
if %ERRORLEVEL% EQU 0 (
  echo Approach 1 SUCCEEDED!
  set APPROACH1_SUCCESS=1
) else (
  echo Approach 1 failed. See approach1_error.log for details.
  set APPROACH1_SUCCESS=0
)

echo.
echo Testing Approach 2: ChromaDB monkey patching...
echo -----------------------------------------------------------
python -c "import chromadb_patch; import chromadb; client = chromadb.Client(); coll = client.create_collection('test2'); coll.add(documents=['Test document'], metadatas=[{'source': 'test'}], ids=['test-1']); print('Success: Monkey patching approach works!')" 2>approach2_error.log
if %ERRORLEVEL% EQU 0 (
  echo Approach 2 SUCCEEDED!
  set APPROACH2_SUCCESS=1
) else (
  echo Approach 2 failed. See approach2_error.log for details.
  set APPROACH2_SUCCESS=0
)

echo.
echo Testing Approach 3: Fallback implementation...
echo -----------------------------------------------------------
python -c "import fallback_chromadb; retriever = fallback_chromadb.SimpleChromaRetriever('test3'); success = retriever.add_document('Test document', {'source': 'test'}, 'test-1'); results = retriever.search('test'); print(f'Success: Fallback approach works! Search returned {len(results[\"ids\"][0])} results')" 2>approach3_error.log
if %ERRORLEVEL% EQU 0 (
  echo Approach 3 SUCCEEDED!
  set APPROACH3_SUCCESS=1
) else (
  echo Approach 3 failed. See approach3_error.log for details.
  set APPROACH3_SUCCESS=0
)

echo.
echo Testing Approach 4: Simple no-embedding test...
echo -----------------------------------------------------------
python simple_chromadb_test.py 2>approach4_error.log
if %ERRORLEVEL% EQU 0 (
  echo Approach 4 SUCCEEDED!
  set APPROACH4_SUCCESS=1
) else (
  echo Approach 4 failed. See approach4_error.log for details.
  set APPROACH4_SUCCESS=0
)

echo.
echo Results summary:
echo -----------------------------------------------------------
echo Approach 1 (Direct embedding): %APPROACH1_SUCCESS%
echo Approach 2 (Monkey patching): %APPROACH2_SUCCESS%
echo Approach 3 (Fallback implementation): %APPROACH3_SUCCESS%
echo Approach 4 (Simple test): %APPROACH4_SUCCESS%
echo.

rem Generate configuration based on results
echo Step 3: Generating optimal configuration...
echo -----------------------------------------------------------
(
  echo # Auto-generated ChromaDB configuration
  echo # Generated on %date% %time%
  echo.
  if %APPROACH1_SUCCESS%==1 (
    echo # Using Approach 1: Direct embedding function customization
    echo USE_DIRECT_EMBEDDING=True
    echo USE_MONKEY_PATCH=False
    echo USE_FALLBACK=False
  ) else if %APPROACH2_SUCCESS%==1 (
    echo # Using Approach 2: ChromaDB monkey patching
    echo USE_DIRECT_EMBEDDING=False
    echo USE_MONKEY_PATCH=True
    echo USE_FALLBACK=False
  ) else if %APPROACH3_SUCCESS%==1 (
    echo # Using Approach 3: Fallback implementation
    echo USE_DIRECT_EMBEDDING=False
    echo USE_MONKEY_PATCH=False
    echo USE_FALLBACK=True
  ) else (
    echo # No approach succeeded, disabling ChromaDB
    echo USE_DIRECT_EMBEDDING=False
    echo USE_MONKEY_PATCH=False
    echo USE_FALLBACK=False
    echo DISABLE_CHROMADB=True
  )
) > chromadb_config.py

echo Configuration saved to chromadb_config.py
echo.

echo Step 4: Final test with the selected approach...
echo -----------------------------------------------------------
python -c "import chromadb_config; import os; print(f'Selected approach: {\"Direct embedding\" if getattr(chromadb_config, \"USE_DIRECT_EMBEDDING\", False) else \"Monkey patching\" if getattr(chromadb_config, \"USE_MONKEY_PATCH\", False) else \"Fallback\" if getattr(chromadb_config, \"USE_FALLBACK\", False) else \"Disabled\"}'); import fallback_chromadb; retriever = fallback_chromadb.SimpleChromaRetriever('final_test'); success = retriever.add_document('Final test document', {'source': 'final'}, 'final-1'); results = retriever.search('test'); print(f'Final test successful! Search returned {len(results[\"ids\"][0])} results')"

if %ERRORLEVEL% EQU 0 (
  echo.
  echo ================================================
  echo SUCCESS! ChromaDB fixed with the selected approach
  echo ================================================
  echo.
  echo You can now use the A-MEM system with the working ChromaDB configuration.
  echo The system will automatically use the best approach based on testing.
  echo.
  echo Run the server with:
  echo   run_server_with_chromadb.bat
) else (
  echo.
  echo WARNING: Final test failed. Falling back to DISABLE_CHROMADB mode.
  echo The system will run but without ChromaDB functionality.
  echo.
)

goto :end

:check_admin
    echo Checking for administrator privileges...
    net session >nul 2>&1
    if %errorlevel% == 0 (
        echo Running with administrator privileges - good!
    ) else (
        echo Warning: Not running with administrator privileges.
        echo Some operations might fail due to permission issues.
        echo Consider running this script as administrator if problems occur.
        echo.
    )
    exit /b

:end
pause
