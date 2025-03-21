from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class MemoryCreateRequest(BaseModel):
    """Request model for creating a new memory"""
    content: str = Field(..., description="The main text content of the memory")
    tags: Optional[List[str]] = Field(None, description="Classification tags for the memory")
    category: Optional[str] = Field(None, description="Classification category")
    timestamp: Optional[str] = Field(None, description="Creation time in format YYYYMMDDHHMM")

class MemoryUpdateRequest(BaseModel):
    """Request model for updating an existing memory"""
    content: Optional[str] = Field(None, description="The main text content of the memory")
    tags: Optional[List[str]] = Field(None, description="Classification tags for the memory")
    category: Optional[str] = Field(None, description="Classification category")
    context: Optional[str] = Field(None, description="The broader context or domain of the memory")
    keywords: Optional[List[str]] = Field(None, description="Key terms extracted from the content")

class MemoryResponse(BaseModel):
    """Response model for memory data"""
    id: str = Field(..., description="Unique identifier for the memory")
    content: str = Field(..., description="The main text content of the memory")
    tags: List[str] = Field(default_factory=list, description="Classification tags for the memory")
    category: str = Field("Uncategorized", description="Classification category")
    context: str = Field("General", description="The broader context or domain of the memory")
    keywords: List[str] = Field(default_factory=list, description="Key terms extracted from the content")
    timestamp: str = Field(..., description="Creation time in format YYYYMMDDHHMM")
    last_accessed: str = Field(..., description="Last access time in format YYYYMMDDHHMM")
    retrieval_count: int = Field(0, description="Number of times this memory has been accessed")
    links: List[str] = Field(default_factory=list, description="References to related memories")

class MemorySearchRequest(BaseModel):
    """Request model for searching memories"""
    query: str = Field(..., description="Search query text")
    k: int = Field(5, description="Maximum number of results to return")

class MemorySearchResult(BaseModel):
    """Model for a single memory search result"""
    id: str = Field(..., description="Memory ID")
    content: str = Field(..., description="Memory content")
    context: str = Field(..., description="Memory context")
    keywords: List[str] = Field(default_factory=list, description="Memory keywords")
    score: float = Field(..., description="Similarity score")

class MemorySearchResponse(BaseModel):
    """Response model for memory search"""
    results: List[MemorySearchResult] = Field(default_factory=list, description="Search results")

class DeleteResponse(BaseModel):
    """Response model for delete operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Additional information about the operation")
