"""
Fallback ChromaDB implementation that doesn't rely on embeddings
This is a simple wrapper around ChromaDB that avoids the embedding issues
"""
import os
import logging
import time
import numpy as np
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Project cache directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(PROJECT_DIR, ".cache")
PERSIST_DIR = os.path.join(CACHE_DIR, "chromadb_data")

class SkipEmbeddingFunction:
    """Embedding function that just returns random vectors without using models"""
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        logger.info(f"Initialized skip embedding function with dimension {dimension}")
        
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Return random vectors for each text"""
        if not input:
            return []
            
        # Return random vectors with a seed based on the text to ensure consistency
        embeddings = []
        for text in input:
            # Use a simple hash of the text as a seed
            seed = sum(ord(c) for c in text)
            np.random.seed(seed)
            
            # Generate a random vector
            embedding = np.random.rand(self.dimension)
            
            # Normalize it
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
                
            embeddings.append(embedding.tolist())
            
        return embeddings

class SimpleChromaRetriever:
    """Simple ChromaDB wrapper that avoids embedding issues"""
    def __init__(self, collection_name: str = "memories"):
        """Initialize the ChromaDB wrapper
        
        Args:
            collection_name: Name of the collection
        """
        self.collection_name = collection_name
        self.in_memory_docs = {}  # Fallback in-memory storage
        
        # Try to initialize ChromaDB with skip embeddings
        try:
            logger.info("Initializing ChromaDB...")
            import chromadb
            
            # Initialize client
            try:
                # Try persistent client first
                self.client = chromadb.PersistentClient(path=PERSIST_DIR)
                logger.info("Using persistent ChromaDB client")
            except Exception as e:
                logger.warning(f"Error initializing persistent client: {e}")
                # Fall back to in-memory client
                self.client = chromadb.Client()
                logger.info("Using in-memory ChromaDB client")
                
            # Create collection with skip embeddings
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=SkipEmbeddingFunction()
            )
            
            # Flag to indicate ChromaDB is working
            self.use_chromadb = True
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            # Flag to indicate we're using in-memory fallback
            self.use_chromadb = False
            self.client = None
            self.collection = None
            logger.info("Using in-memory fallback")
            
    def add_document(self, document: str, metadata: Dict, doc_id: str) -> bool:
        """Add a document
        
        Args:
            document: Text content
            metadata: Document metadata
            doc_id: Document ID
            
        Returns:
            bool: Success status
        """
        if self.use_chromadb and self.collection:
            try:
                # Process metadata for ChromaDB (convert lists to strings)
                processed_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, list):
                        processed_metadata[key] = ", ".join(value)
                    else:
                        processed_metadata[key] = value
                
                # Add to ChromaDB
                self.collection.add(
                    documents=[document],
                    metadatas=[processed_metadata],
                    ids=[doc_id]
                )
                return True
            except Exception as e:
                logger.error(f"Error adding document to ChromaDB: {e}")
                
                # Fall back to in-memory storage
                self.use_chromadb = False
                logger.info("Switching to in-memory fallback")
        
        # In-memory fallback
        self.in_memory_docs[doc_id] = {
            "document": document,
            "metadata": metadata,
            "id": doc_id,
            "embedding": None  # We don't compute real embeddings
        }
        return True
        
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document
        
        Args:
            doc_id: Document ID
            
        Returns:
            bool: Success status
        """
        if self.use_chromadb and self.collection:
            try:
                self.collection.delete(ids=[doc_id])
                return True
            except Exception as e:
                logger.error(f"Error deleting document from ChromaDB: {e}")
                
        # In-memory fallback
        if doc_id in self.in_memory_docs:
            del self.in_memory_docs[doc_id]
            
        return True
        
    def search(self, query: str, k: int = 5):
        """Search for documents
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            Dict with ids, documents, distances, and metadatas
        """
        if self.use_chromadb and self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=k
                )
                
                # Process results (convert string metadata back to lists)
                if 'metadatas' in results and results['metadatas']:
                    for metadata in results['metadatas']:
                        for key in ['keywords', 'tags']:
                            if key in metadata and isinstance(metadata[key], str):
                                metadata[key] = [item.strip() for item in metadata[key].split(',')]
                                
                return results
            except Exception as e:
                logger.error(f"Error searching in ChromaDB: {e}")
                
        # In-memory fallback
        if not self.in_memory_docs:
            return {'ids': [[]], 'distances': [[]], 'metadatas': [[]], 'documents': [[]]}
            
        # Simple text search
        matches = []
        for doc_id, doc_data in self.in_memory_docs.items():
            if query.lower() in doc_data["document"].lower():
                # Calculate a simple similarity score
                score = len(query) / len(doc_data["document"]) 
                matches.append((doc_id, doc_data, score))
                
        # Sort by score
        matches.sort(key=lambda x: x[2], reverse=True)
        
        # Limit to k results
        matches = matches[:k]
        
        # Format results like ChromaDB
        ids = [[match[0] for match in matches]]
        documents = [[match[1]["document"] for match in matches]]
        distances = [[match[2] for match in matches]]
        metadatas = [[match[1]["metadata"] for match in matches]]
        
        return {
            'ids': ids,
            'documents': documents,
            'distances': distances,
            'metadatas': metadatas
        }
