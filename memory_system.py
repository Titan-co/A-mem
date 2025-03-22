def strip_markdown_code_fences(text):
    """Strip Markdown code fences from text to extract raw JSON.
    
    Some API providers (like OpenRouter) wrap JSON in ```json ... ``` blocks
    or with backticks like `json { ... }`. This function extracts the JSON content.
    
    Args:
        text (str): Text that might contain Markdown-wrapped JSON
        
    Returns:
        str: Cleaned text with code fences removed
    """
    if not text:
        return text
    
    # Make a copy of the original text for later fallback if needed
    original_text = text
    text = text.strip()
    
    # Case 1: JSON wrapped in triple backticks (```json ... ```)
    if text.startswith('```'):
        # Find the end of the opening fence line
        first_newline = text.find('\n')
        if first_newline == -1:
            # Special case: single line with triple backticks
            # Like: ```json {...}```
            # Extract content by removing the opening and closing fences
            opening_marker = '```json'
            # Check if it has `json` or just ```
            if text.startswith(opening_marker):
                text = text[len(opening_marker):]
            else:  
                # Just starts with ```
                text = text[3:]
            
            # Remove closing backticks
            if text.endswith('```'):
                text = text[:-3]
                
            return text.strip()
        
        # Handle normal multiline case
        # Find the closing fence
        closing_fence = text.rfind('```')
        if closing_fence <= first_newline:
            return text  # No closing fence or it's before the first newline
            
        # Extract the content between the fences
        content = text[first_newline + 1:closing_fence].strip()
        return content
    
    # Case 2: JSON wrapped in single backticks (`json {...}`) or double backticks
    for prefix in ['`json', '``json', '`', '``']:
        if text.startswith(prefix):
            # Remove the opening marker
            text = text[len(prefix):]
            
            # Remove closing backticks
            for suffix in ['`', '``']:
                if text.endswith(suffix):
                    text = text[:-len(suffix)]
                    break
            
            return text.strip()
    
    # Case 3: Try to find JSON-like structure in the text
    # If we got here, return the original text as a last resort
    return text

import keyword
from typing import List, Dict, Optional, Any
import uuid
from datetime import datetime
from llm_controller import LLMController
from retrievers import SimpleEmbeddingRetriever, ChromaRetriever
import json
import logging

logger = logging.getLogger(__name__)

class MemoryNote:
    """A memory note that represents a single unit of information in the memory system.
    
    This class encapsulates all metadata associated with a memory, including:
    - Core content and identifiers
    - Temporal information (creation and access times)
    - Semantic metadata (keywords, context, tags)
    - Relationship data (links to other memories)
    - Usage statistics (retrieval count)
    - Evolution tracking (history of changes)
    """
    
    def __init__(self, 
                 content: str,
                 id: Optional[str] = None,
                 keywords: Optional[List[str]] = None,
                 links: Optional[Dict] = None,
                 retrieval_count: Optional[int] = None,
                 timestamp: Optional[str] = None,
                 last_accessed: Optional[str] = None,
                 context: Optional[str] = None,
                 evolution_history: Optional[List] = None,
                 category: Optional[str] = None,
                 tags: Optional[List[str]] = None):
        """Initialize a new memory note with its associated metadata.
        
        Args:
            content (str): The main text content of the memory
            id (Optional[str]): Unique identifier for the memory. If None, a UUID will be generated
            keywords (Optional[List[str]]): Key terms extracted from the content
            links (Optional[Dict]): References to related memories
            retrieval_count (Optional[int]): Number of times this memory has been accessed
            timestamp (Optional[str]): Creation time in format YYYYMMDDHHMM
            last_accessed (Optional[str]): Last access time in format YYYYMMDDHHMM
            context (Optional[str]): The broader context or domain of the memory
            evolution_history (Optional[List]): Record of how the memory has evolved
            category (Optional[str]): Classification category
            tags (Optional[List[str]]): Additional classification tags
        """
        # Core content and ID
        self.content = content
        self.id = id or str(uuid.uuid4())
        
        # Semantic metadata
        self.keywords = keywords or []
        self.links = links or []
        self.context = context or "General"
        self.category = category or "Uncategorized"
        self.tags = tags or []
        
        # Temporal information
        current_time = datetime.now().strftime("%Y%m%d%H%M")
        self.timestamp = timestamp or current_time
        self.last_accessed = last_accessed or current_time
        
        # Usage and evolution data
        self.retrieval_count = retrieval_count or 0
        self.evolution_history = evolution_history or []

