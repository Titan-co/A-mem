from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional, List
from memory_system import AgenticMemorySystem, MemoryNote
from models import (
    MemoryCreateRequest, 
    MemoryUpdateRequest, 
    MemoryResponse, 
    MemorySearchResponse,
    MemorySearchResult,
    DeleteResponse
)
from utils import memory_note_to_dict, handle_not_found, handle_search_results
from config import settings

router = APIRouter(tags=["memories"])

# Dependency to get the memory system
def get_memory_system():
    # This would normally be initialized once at server startup
    # For demonstration, we're initializing it here
    yield memory_system

@router.post("/memories", response_model=MemoryResponse, status_code=201)
async def create_memory(
    request: MemoryCreateRequest,
    memory_system: AgenticMemorySystem = Depends(get_memory_system)
):
    """Create a new memory"""
    # Prepare kwargs for memory creation
    kwargs = request.model_dump(exclude_unset=True)
    
    # Create memory note
    memory_id = memory_system.create(**kwargs)
    
    # Retrieve the created memory
    memory = memory_system.read(memory_id)
    
    # Convert memory to response format
    return memory_note_to_dict(memory)

@router.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str = Path(..., description="The ID of the memory to retrieve"),
    memory_system: AgenticMemorySystem = Depends(get_memory_system)
):
    """Retrieve a memory by ID"""
    memory = memory_system.read(memory_id)
    
    if not memory:
        handle_not_found(memory_id)
        
    return memory_note_to_dict(memory)

@router.put("/memories/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    request: MemoryUpdateRequest,
    memory_id: str = Path(..., description="The ID of the memory to update"),
    memory_system: AgenticMemorySystem = Depends(get_memory_system)
):
    """Update an existing memory"""
    # Check if memory exists
    memory = memory_system.read(memory_id)
    if not memory:
        handle_not_found(memory_id)
    
    # Prepare update kwargs
    kwargs = request.model_dump(exclude_unset=True)
    kwargs["memory_id"] = memory_id
    
    # Update memory
    success = memory_system.update(**kwargs)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to update memory"
        )
    
    # Retrieve the updated memory
    updated_memory = memory_system.read(memory_id)
    return memory_note_to_dict(updated_memory)

@router.delete("/memories/{memory_id}", response_model=DeleteResponse)
async def delete_memory(
    memory_id: str = Path(..., description="The ID of the memory to delete"),
    memory_system: AgenticMemorySystem = Depends(get_memory_system)
):
    """Delete a memory by ID"""
    success = memory_system.delete(memory_id)
    
    if not success:
        handle_not_found(memory_id)
        
    return {"success": True, "message": f"Memory {memory_id} successfully deleted"}

@router.get("/search", response_model=MemorySearchResponse)
async def search_memories(
    query: str = Query(..., description="Search query text"),
    k: Optional[int] = Query(settings.DEFAULT_K, description="Maximum number of results to return"),
    memory_system: AgenticMemorySystem = Depends(get_memory_system)
):
    """Search for memories"""
    # Perform search
    results = memory_system.search(query, k)
    
    # Process results
    processed_results = handle_search_results(results)
    
    # Create response
    search_results = [MemorySearchResult(**result) for result in processed_results]
    return {"results": search_results}

# Initialize memory system
memory_system = AgenticMemorySystem(
    model_name=settings.MODEL_NAME,
    llm_backend=settings.LLM_BACKEND,
    llm_model=settings.LLM_MODEL,
    evo_threshold=settings.EVO_THRESHOLD,
    api_key=settings.API_KEY,
    api_base=settings.API_URL  # Pass API URL to the memory system
)
