from memory_system import AgenticMemorySystem, MemoryNote
from config import settings
import traceback
import time

def test_memory_without_llm():
    """Test basic memory operations without relying on LLM for content analysis"""
    try:
        print("Creating simplified memory system...")
        
        # Initialize memory system
        memory_system = AgenticMemorySystem(
            model_name=settings.MODEL_NAME,
            llm_backend=settings.LLM_BACKEND,
            llm_model=settings.LLM_MODEL,
            evo_threshold=settings.EVO_THRESHOLD,
            api_key=settings.API_KEY,
            api_base=settings.API_URL
        )
        
        # Override the analyze_content method to avoid using LLM
        def mock_analyze_content(content):
            print("Using mock content analysis (no LLM call)")
            return {
                "keywords": ["test", "memory", "mock"],
                "context": "Testing without LLM",
                "tags": ["test", "no-llm"]
            }
        
        # Replace the real method with our mock
        memory_system.analyze_content = mock_analyze_content
        
        print("Memory system initialized with mock content analysis")
        
        # Test basic memory operations
        print("\nTesting basic memory operations...")
        try:
            # Create a test memory
            content = f"Test memory created at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            print(f"Creating memory with content: {content}")
            memory_id = memory_system.create(content=content)
            print(f"Created memory with ID: {memory_id}")
            
            # Read the created memory
            memory = memory_system.read(memory_id)
            print(f"Retrieved memory: {memory.content}")
            print(f"Keywords: {memory.keywords}")
            print(f"Tags: {memory.tags}")
            print(f"Context: {memory.context}")
            
            # Search for memories
            print("\nSearching for memories...")
            results = memory_system.search("test", k=5)
            print(f"Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"Result {i}: {result.get('content', 'No content')} (Score: {result.get('score', 0)})")
            
            # Delete the test memory
            print("\nDeleting test memory...")
            success = memory_system.delete(memory_id)
            print(f"Deletion successful: {success}")
            
            print("\nAll memory operations completed successfully!")
            return True
        except Exception as e:
            print(f"Error in memory operations: {e}")
            print(traceback.format_exc())
            return False
            
    except Exception as e:
        print(f"Error setting up memory system: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing A-MEM Memory System Without LLM")
    print("=" * 50)
    result = test_memory_without_llm()
    print("\nTest result:", "SUCCESS" if result else "FAILED")
