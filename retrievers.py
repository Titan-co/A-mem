from typing import List, Dict, Any, Optional, Union
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import nltk
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
from chromadb.config import Settings
import pickle
from nltk.tokenize import word_tokenize
import os
import logging
import time
import sys

# Import custom embedding function
from custom_embedding import LocalCacheEmbeddingFunction

# Configure logging
logger = logging.getLogger(__name__)

# Create a project-specific cache directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(PROJECT_DIR, ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Set environment variables for various model caches
os.environ["CHROMADB_CACHE_DIR"] = CACHE_DIR
os.environ["SENTENCE_TRANSFORMERS_HOME"] = os.path.join(CACHE_DIR, "sentence_transformers")
os.environ["TRANSFORMERS_CACHE"] = os.path.join(CACHE_DIR, "transformers")
os.environ["HF_HOME"] = os.path.join(CACHE_DIR, "transformers")
os.environ["TMPDIR"] = os.path.join(CACHE_DIR, "tmp")

# Ensure the ONNX models directory exists
ONNX_DIR = os.path.join(CACHE_DIR, "onnx_models")
os.makedirs(ONNX_DIR, exist_ok=True)

def check_directory_writable(directory):
    """Check if a directory is writable by creating a test file"""
    if not os.path.exists(directory):
        return False
        
    try:
        test_file = os.path.join(directory, ".write_test")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except Exception as e:
        logger.warning(f"Directory {directory} is not writable: {e}")
        return False

def simple_tokenize(text):
    """Simple tokenization wrapper using NLTK's word_tokenize"""
    try:
        return word_tokenize(text)
    except LookupError:
        # Download nltk data if needed
        try:
            nltk.download('punkt', quiet=True)
            return word_tokenize(text)
        except Exception as e:
            # Fallback to simple splitting if NLTK fails
            logger.warning(f"NLTK tokenization failed: {e}. Using simple split.")
            return text.split()

