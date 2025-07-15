"""
Memory Router for Ember AI Assistant Framework
Routes memory operations and manages memory contexts for different conversation threads.
"""

from typing import Dict, List, Optional, Any
from memory_store import MemoryStore, MemoryEntry
import time


class MemoryRouter:
    """Routes memory operations and manages memory contexts."""
    
    def __init__(self, base_store: MemoryStore = None):
        self.base_store = base_store or MemoryStore()
        self.context_stores: Dict[str, MemoryStore] = {}
        self.active_context: Optional[str] = None
    
    def create_context(self, context_id: str) -> bool:
        """Create a new memory context."""
        if context_id in self.context_stores:
            return False
        
        context_store = MemoryStore(f"memory_store_{context_id}.json")
        self.context_stores[context_id] = context_store
        return True
    
    def set_active_context(self, context_id: str) -> bool:
        """Set the active memory context."""
        if context_id == "base":
            self.active_context = None
            return True
        
        if context_id not in self.context_stores:
            return False
        
        self.active_context = context_id
        return True
    
    def get_active_store(self) -> MemoryStore:
        """Get the currently active memory store."""
        if self.active_context is None:
            return self.base_store
        return self.context_stores[self.active_context]
    
    def save_memory(self, content: str, importance: float = 0.5, tags: List[str] = None, 
                   context_id: str = None) -> str:
        """Save memory to the specified context or active context."""
        if context_id is None:
            store = self.get_active_store()
        elif context_id == "base":
            store = self.base_store
        else:
            if context_id not in self.context_stores:
                raise ValueError(f"Context '{context_id}' does not exist")
            store = self.context_stores[context_id]
        
        return store.save_memory(content, importance, tags or [])
    
    def retrieve_memory(self, memory_id: str, context_id: str = None) -> Optional[MemoryEntry]:
        """Retrieve memory from the specified context or search all contexts."""
        if context_id is None:
            # Search in active context first, then base
            store = self.get_active_store()
            entry = store.retrieve_memory(memory_id)
            if entry is None and self.active_context is not None:
                entry = self.base_store.retrieve_memory(memory_id)
            return entry
        elif context_id == "base":
            return self.base_store.retrieve_memory(memory_id)
        else:
            if context_id not in self.context_stores:
                return None
            return self.context_stores[context_id].retrieve_memory(memory_id)
    
    def search_memories(self, query: str, limit: int = 10, context_id: str = None) -> List[MemoryEntry]:
        """Search memories in the specified context or across all contexts."""
        if context_id is None:
            # Search in active context first, then base
            store = self.get_active_store()
            results = store.search_memories(query, limit)
            
            # If active context is not base, also search base context
            if self.active_context is not None:
                base_results = self.base_store.search_memories(query, limit)
                # Merge and deduplicate results
                all_results = results + base_results
                seen_ids = set()
                unique_results = []
                for entry in all_results:
                    if entry.id not in seen_ids:
                        seen_ids.add(entry.id)
                        unique_results.append(entry)
                results = unique_results[:limit]
            
            return results
        elif context_id == "base":
            return self.base_store.search_memories(query, limit)
        else:
            if context_id not in self.context_stores:
                return []
            return self.context_stores[context_id].search_memories(query, limit)
    
    def delete_memory(self, memory_id: str, context_id: str = None) -> bool:
        """Delete memory from the specified context or active context."""
        if context_id is None:
            store = self.get_active_store()
        elif context_id == "base":
            store = self.base_store
        else:
            if context_id not in self.context_stores:
                return False
            store = self.context_stores[context_id]
        
        return store.delete_memory(memory_id)
    
    def get_context_memories(self, context_id: str = None) -> List[MemoryEntry]:
        """Get all memories from the specified context or active context."""
        if context_id is None:
            store = self.get_active_store()
        elif context_id == "base":
            store = self.base_store
        else:
            if context_id not in self.context_stores:
                return []
            store = self.context_stores[context_id]
        
        return store.get_all_memories()
    
    def clear_context(self, context_id: str = None) -> bool:
        """Clear all memories from the specified context or active context."""
        if context_id is None:
            store = self.get_active_store()
        elif context_id == "base":
            store = self.base_store
        else:
            if context_id not in self.context_stores:
                return False
            store = self.context_stores[context_id]
        
        store.clear_all_memories()
        return True
    
    def list_contexts(self) -> List[str]:
        """List all available contexts."""
        contexts = ["base"]
        contexts.extend(self.context_stores.keys())
        return contexts
    
    def delete_context(self, context_id: str) -> bool:
        """Delete a context and all its memories."""
        if context_id == "base":
            return False  # Cannot delete base context
        
        if context_id not in self.context_stores:
            return False
        
        # Clear the context
        self.context_stores[context_id].clear_all_memories()
        
        # Remove from context stores
        del self.context_stores[context_id]
        
        # If this was the active context, reset to base
        if self.active_context == context_id:
            self.active_context = None
        
        return True