from memory_system import AgenticMemorySystem
from config import settings
import traceback
import time

def test_memory_initialization():
    try:
        print("Attempting to initialize AgenticMemorySystem...")
        print(f"Settings: MODEL_NAME={settings.MODEL_NAME}, LLM_BACKEND={settings.LLM_BACKEND}, LLM_MODEL={settings.LLM_MODEL}")
        
        # Initialize the memory system
        memory_system = AgenticMemorySystem(
            model_name=settings.MODEL_NAME,
            llm_backend=settings.LLM_BACKEND,
            llm_model=settings.LLM_MODEL,
            evo_threshold=settings.EVO_THRESHOLD,
            api_key=settings.API_KEY
        )
        print("Memory system initialized successfully!")
        
        # Test basic memory operations
        print("\nTesting basic memory operations...")
        try:
            # Create a test memory
            content = f"Test memory created at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            print(f"Creating memory with content: {content}")
            memory_id = memory_system.create(content=content, tags=["test"])
            print(f"Created memory with ID: {memory_id}")
            
            # Read the created memory
            memory = memory_system.read(memory_id)
            print(f"Retrieved memory: {memory.content}")
            
            # Search for memories
            print("Searching for memories...")
            results = memory_system.search("test", k=5)
            print(f"Found {len(results)} results")
            
            # Delete the test memory
            print("Deleting test memory...")
            success = memory_system.delete(memory_id)
            print(f"Deletion successful: {success}")
            
            print("All memory operations completed successfully!")
        except Exception as e:
            print(f"Error in memory operations: {e}")
            print(traceback.format_exc())
        
        return True
    except Exception as e:
        print(f"Error initializing memory system: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing A-MEM Memory System Initialization")
    print("=" * 50)
    result = test_memory_initialization()
    print("\nTest result:", "SUCCESS" if result else "FAILED")