class SimpleEmbeddingRetriever:
    """Simple retriever using sentence embeddings"""
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the embedding retriever with the specified model
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        logger.info(f"Initializing SimpleEmbeddingRetriever with model: {model_name}")
        
        # Check if cache directories are writable
        if not check_directory_writable(CACHE_DIR):
            logger.warning(f"Cache directory {CACHE_DIR} is not writable. Model downloads may fail.")
        
        try:
            # Initialize the model
            self.model = SentenceTransformer(model_name)
            self.documents = []
            self.embeddings = None
            self.embedding_to_id_map = {}  # Track document IDs
            logger.info(f"Successfully initialized sentence transformer model: {model_name}")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            # Instead of crashing, create a fallback embedding function
            logger.warning("Using fallback embedding approach")
            self.model = None
            self.documents = []
            self.embeddings = None
            self.embedding_to_id_map = {}
        
    def _fallback_encode(self, texts: List[str]) -> np.ndarray:
        """Simple fallback encoding when model fails to load
        
        This creates simple bag-of-words vectors as a fallback
        """
        # Simple word frequency vectors as fallback
        vectors = []
        for text in texts:
            # Create a simple word frequency vector
            words = simple_tokenize(text.lower())
            unique_words = set(words)
            # Very simple vector: just a count for each unique word
            vector = np.zeros(len(unique_words) or 1)
            for i, word in enumerate(unique_words):
                vector[i] = words.count(word)
            # Normalize
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            vectors.append(vector)
        
        # Ensure consistent dimensions by padding
        max_len = max(v.shape[0] for v in vectors)
        padded_vectors = []
        for v in vectors:
            padded = np.zeros(max_len)
            padded[:v.shape[0]] = v
            padded_vectors.append(padded)
            
        return np.array(padded_vectors)
        
    def add_document(self, document: str, doc_id: str = None):
        """Add a document to the retriever.
        
        Args:
            document: Text content to add
            doc_id: Optional document ID to track
        """
        doc_index = len(self.documents)
        self.documents.append(document)
        
        if doc_id:
            self.embedding_to_id_map[doc_index] = doc_id
            
        # Update embeddings
        try:
            if self.model:
                if len(self.documents) == 1:
                    self.embeddings = self.model.encode([document])
                else:
                    new_embedding = self.model.encode([document])
                    self.embeddings = np.vstack([self.embeddings, new_embedding])
            else:
                # Use fallback encoding
                if len(self.documents) == 1:
                    self.embeddings = self._fallback_encode([document])
                else:
                    # We need to recalculate all embeddings because dimensions might change
                    self.embeddings = self._fallback_encode(self.documents)
        except Exception as e:
            logger.error(f"Error encoding document: {e}")
            # If encoding fails, ensure dimensions match existing embeddings
            if self.embeddings is not None:
                embedding_dim = self.embeddings.shape[1]
                # Add a zero vector of the same dimension
                new_embedding = np.zeros((1, embedding_dim))
                self.embeddings = np.vstack([self.embeddings, new_embedding])
            else:
                # First document, create a simple one-dimensional embedding
                self.embeddings = np.array([[0.0]])
            
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of dictionaries containing document content and similarity score
        """
        if not self.documents:
            return []
            
        try:
            # Get query embedding
            if self.model:
                query_embedding = self.model.encode([query])
            else:
                query_embedding = self._fallback_encode([query])
            
            # Calculate cosine similarities
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get top k results
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                result = {
                    'content': self.documents[idx],
                    'score': float(similarities[idx])
                }
                
                # Add document ID if available
                if idx in self.embedding_to_id_map:
                    result['id'] = self.embedding_to_id_map[idx]
                    
                results.append(result)
                
            return results
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []

class ChromaRetriever:
    """Vector database retrieval using ChromaDB"""
    def __init__(self, collection_name: str = "memories", max_retries: int = 3):
        """Initialize ChromaDB retriever.
        
        Args:
            collection_name: Name of the ChromaDB collection
            max_retries: Maximum number of retries for initialization
        """
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        # Ensure persistence directory exists with proper permissions
        persist_dir = os.path.join(CACHE_DIR, "chromadb_data")
        os.makedirs(persist_dir, exist_ok=True)
        
        # Check if the directory is writable
        if not check_directory_writable(persist_dir):
            logger.warning(f"ChromaDB persistence directory {persist_dir} is not writable")
            logger.warning("Will use in-memory ChromaDB instead")
            
        # Try to initialize with retries
        for attempt in range(max_retries):
            try:
                logger.info(f"Initializing ChromaDB (attempt {attempt+1}/{max_retries})")
                
                # Create custom embedding function that uses local cache
                embedding_function = LocalCacheEmbeddingFunction()
                
                # First try using the new PersistentClient method
                try:
                    self.client = chromadb.PersistentClient(path=persist_dir)
                    logger.info(f"Successfully initialized ChromaDB PersistentClient")
                except Exception as e:
                    logger.warning(f"Error using new ChromaDB PersistentClient: {e}")
                    logger.info("Trying fallback ChromaDB client...")
                    
                    # Fall back to older API if needed
                    try:
                        self.client = chromadb.Client(Settings(
                            allow_reset=True,
                            persist_directory=persist_dir
                        ))
                        logger.info(f"Successfully initialized ChromaDB Client with persistence")
                    except Exception as inner_e:
                        logger.warning(f"Error initializing ChromaDB with persistence: {inner_e}")
                        logger.info("Using in-memory ChromaDB as last resort")
                        
                        # Use in-memory client as last resort
                        self.client = chromadb.Client()
                        logger.info(f"Successfully initialized in-memory ChromaDB Client")
                
                # Create or get collection with our custom embedding function
                self.collection = self.client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=embedding_function
                )
                logger.info(f"Successfully initialized ChromaDB collection: {collection_name}")
                
                # If we got here, initialization succeeded
                break
                
            except Exception as e:
                logger.error(f"ChromaDB initialization attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    # Wait before retrying with exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts to initialize ChromaDB failed")
                    # Create an in-memory fallback collection
                    try:
                        self.client = chromadb.Client()
                        embedding_function = LocalCacheEmbeddingFunction()
                        self.collection = self.client.get_or_create_collection(
                            name=collection_name,
                            embedding_function=embedding_function
                        )
                        logger.warning("Created in-memory fallback collection (changes will not persist)")
                    except Exception as fallback_error:
                        logger.error(f"Even fallback collection creation failed: {fallback_error}")
                        logger.error("ChromaRetriever will be non-functional")
        
    def add_document(self, document: str, metadata: Dict, doc_id: str):
        """Add a document to ChromaDB.
        
        Args:
            document: Text content to add
            metadata: Dictionary of metadata
            doc_id: Unique identifier for the document
            
        Returns:
            bool: True if operation succeeded, False otherwise
        """
        if self.collection is None:
            logger.error("Cannot add document: ChromaDB collection not initialized")
            return False
            
        try:
            # Convert lists to strings in metadata to comply with ChromaDB requirements
            processed_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, list):
                    processed_metadata[key] = ", ".join(value)
                else:
                    processed_metadata[key] = value
                    
            self.collection.add(
                documents=[document],
                metadatas=[processed_metadata],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            logger.error(f"Error adding document to ChromaDB: {e}")
            return False
        
    def delete_document(self, doc_id: str):
        """Delete a document from ChromaDB.
        
        Args:
            doc_id: ID of document to delete
            
        Returns:
            bool: True if operation succeeded, False otherwise
        """
        if self.collection is None:
            logger.error("Cannot delete document: ChromaDB collection not initialized")
            return False
            
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            logger.error(f"Error deleting document from ChromaDB: {e}")
            return False
        
    def search(self, query: str, k: int = 5):
        """Search for similar documents.
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            Dict: ChromaDB query results with documents, ids, distances, and metadatas
        """
        if self.collection is None:
            logger.error("Cannot search: ChromaDB collection not initialized")
            return {'ids': [[]], 'distances': [[]], 'metadatas': [[]], 'documents': [[]]}
            
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            # Convert string metadata back to lists where appropriate
            if 'metadatas' in results and results['metadatas']:
                for metadata in results['metadatas']:
                    for key in ['keywords', 'tags']:
                        if key in metadata and isinstance(metadata[key], str):
                            metadata[key] = [item.strip() for item in metadata[key].split(',')]
                            
            return results
        except Exception as e:
            logger.error(f"Error searching in ChromaDB: {e}")
            return {'ids': [[]], 'distances': [[]], 'metadatas': [[]], 'documents': [[]]}
            
    def get_collection_stats(self):
        """Get statistics about the collection.
        
        Returns:
            Dict: Collection statistics (count, etc)
        """
        if self.collection is None:
            return {"error": "ChromaDB collection not initialized", "count": 0}
            
        try:
            # Get count of documents
            count = len(self.collection.get()['ids'])
            return {"count": count, "name": self.collection_name}
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e), "count": 0}
