from fastapi import HTTPException
from typing import Dict, Any, List
from datetime import datetime
from memory_system import MemoryNote

def format_datetime() -> str:
    """Get current datetime in the format used by A-MEM (YYYYMMDDHHMM)"""
    return datetime.now().strftime("%Y%m%d%H%M")

def memory_note_to_dict(memory: MemoryNote) -> Dict[str, Any]:
    """Convert a MemoryNote object to a dictionary"""
    if not memory:
        return None
        
    return {
        "id": memory.id,
        "content": memory.content,
        "tags": memory.tags,
        "category": memory.category,
        "context": memory.context,
        "keywords": memory.keywords,
        "timestamp": memory.timestamp,
        "last_accessed": memory.last_accessed,
        "retrieval_count": memory.retrieval_count,
        "links": memory.links
    }

def handle_not_found(memory_id: str):
    """Raise a standard 404 exception for memory not found"""
    raise HTTPException(
        status_code=404,
        detail=f"Memory with ID {memory_id} not found"
    )

def handle_search_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process and standardize search results"""
    processed_results = []
    for result in results:
        processed_results.append({
            "id": result.get("id", ""),
            "content": result.get("content", ""),
            "context": result.get("context", ""),
            "keywords": result.get("keywords", []),
            "score": result.get("score", 0.0)
        })
    return processed_results
