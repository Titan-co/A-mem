"""
Test script for memory evolution
"""
from memory_system import AgenticMemorySystem
from config import settings
import time
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_memory_evolution():
    """Test the memory evolution functionality"""
    try:
        # Initialize the memory system
        logger.info("Initializing the memory system...")
        memory_system = AgenticMemorySystem(
            model_name=settings.MODEL_NAME,
            llm_backend=settings.LLM_BACKEND,
            llm_model=settings.LLM_MODEL,
            evo_threshold=3,  # Set to a low value for testing
            api_key=settings.API_KEY,
            api_base=settings.API_URL
        )
        logger.info("Memory system initialized successfully")
        
        # Create a set of related memories to trigger evolution
        logger.info("Creating related memories to test evolution...")
        
        # Create first memory
        content1 = "Machine learning is a type of artificial intelligence that allows software applications to become more accurate at predicting outcomes without being explicitly programmed to do so."
        memory_id1 = memory_system.create(
            content=content1,
            tags=["AI", "machine learning"],
            category="Technology"
        )
        logger.info(f"Created memory 1 with ID: {memory_id1}")
        
        # Let's retrieve the memory to see its metadata
        memory1 = memory_system.read(memory_id1)
        logger.info(f"Memory 1 - Tags: {memory1.tags}, Context: {memory1.context}")
        
        # Create second memory
        content2 = "Deep learning is a subset of machine learning that uses neural networks with many layers to analyze various factors of data."
        memory_id2 = memory_system.create(
            content=content2,
            tags=["AI", "deep learning", "neural networks"],
            category="Technology"
        )
        logger.info(f"Created memory 2 with ID: {memory_id2}")
        
        # Let's retrieve the memory to see its metadata
        memory2 = memory_system.read(memory_id2)
        logger.info(f"Memory 2 - Tags: {memory2.tags}, Context: {memory2.context}")
        
        # Create third memory that should trigger evolution
        content3 = "Neural networks are computing systems inspired by the biological neural networks that constitute animal brains. They are a key component of modern machine learning systems."
        memory_id3 = memory_system.create(
            content=content3,
            tags=["AI", "neural networks", "biology"],
            category="Technology"
        )
        logger.info(f"Created memory 3 with ID: {memory_id3}")
        
        # Let's retrieve the memory to see its metadata
        memory3 = memory_system.read(memory_id3)
        logger.info(f"Memory 3 - Tags: {memory3.tags}, Context: {memory3.context}")
        
        # Now check if the memories have been evolved
        logger.info("Checking if memories have evolved...")
        
        # Re-read the memories
        memory1 = memory_system.read(memory_id1)
        memory2 = memory_system.read(memory_id2)
        memory3 = memory_system.read(memory_id3)
        
        logger.info(f"Memory 1 - Tags: {memory1.tags}, Context: {memory1.context}")
        logger.info(f"Memory 2 - Tags: {memory2.tags}, Context: {memory2.context}")
        logger.info(f"Memory 3 - Tags: {memory3.tags}, Context: {memory3.context}")
        
        # Check if any links were created
        logger.info(f"Memory 1 - Links: {memory1.links}")
        logger.info(f"Memory 2 - Links: {memory2.links}")
        logger.info(f"Memory 3 - Links: {memory3.links}")
        
        logger.info("Memory evolution test completed")
        return True
    except Exception as e:
        logger.error(f"Error in memory evolution test: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Testing A-MEM Memory Evolution")
    logger.info("=" * 50)
    
    result = test_memory_evolution()
    
    logger.info("\nTest result: %s", "SUCCESS" if result else "FAILED")
