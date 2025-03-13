from typing import Dict, List, Optional, Union, Any
from chromadb.config import Settings
import chromadb
import logging
from dataclasses import dataclass
import json
from datetime import datetime
import os
import sys
import uuid

# Add path to chromadb
os.environ["PATH"] = f"{os.environ.get('PATH', '')}:/usr/local/lib/python3.10/site-packages/chromadb"

@dataclass
class KnowledgeEntry:
    """Represents a piece of knowledge in semantic memory"""
    content: str
    metadata: Dict[str, Any]
    embedding_model: str = "all-MiniLM-L6-v2"  # Default embedding model

class SemanticMemory:
    """ChromaDB-based semantic memory implementation for storing and retrieving knowledge"""
    
    def __init__(self, persist_directory: str = "./semantic_memory_data",
                 collection_name: str = "knowledge_base"):
        """Initialize ChromaDB client and collection"""
        try:
            # Initialize ChromaDB with persistence using the new API
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Main knowledge base for semantic memory"}
            )
            
            logging.info(f"Successfully initialized semantic memory with collection: {collection_name}")
            
        except Exception as e:
            logging.error(f"Failed to initialize semantic memory: {e}")
            raise

    def store_knowledge(self, entry: KnowledgeEntry) -> bool:
        """Store a piece of knowledge in the semantic memory"""
        try:
            # Generate unique ID for the knowledge entry
            entry_id = str(uuid.uuid4())
            
            # Add timestamp to metadata
            entry.metadata["timestamp"] = datetime.utcnow().isoformat()
            
            # Add to collection
            self.collection.add(
                documents=[entry.content],
                metadatas=[entry.metadata],
                ids=[entry_id]
            )
            
            logging.info(f"Successfully stored knowledge entry: {entry_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to store knowledge: {e}")
            return False

    def query_knowledge(self, query: str, n_results: int = 5, 
                       metadata_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query the semantic memory for relevant knowledge"""
        try:
            # Construct query parameters
            query_params = {
                "query_texts": [query],
                "n_results": n_results
            }
            
            if metadata_filter:
                query_params["where"] = metadata_filter
            
            # Execute query
            results = self.collection.query(**query_params)
            
            # Format results
            formatted_results = []
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                    "id": results["ids"][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            logging.error(f"Failed to query knowledge: {e}")
            return []

    def batch_store_knowledge(self, entries: List[KnowledgeEntry]) -> bool:
        """Store multiple knowledge entries in batch"""
        try:
            documents = []
            metadatas = []
            ids = []
            
            for entry in entries:
                entry_id = str(uuid.uuid4())
                entry.metadata["timestamp"] = datetime.utcnow().isoformat()
                
                documents.append(entry.content)
                metadatas.append(entry.metadata)
                ids.append(entry_id)
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logging.info(f"Successfully stored {len(entries)} knowledge entries")
            return True
            
        except Exception as e:
            logging.error(f"Failed to batch store knowledge: {e}")
            return False

    def delete_knowledge(self, entry_ids: Union[str, List[str]]) -> bool:
        """Delete knowledge entries by their IDs"""
        try:
            if isinstance(entry_ids, str):
                entry_ids = [entry_ids]
                
            self.collection.delete(ids=entry_ids)
            logging.info(f"Successfully deleted {len(entry_ids)} knowledge entries")
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete knowledge entries: {e}")
            return False

    def update_knowledge(self, entry_id: str, new_entry: KnowledgeEntry) -> bool:
        """Update an existing knowledge entry"""
        try:
            # Update timestamp
            new_entry.metadata["updated_at"] = datetime.utcnow().isoformat()
            
            self.collection.update(
                ids=[entry_id],
                documents=[new_entry.content],
                metadatas=[new_entry.metadata]
            )
            
            logging.info(f"Successfully updated knowledge entry: {entry_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to update knowledge entry: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge collection"""
        try:
            count = self.collection.count()
            return {
                "total_entries": count,
                "collection_name": self.collection.name,
                "metadata": self.collection.metadata
            }
        except Exception as e:
            logging.error(f"Failed to get collection stats: {e}")
            return {}

    def clear_cache(self):
        """Clear the semantic memory cache"""
        try:
            self.collection = self.client.get_collection(self.collection.name)
            logging.info("Successfully cleared semantic memory cache")
        except Exception as e:
            logging.error(f"Failed to clear cache: {e}")

    def clear_all(self) -> bool:
        """Clear all semantic memory data (use with caution)"""
        try:
            self.client.delete_collection(self.collection.name)
            # Recreate empty collection
            self.collection = self.client.create_collection(
                name=self.collection.name,
                metadata={"description": "Main knowledge base for semantic memory"}
            )
            logging.info("Successfully cleared all semantic memory data")
            return True
        except Exception as e:
            logging.error(f"Failed to clear semantic memory: {e}")
            return False