class AgenticMemorySystem:
    """Core memory system that manages memory notes and their evolution.
    
    This system provides:
    - Memory creation, retrieval, update, and deletion
    - Content analysis and metadata extraction
    - Memory evolution and relationship management
    - Hybrid search capabilities
    """
    
    def __init__(self, 
                 model_name: str = 'all-MiniLM-L6-v2',
                 llm_backend: str = "openai",
                 llm_model: str = "gpt-4",
                 evo_threshold: int = 3,
                 api_key: Optional[str] = None,
                 api_base: Optional[str] = None,
                 llm_controller = None):  
        """Initialize the memory system.
        
        Args:
            model_name: Name of the sentence transformer model
            llm_backend: LLM backend to use (openai/ollama)
            llm_model: Name of the LLM model
            evo_threshold: Number of memories before triggering evolution
            api_key: API key for the LLM service
            llm_controller: Optional custom LLM controller for testing
        """
        self.memories = {}
        self.model_name = model_name  # Store the model name for later use
        self.retriever = SimpleEmbeddingRetriever(model_name)
        self.chroma_retriever = ChromaRetriever()
        self.llm_controller = llm_controller or LLMController(llm_backend, llm_model, api_key, api_base)
        self.evo_cnt = 0
        self.evo_threshold = evo_threshold

        # Evolution system prompt
        self._evolution_system_prompt = '''
                                You are an AI memory evolution agent responsible for managing and evolving a knowledge base.
                                Analyze the the new memory note according to keywords and context, also with their several nearest neighbors memory.
                                Make decisions about its evolution.  

                                The new memory context:
                                {context}
                                content: {content}
                                keywords: {keywords}

                                The nearest neighbors memories:
                                {nearest_neighbors_memories}

                                Based on this information, determine:
                                1. Should this memory be evolved? Consider its relationships with other memories.
                                2. What specific actions should be taken (strengthen, update_neighbor)?
                                   2.1 If choose to strengthen the connection, which memory should it be connected to? Can you give the updated tags of this memory?
                                   2.2 If choose to update_neighbor, you can update the context and tags of these memories based on the understanding of these memories.
                                Tags should be determined by the content of these characteristic of these memories, which can be used to retrieve them later and categorize them.
                                All the above information should be returned in a list format according to the sequence: [[new_memory],[neighbor_memory_1],...[neighbor_memory_n]]
                                These actions can be combined.
                                Return your decision in JSON format with the following structure:
                                {{
                                    "should_evolve": True or False,
                                    "actions": ["strengthen", "update_neighbor"],
                                    "suggested_connections": ["neighbor_memory_ids"],
                                    "tags_to_update": ["tag_1",..."tag_n"], 
                                    "new_context_neighborhood": ["new context",...,"new context"],
                                    "new_tags_neighborhood": [["tag_1",...,"tag_n"],...["tag_1",...,"tag_n"]],
                                }}
                                '''
        
    def _extract_best_json(self, text: str) -> Dict:
        """Extract the best JSON object from text, trying multiple approaches.
        
        Args:
            text: Text potentially containing JSON
            
        Returns:
            Dict: Extracted JSON object or default empty values
        """
        # Default response if all approaches fail
        default_response = {
            "keywords": ["auto-generated"],
            "context": "General",
            "tags": ["auto-tagged"]
        }
        
        # Try direct parsing first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
            
        # Try regex approaches - from most to least specific
        import re
        # Pattern for complete JSON object with attributes
        patterns = [
            r'\{\s*"keywords"\s*:\s*\[[^\]]*\]\s*,\s*"context"\s*:\s*"[^"]*"\s*,\s*"tags"\s*:\s*\[[^\]]*\]\s*\}',
            r'\{\s*"[^"]*"\s*:\s*(?:\[[^\]]*\]|"[^"]*")(?:\s*,\s*"[^"]*"\s*:\s*(?:\[[^\]]*\]|"[^"]*"))*\s*\}',
            r'\{[^\{\}]*\}',  # Simple JSON object without nested objects
            r'\{[\s\S]*?\}'   # Any JSON-like structure (most permissive)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Last resort: Try to extract arrays for keywords and tags
        keywords = re.findall(r'\[\s*(?:"[^"]*"\s*(?:,\s*"[^"]*"\s*)*)\]', text)
        if keywords:
            try:
                keyword_list = json.loads(keywords[0])
                default_response["keywords"] = keyword_list
            except:
                pass
                
        # If we got here, extraction failed - use the default
        return default_response

    def analyze_content(self, content: str) -> Dict:            
        """Analyze content using LLM to extract semantic metadata.
        
        Uses a language model to understand the content and extract:
        - Keywords: Important terms and concepts
        - Context: Overall domain or theme
        - Tags: Classification categories
        
        Args:
            content (str): The text content to analyze
            
        Returns:
            Dict: Contains extracted metadata with keys:
                - keywords: List[str]
                - context: str
                - tags: List[str]
        """
        prompt = """Generate a structured analysis of the following content by:
            1. Identifying the most salient keywords (focus on nouns, verbs, and key concepts)
            2. Extracting core themes and contextual elements
            3. Creating relevant categorical tags

            Format the response as a JSON object:
            {
                "keywords": [
                    // several specific, distinct keywords that capture key concepts and terminology
                    // Order from most to least important
                    // Don't include keywords that are the name of the speaker or time
                    // At least three keywords, but don't be too redundant.
                ],
                "context": 
                    // one sentence summarizing:
                    // - Main topic/domain
                    // - Key arguments/points
                    // - Intended audience/purpose
                ,
                "tags": [
                    // several broad categories/themes for classification
                    // Include domain, format, and type tags
                    // At least three tags, but don't be too redundant.
                ]
            }

            IMPORTANT: Return ONLY the JSON object with no other text or formatting.

            Content for analysis:
            """ + content
        try:
            response = self.llm_controller.llm.get_completion(prompt, response_format={"type": "json_object"}, temperature=0.7)
            
            # Strip any Markdown code fences from the response
            cleaned_response = strip_markdown_code_fences(response)
            
            # Try to extract valid JSON using multiple approaches
            return self._extract_best_json(cleaned_response)
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            # Return basic valid values when all else fails
            simple_words = content.split()[:10]  # Use first 10 words as basic keywords
            keywords = [w for w in simple_words if len(w) > 3][:5]  # Filter to longer words
            return {
                "keywords": keywords if keywords else ["auto-generated"],
                "context": "General content analysis",
                "tags": ["auto-tagged", "text-content"]
            }

    def create(self, content: str, **kwargs) -> str:
        """Create a new memory note.
        
        Args:
            content: The content of the memory
            **kwargs: Additional metadata (tags, category, etc.)
            
        Returns:
            str: ID of the created memory
        """
        # Create memory note
        analysis = self.analyze_content(content)
        keyword, context, tags_from_analysis = analysis["keywords"], analysis["context"], analysis["tags"]
        
        # Use provided tags if available, otherwise use tags from analysis
        if 'tags' not in kwargs:
            kwargs['tags'] = tags_from_analysis
            
        note = MemoryNote(content=content, keywords=keyword, context=context, **kwargs)
        self.memories[note.id] = note
        
        # Add to retrievers
        metadata = {
            "context": note.context,
            "keywords": note.keywords,
            "tags": note.tags,
            "category": note.category,
            "timestamp": note.timestamp
        }
        self.chroma_retriever.add_document(document=content, metadata=metadata, doc_id=note.id)
        self.retriever.add_document(content)
        
        # First increment the counter
        self.evo_cnt += 1
        
        evolved = self._process_memory_evolution(note)
        
        if evolved == True:
            self.evo_cnt += 1
            if self.evo_cnt % self.evo_threshold == 0:
                self.consolidate_memories()
        
        return note.id
    
    def consolidate_memories(self):
        """Consolidate memories: update retriever with new documents
        
        This function re-initializes both retrievers (SimpleEmbeddingRetriever and ChromaRetriever)
        and updates them with all memory documents, including their metadata (context, keywords, tags).
        This ensures the retrieval systems have the latest state of all memories for accurate search results.
        
        The consolidation process:
        1. Reinitializes both retrievers with their original configurations (which clears existing data)
        2. Adds all memory documents back to both retrievers with their current metadata
        3. Ensures consistent document representation across both retrieval systems
        """
        # 1. Save original configuration
        model_name = self.model_name  # Use the stored model name instead of trying to extract it
        collection_name = self.chroma_retriever.collection.name
        
        # 2. Clear and reinitialize retrievers
        # For SimpleEmbeddingRetriever, creating a new instance clears all documents
        self.retriever = SimpleEmbeddingRetriever(model_name)
        
        # For ChromaRetriever, we need to delete the collection and recreate it
        try:
            self.chroma_retriever.client.delete_collection(collection_name)
        except Exception as e:
            logger.warning(f"Failed to delete collection {collection_name}: {e}")
        self.chroma_retriever = ChromaRetriever(collection_name)
        
        # 3. Re-add all memory documents with their metadata to both retrievers
        for memory_id, memory in self.memories.items():
            # Prepare metadata for ChromaDB
            metadata = {
                "context": memory.context,
                "keywords": memory.keywords,
                "tags": memory.tags,
                "category": memory.category,
                "timestamp": memory.timestamp
            }
            
            # Add to ChromaRetriever
            self.chroma_retriever.add_document(
                document=memory.content,
                metadata=metadata,
                doc_id=memory_id
            )
            
            # Create enhanced document for SimpleEmbeddingRetriever by combining content with metadata
            metadata_text = f"{memory.context} {' '.join(memory.keywords)} {' '.join(memory.tags)}"
            enhanced_document = f"{memory.content} , {metadata_text}"
            
            # Add to SimpleEmbeddingRetriever
            self.retriever.add_document(enhanced_document)
            
        logger.info(f"Memory consolidation complete. Updated {len(self.memories)} memories in both retrievers.")
    
    def read(self, memory_id: str) -> Optional[MemoryNote]:
        """Retrieve a memory note by its ID.
        
        Args:
            memory_id (str): ID of the memory to retrieve
            
        Returns:
            MemoryNote if found, None otherwise
        """
        return self.memories.get(memory_id)
    
    def update(self, memory_id: str, **kwargs) -> bool:
        """Update a memory note.
        
        Args:
            memory_id: ID of memory to update
            **kwargs: Fields to update
            
        Returns:
            bool: True if update successful
        """
        if memory_id not in self.memories:
            return False
            
        note = self.memories[memory_id]
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(note, key):
                setattr(note, key, value)
                
        # Update in ChromaDB
        metadata = {
            "context": note.context,
            "keywords": note.keywords,
            "tags": note.tags,
            "category": note.category,
            "timestamp": note.timestamp
        }
        self.chroma_retriever.delete_document(memory_id)
        self.chroma_retriever.add_document(document=note.content, metadata=metadata, doc_id=memory_id)
        
        return True
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory note by its ID.
        
        Args:
            memory_id (str): ID of the memory to delete
            
        Returns:
            bool: True if memory was deleted, False if not found
        """
        if memory_id in self.memories:
            # Delete from ChromaDB
            self.chroma_retriever.delete_document(memory_id)
            # Delete from local storage
            del self.memories[memory_id]
            return True
        return False
    
    def _search_raw(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Internal search method that returns raw results from ChromaDB.
        
        This is used internally by the memory evolution system to find
        related memories for potential evolution.
        
        Args:
            query (str): The search query text
            k (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: Raw search results from ChromaDB
        """
        results = self.chroma_retriever.search(query, k)
        return [{'id': doc_id, 'score': score} 
                for doc_id, score in zip(results['ids'][0], results['distances'][0])]
                
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for memories using a hybrid retrieval approach.
        
        This method combines results from both:
        1. ChromaDB vector store (semantic similarity)
        2. Embedding-based retrieval (dense vectors)
        
        The results are deduplicated and ranked by relevance.
        
        Args:
            query (str): The search query text
            k (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of search results, each containing:
                - id: Memory ID
                - content: Memory content
                - score: Similarity score
                - metadata: Additional memory metadata
        """
        # Get results from ChromaDB
        chroma_results = self.chroma_retriever.search(query, k)
        memories = []
        
        # Process ChromaDB results
        for i, doc_id in enumerate(chroma_results['ids'][0]):
            memory = self.memories.get(doc_id)
            if memory:
                memories.append({
                    'id': doc_id,
                    'content': memory.content,
                    'context': memory.context,
                    'keywords': memory.keywords,
                    'score': chroma_results['distances'][0][i]
                })
                
        # Get results from embedding retriever
        embedding_results = self.retriever.search(query, k)
        
        # Combine results with deduplication
        seen_ids = set(m['id'] for m in memories)
        for result in embedding_results:
            memory_id = result.get('id')
            if memory_id and memory_id not in seen_ids:
                memory = self.memories.get(memory_id)
                if memory:
                    memories.append({
                        'id': memory_id,
                        'content': memory.content,
                        'context': memory.context,
                        'keywords': memory.keywords,
                        'score': result.get('score', 0.0)
                    })
                    seen_ids.add(memory_id)
                    
        return memories[:k]
        
    def _process_memory_evolution(self, note: MemoryNote) -> bool:
        """Process potential memory evolution for a new note.
        
        Args:
            note: The new memory note to evaluate for evolution
            
        Returns:
            bool: Whether evolution occurred
        """
        # Get nearest neighbors
        neighbors = self.search(note.content, k=5)
        if not neighbors:
            return False
            
        # Store the IDs of neighbors for later use
        neighbor_ids = [mem['id'] for mem in neighbors if 'id' in mem]
            
        # Format neighbors for LLM
        neighbors_text = "\n".join([
            f"Memory {mem['id']}:\n"
            f"Content: {mem['content']}\n"
            f"Context: {mem['context']}\n"
            f"Keywords: {mem['keywords']}\n"
            for mem in neighbors
        ])
        
        # Query LLM for evolution decision
        prompt = self._evolution_system_prompt.format(
            content=note.content,
            context=note.context,
            keywords=note.keywords,
            nearest_neighbors_memories=neighbors_text
        )
        
        # Add an explicit instruction to avoid Markdown formatting
        prompt += "\n\nIMPORTANT: Return ONLY the JSON object with no Markdown formatting, code blocks, or backticks."
        
        response = self.llm_controller.llm.get_completion(
            prompt,response_format={"type": "json_object"}
        )
        try:
            # Strip any Markdown code fences from the response
            cleaned_response = strip_markdown_code_fences(response)
            
            # Try to extract JSON using our enhanced method
            default_evolution = {
                "should_evolve": False,
                "actions": [],
                "suggested_connections": [],
                "tags_to_update": [],
                "new_context_neighborhood": [],
                "new_tags_neighborhood": []
            }
            
            # First try to parse as is
            try:
                response_json = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                logger.warning(f"Initial JSON parse failed in evolution: {e}")
                logger.debug(f"Cleaned response: {cleaned_response}")
                
                # Try more aggressive extraction with regex
                import re
                # Look for the entire evolution JSON structure
                patterns = [
                    r'\{\s*"should_evolve"\s*:.*?\}',  # Find the entire evolution JSON
                    r'\{[\s\S]*?"should_evolve"[\s\S]*?\}',  # More permissive pattern
                    r'\{[\s\S]*?\}'  # Most permissive - any JSON-like structure
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, cleaned_response)
                    if match:
                        try:
                            response_json = json.loads(match.group(0))
                            # Check if it has the required fields
                            if "should_evolve" in response_json:
                                break
                        except json.JSONDecodeError:
                            continue
                else:  # No break occurred in the for loop
                    logger.error("Could not extract valid JSON from LLM response")
                    # Use default response that doesn't trigger evolution
                    response_json = default_evolution
            # Get the evolution decision, with safe fallback
            should_evolve = response_json.get("should_evolve", False)
            # Convert string "True"/"False" to boolean if needed
            if isinstance(should_evolve, str):
                should_evolve = should_evolve.lower() == "true"
                
            if should_evolve:
                # Get actions with safe fallback
                actions = response_json.get("actions", [])
                if not isinstance(actions, list):
                    actions = [actions] if actions else []
                    
                for action in actions:
                    if action == "strengthen":
                        # Get values with safe fallbacks
                        suggest_connections = response_json.get("suggested_connections", [])
                        new_tags = response_json.get("tags_to_update", [])
                        
                        # Ensure they're lists
                        if not isinstance(suggest_connections, list):
                            suggest_connections = [suggest_connections] if suggest_connections else []
                        if not isinstance(new_tags, list):
                            new_tags = [new_tags] if new_tags else []
                            
                        # Update the memory
                        note.links.extend(suggest_connections)
                        note.tags = new_tags
                        
                    elif action == "update_neighbor":
                        # Get values with safe fallbacks
                        new_context_neighborhood = response_json.get("new_context_neighborhood", [])
                        new_tags_neighborhood = response_json.get("new_tags_neighborhood", [])
                        
                        # Ensure they're lists
                        if not isinstance(new_context_neighborhood, list):
                            new_context_neighborhood = [new_context_neighborhood] if new_context_neighborhood else []
                        if not isinstance(new_tags_neighborhood, list):
                            new_tags_neighborhood = [new_tags_neighborhood] if new_tags_neighborhood else []
                        
                        noteslist = list(self.memories.values())
                        notes_id = list(self.memories.keys())
                        
                        # Create a mapping from neighbor ID to its index in the memory list
                        indices = []
                        for neighbor_id in neighbor_ids:
                            if neighbor_id in notes_id:
                                indices.append(notes_id.index(neighbor_id))
                            else:
                                indices.append(-1)  # Invalid index as a fallback
                        
                        # Make sure we have valid indices to work with
                        if not indices:
                            logger.warning("No valid memory indices found for evolution")
                            continue
                        
                        # Make sure we don't go out of bounds
                        max_updates = min(len(indices), len(new_tags_neighborhood), len(new_context_neighborhood))
                        
                        for i in range(max_updates):
                            # find some memory
                            tags = new_tags_neighborhood[i]
                            context = new_context_neighborhood[i]
                            memorytmp_idx = indices[i]
                            
                            # Check if index is valid
                            if memorytmp_idx >= 0 and memorytmp_idx < len(noteslist):
                                notetmp = noteslist[memorytmp_idx]
                                # add tag to memory - ensure tags is a list
                                if not isinstance(tags, list):
                                    tags = [tags] if tags else []
                                notetmp.tags = tags
                                notetmp.context = context
                                self.memories[notes_id[memorytmp_idx]] = notetmp
                            else:
                                logger.warning(f"Invalid memory index {memorytmp_idx}")
            return should_evolve
            
        except (json.JSONDecodeError, KeyError, Exception) as e:
            logger.error(f"Error in memory evolution: {str(e)}")
            return False
