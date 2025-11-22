"""
Unit tests for AIMemo core functionality
"""

import pytest
import tempfile
from pathlib import Path

from aimemo import AIMemo, SQLiteStore


@pytest.fixture
def temp_db():
    """Create a temporary database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def aimemo(temp_db):
    """Create AIMemo instance with temp database."""
    store = SQLiteStore(temp_db)
    return AIMemo(store=store, namespace="test")


def test_add_memory(aimemo):
    """Test adding a memory."""
    memory_id = aimemo.add_memory("This is a test memory")
    assert memory_id is not None
    assert len(memory_id) == 16


def test_search_memory(aimemo):
    """Test searching memories."""
    aimemo.add_memory("I love Python programming")
    aimemo.add_memory("JavaScript is also great")
    
    results = aimemo.search("Python", limit=5)
    assert len(results) > 0
    assert "Python" in results[0]["content"]


def test_get_context(aimemo):
    """Test getting formatted context."""
    aimemo.add_memory("User is a data scientist")
    aimemo.add_memory("User prefers Python")
    
    context = aimemo.get_context("scientist")
    assert "Previous context:" in context
    assert "data scientist" in context.lower()


def test_clear_memories(aimemo):
    """Test clearing memories."""
    aimemo.add_memory("Test memory 1")
    aimemo.add_memory("Test memory 2")
    
    aimemo.clear()
    
    results = aimemo.search("Test", limit=10)
    assert len(results) == 0


def test_namespace_isolation(temp_db):
    """Test that namespaces are isolated."""
    store = SQLiteStore(temp_db)
    
    aimemo1 = AIMemo(store=store, namespace="user1")
    aimemo2 = AIMemo(store=store, namespace="user2")
    
    aimemo1.add_memory("User 1 memory")
    aimemo2.add_memory("User 2 memory")
    
    results1 = aimemo1.search("User", limit=10)
    results2 = aimemo2.search("User", limit=10)
    
    assert len(results1) == 1
    assert len(results2) == 1
    assert "User 1" in results1[0]["content"]
    assert "User 2" in results2[0]["content"]


def test_memory_with_tags(aimemo):
    """Test adding memory with tags."""
    memory_id = aimemo.add_memory(
        "Test content",
        tags=["test", "example"]
    )
    
    results = aimemo.search("Test", limit=5)
    assert len(results) > 0
    assert "test" in results[0]["tags"]


def test_memory_with_metadata(aimemo):
    """Test adding memory with metadata."""
    memory_id = aimemo.add_memory(
        "Test content",
        metadata={"source": "test", "priority": "high"}
    )
    
    results = aimemo.search("Test", limit=5)
    assert len(results) > 0
    assert results[0]["metadata"]["source"] == "test"


def test_enable_disable(aimemo):
    """Test enable/disable functionality."""
    assert not aimemo._enabled
    
    aimemo.enable()
    assert aimemo._enabled
    
    aimemo.disable()
    assert not aimemo._enabled


def test_context_manager(temp_db):
    """Test context manager usage."""
    store = SQLiteStore(temp_db)
    
    with AIMemo(store=store) as aimemo:
        assert aimemo._enabled
        aimemo.add_memory("Test memory")
    
    # Should be disabled after exiting context
    assert not aimemo._enabled


def test_working_memory(aimemo):
    """Test working memory functionality."""
    aimemo.add_to_working_memory("Important fact")
    assert len(aimemo._working_memory) == 1
    
    # Test limit
    limit = aimemo.config.working_memory_limit
    for i in range(limit + 2):
        aimemo.add_to_working_memory(f"Fact {i}")
        
    assert len(aimemo._working_memory) == limit
    assert aimemo._working_memory[-1]["content"] == f"Fact {limit + 1}"


def test_conscious_mode(temp_db):
    """Test conscious mode context injection."""
    store = SQLiteStore(temp_db)
    aimemo = AIMemo(store=store, conscious_ingest=True)
    
    aimemo.add_to_working_memory("I am in conscious mode")
    
    context = aimemo.get_context("test")
    assert "Working Memory:" in context
    assert "I am in conscious mode" in context


def test_auto_mode_fallback(temp_db):
    """Test fallback to auto mode (search)."""
    store = SQLiteStore(temp_db)
    aimemo = AIMemo(store=store, conscious_ingest=False, auto_ingest=True)
    
    aimemo.add_memory("Stored memory")
    
    context = aimemo.get_context("Stored")
    assert "Previous context:" in context
    assert "Stored memory" in context

