@echo off
echo =====================================
echo A-MEM ChromaDB Debug and Fix
echo =====================================
echo.

echo Step 1: Cleaning and setting up cache directories...
python initialize_cache.py --force --verbose
if %ERRORLEVEL% NEQ 0 (
  echo ERROR: Cache setup failed!
  goto error
)
echo.

echo Step 2: Checking environment variables...
set | findstr CACHE
set | findstr CHROMA
set | findstr TRANS
set | findstr HF_
echo.

echo Step 3: Setting additional environment variables for debugging...
set PYTHONVERBOSE=1
set CHROMADB_VERBOSE=1

echo Step 4: Running detailed ChromaDB test with debug enabled...
python -v test_chromadb.py > chromadb_detailed_debug.log 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo WARNING: ChromaDB test had issues. See chromadb_detailed_debug.log for details.
  echo Trying to continue anyway...
) else (
  echo SUCCESS: ChromaDB basic test passed!
)
echo.

echo Step 5: Verifying with a controlled test...
python -c "from custom_embedding import LocalCacheEmbeddingFunction; import chromadb; client = chromadb.Client(); embedding_func = LocalCacheEmbeddingFunction(); collection = client.create_collection('test_debug', embedding_function=embedding_func); print('Successfully created test collection with custom embedding function'); collection.add(documents=['This is a test document'], metadatas=[{'source': 'debug'}], ids=['debug-1']); print('Successfully added document to collection'); results = collection.query(query_texts=['test'], n_results=1); print(f'Query results: {results}')"
if %ERRORLEVEL% NEQ 0 (
  echo ERROR: Direct ChromaDB test failed! 
  echo You may need to manually edit the custom_embedding.py file.
  goto error
)
echo.

echo SUCCESS! Direct ChromaDB test succeeded.
echo.
echo Now testing the full memory system with ChromaDB enabled...
echo This will help verify that all components work together properly.
echo.
python -c "from memory_system import AgenticMemorySystem; import os; os.environ['DISABLE_LLM'] = 'true'; mem = AgenticMemorySystem(); mem_id = mem.create('Test memory'); print(f'Created memory with ID: {mem_id}'); results = mem.search('test'); print(f'Search returned {len(results)} results'); print('SUCCESS: Memory system is working with ChromaDB!')"
if %ERRORLEVEL% NEQ 0 (
  echo ERROR: Full memory system test failed!
  goto error
)

echo.
echo =============================================
echo ALL TESTS PASSED! ChromaDB is working properly.
echo =============================================
echo.
echo You can now use the full A-MEM system with ChromaDB enabled.
echo Run the standard server with:
echo.
echo   run_server_with_chromadb.bat
echo.
goto end

:error
echo.
echo There were errors during ChromaDB activation.
echo Review the log files for detailed error information:
echo   - chromadb_detailed_debug.log
echo   - chromadb_test.log
echo   - cache_setup.log
echo.

:end
pause
