"""
Memory Store for Ember AI Assistant Framework
Handles storage and retrieval of memory entries with embedding-based search.
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import numpy as np


@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    content: str
    importance: float
    tags: List[str]
    timestamp: float
    id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary."""
        return cls(**data)


class MemoryStore:
    """Handles storage and retrieval of memory entries."""
    
    def __init__(self, storage_path: str = "memory_store.json"):
        self.storage_path = storage_path
        self.memories: Dict[str, MemoryEntry] = {}
        self.load_memories()
    
    def save_memory(self, content: str, importance: float = 0.5, tags: List[str] = None) -> str:
        """Save a new memory entry."""
        if tags is None:
            tags = []
        
        # Validate content
        if not content or len(content.strip()) < 8:
            raise ValueError("Content must be at least 8 characters long")
        
        if not any(c.isalpha() for c in content):
            raise ValueError("Content must contain at least one letter")
        
        memory_id = f"mem_{int(time.time() * 1000)}"
        entry = MemoryEntry(
            content=content.strip(),
            importance=min(max(importance, 0.0), 1.0),  # Clamp to [0, 1]
            tags=tags,
            timestamp=time.time(),
            id=memory_id
        )
        
        self.memories[memory_id] = entry
        self._save_to_disk()
        return memory_id
    
    def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific memory by ID."""
        return self.memories.get(memory_id)
    
    def search_memories(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search memories by content similarity (simple text matching for now)."""
        if not query.strip():
            return []
        
        query_lower = query.lower()
        results = []
        
        for entry in self.memories.values():
            # Simple similarity scoring
            content_lower = entry.content.lower()
            score = 0
            
            # Exact match gets highest score
            if query_lower in content_lower:
                score += 10
            
            # Word overlap
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            overlap = len(query_words & content_words)
            score += overlap * 2
            
            # Tag matching
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 3
            
            if score > 0:
                results.append((score, entry))
        
        # Sort by score (descending) and importance
        results.sort(key=lambda x: (x[0], x[1].importance), reverse=True)
        return [entry for _, entry in results[:limit]]
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        if memory_id in self.memories:
            del self.memories[memory_id]
            self._save_to_disk()
            return True
        return False
    
    def get_all_memories(self) -> List[MemoryEntry]:
        """Get all memories."""
        return list(self.memories.values())
    
    def clear_all_memories(self):
        """Clear all memories."""
        self.memories.clear()
        self._save_to_disk()
    
    def _save_to_disk(self):
        """Save memories to disk."""
        try:
            data = {
                memory_id: entry.to_dict()
                for memory_id, entry in self.memories.items()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save memories to disk: {e}")
    
    def load_memories(self):
        """Load memories from disk."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.memories = {
                    memory_id: MemoryEntry.from_dict(entry_data)
                    for memory_id, entry_data in data.items()
                }
        except FileNotFoundError:
            # File doesn't exist yet, start with empty store
            self.memories = {}
        except Exception as e:
            print(f"Warning: Failed to load memories from disk: {e}")
            self.memories = {}