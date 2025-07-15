"""
Hypothesis property tests for memory system components.
Tests MemoryStore and MemoryRouter with robust content guards.
"""

import pytest
from hypothesis import given, settings, strategies as st
from hypothesis.strategies import text, floats, lists
import tempfile
import os

from memory_store import MemoryStore, MemoryEntry
from memory_router import MemoryRouter
from tests.hypothesis._helpers import robust_content_guard


class TestMemoryStoreProperties:
    """Property tests for MemoryStore."""
    
    def setup_method(self):
        """Set up a temporary storage file for each test."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.store = MemoryStore(self.temp_file.name)
    
    def teardown_method(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    @given(
        content=text(min_size=1, max_size=100),
        importance=floats(min_value=0.0, max_value=1.0),
        tags=lists(text(min_size=1, max_size=10), max_size=5),
    )
    @settings(deadline=None)
    def test_memory_save_and_retrieve(self, content, importance, tags):
        """Test that saved memories can be retrieved correctly."""
        robust_content_guard(content)
        
        # Save memory
        memory_id = self.store.save_memory(content, importance, tags)
        
        # Retrieve memory
        retrieved = self.store.retrieve_memory(memory_id)
        
        # Verify retrieval
        assert retrieved is not None
        assert retrieved.content == content.strip()
        assert retrieved.importance == min(max(importance, 0.0), 1.0)
        assert retrieved.tags == tags
        assert retrieved.id == memory_id
    
    @given(
        content=text(min_size=1, max_size=100),
        importance=floats(min_value=0.0, max_value=1.0),
        tags=lists(text(min_size=1, max_size=10), max_size=5),
    )
    @settings(deadline=None)
    def test_memory_persistence(self, content, importance, tags):
        """Test that memories persist across store reloads."""
        robust_content_guard(content)
        
        # Save memory
        memory_id = self.store.save_memory(content, importance, tags)
        
        # Create new store instance (simulates reload)
        new_store = MemoryStore(self.temp_file.name)
        
        # Retrieve from new store
        retrieved = new_store.retrieve_memory(memory_id)
        
        # Verify persistence
        assert retrieved is not None
        assert retrieved.content == content.strip()
        assert retrieved.importance == min(max(importance, 0.0), 1.0)
        assert retrieved.tags == tags
    
    @given(
        content=text(min_size=1, max_size=100),
        importance=floats(min_value=0.0, max_value=1.0),
        tags=lists(text(min_size=1, max_size=10), max_size=5),
    )
    @settings(deadline=None)
    def test_memory_deletion(self, content, importance, tags):
        """Test that memories can be deleted."""
        robust_content_guard(content)
        
        # Save memory
        memory_id = self.store.save_memory(content, importance, tags)
        
        # Verify it exists
        assert self.store.retrieve_memory(memory_id) is not None
        
        # Delete memory
        success = self.store.delete_memory(memory_id)
        assert success is True
        
        # Verify it's gone
        assert self.store.retrieve_memory(memory_id) is None
    
    @given(
        contents=lists(text(min_size=1, max_size=50), min_size=1, max_size=5),
        importance=floats(min_value=0.0, max_value=1.0),
        tags=lists(text(min_size=1, max_size=10), max_size=3),
    )
    @settings(deadline=None)
    def test_memory_search(self, contents, importance, tags):
        """Test memory search functionality."""
        # Filter out pathological content
        valid_contents = []
        for content in contents:
            try:
                robust_content_guard(content)
                valid_contents.append(content)
            except:
                continue
        
        if not valid_contents:
            return  # Skip if no valid content
        
        # Save memories
        memory_ids = []
        for content in valid_contents:
            memory_id = self.store.save_memory(content, importance, tags)
            memory_ids.append(memory_id)
        
        # Search for each content
        for content in valid_contents:
            results = self.store.search_memories(content, limit=10)
            assert len(results) > 0
            
            # At least one result should contain the search term
            found = False
            for result in results:
                if content.lower() in result.content.lower():
                    found = True
                    break
            assert found
    
    @given(
        content=text(min_size=1, max_size=100),
        importance=floats(min_value=0.0, max_value=1.0),
        tags=lists(text(min_size=1, max_size=10), max_size=5),
    )
    @settings(deadline=None)
    def test_memory_importance_clamping(self, content, importance, tags):
        """Test that importance values are properly clamped."""
        robust_content_guard(content)
        
        # Save memory
        memory_id = self.store.save_memory(content, importance, tags)
        
        # Retrieve and verify clamping
        retrieved = self.store.retrieve_memory(memory_id)
        expected_importance = min(max(importance, 0.0), 1.0)
        assert retrieved.importance == expected_importance


class TestMemoryRouterProperties:
    """Property tests for MemoryRouter."""
    
    def setup_method(self):
        """Set up temporary storage files for each test."""
        self.temp_base = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_base.close()
        self.base_store = MemoryStore(self.temp_base.name)
        self.router = MemoryRouter(self.base_store)
    
    def teardown_method(self):
        """Clean up temporary files."""
        for temp_file in [self.temp_base.name]:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        # Clean up context files
        for context_id in self.router.list_contexts():
            if context_id != "base":
                context_file = f"memory_store_{context_id}.json"
                if os.path.exists(context_file):
                    os.unlink(context_file)
    
    @given(
        content=text(min_size=1, max_size=100),
        importance=floats(min_value=0.0, max_value=1.0),
        tags=lists(text(min_size=1, max_size=10), max_size=5),
        context_id=st.sampled_from(["base", "test_context"]),
    )
    @settings(deadline=None)
    def test_router_save_and_retrieve(self, content, importance, tags, context_id):
        """Test that router can save and retrieve memories in different contexts."""
        robust_content_guard(content)
        
        # Create context if needed
        if context_id != "base":
            self.router.create_context(context_id)
        
        # Save memory
        memory_id = self.router.save_memory(content, importance, tags, context_id)
        
        # Retrieve memory
        retrieved = self.router.retrieve_memory(memory_id, context_id)
        
        # Verify retrieval
        assert retrieved is not None
        assert retrieved.content == content.strip()
        assert retrieved.importance == min(max(importance, 0.0), 1.0)
        assert retrieved.tags == tags
        assert retrieved.id == memory_id
    
    @given(
        content=text(min_size=1, max_size=100),
        importance=floats(min_value=0.0, max_value=1.0),
        tags=lists(text(min_size=1, max_size=10), max_size=5),
    )
    @settings(deadline=None)
    def test_router_context_switching(self, content, importance, tags):
        """Test that router properly handles context switching."""
        robust_content_guard(content)
        
        # Create a test context
        context_id = "test_context"
        self.router.create_context(context_id)
        
        # Save memory in base context
        base_memory_id = self.router.save_memory(content, importance, tags, "base")
        
        # Save memory in test context
        test_memory_id = self.router.save_memory(content + "_test", importance, tags, context_id)
        
        # Switch to test context
        self.router.set_active_context(context_id)
        
        # Verify we can retrieve from active context
        retrieved = self.router.retrieve_memory(test_memory_id)
        assert retrieved is not None
        assert retrieved.content == (content + "_test").strip()
        
        # Verify we can still retrieve from base context
        base_retrieved = self.router.retrieve_memory(base_memory_id, "base")
        assert base_retrieved is not None
        assert base_retrieved.content == content.strip()
    
    @given(
        content=text(min_size=1, max_size=100),
        importance=floats(min_value=0.0, max_value=1.0),
        tags=lists(text(min_size=1, max_size=10), max_size=5),
    )
    @settings(deadline=None)
    def test_router_search_across_contexts(self, content, importance, tags):
        """Test that router can search across contexts."""
        robust_content_guard(content)
        
        # Create a test context
        context_id = "test_context"
        self.router.create_context(context_id)
        
        # Save memory in base context
        self.router.save_memory(content, importance, tags, "base")
        
        # Save memory in test context
        self.router.save_memory(content + "_test", importance, tags, context_id)
        
        # Search in base context
        base_results = self.router.search_memories(content, context_id="base")
        assert len(base_results) > 0
        
        # Search in test context
        test_results = self.router.search_memories(content, context_id=context_id)
        assert len(test_results) > 0
        
        # Search across all contexts (active context is base)
        all_results = self.router.search_memories(content)
        assert len(all_results) > 0
    
    @given(
        content=text(min_size=1, max_size=100),
        importance=floats(min_value=0.0, max_value=1.0),
        tags=lists(text(min_size=1, max_size=10), max_size=5),
    )
    @settings(deadline=None)
    def test_router_context_management(self, content, importance, tags):
        """Test context creation, listing, and deletion."""
        robust_content_guard(content)
        
        # Create a test context
        context_id = "test_context"
        success = self.router.create_context(context_id)
        assert success is True
        
        # Verify context is listed
        contexts = self.router.list_contexts()
        assert context_id in contexts
        assert "base" in contexts
        
        # Save memory in the context
        memory_id = self.router.save_memory(content, importance, tags, context_id)
        
        # Verify memory exists
        retrieved = self.router.retrieve_memory(memory_id, context_id)
        assert retrieved is not None
        
        # Delete context
        success = self.router.delete_context(context_id)
        assert success is True
        
        # Verify context is gone
        contexts = self.router.list_contexts()
        assert context_id not in contexts
        
        # Verify memory is gone
        retrieved = self.router.retrieve_memory(memory_id, context_id)
        assert retrieved is None