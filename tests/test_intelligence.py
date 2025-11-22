"""
Tests for v1.1 intelligence features.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from aimemo import AIMemo, SQLiteStore
from aimemo.extractors import RegexEntityExtractor
from aimemo.categorizer import KeywordCategorizer, MemoryCategory


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


def test_entity_extraction():
    """Test regex entity extraction."""
    extractor = RegexEntityExtractor()
    
    text = "Meeting with John Doe on 2023-10-25 at test@example.com"
    entities = extractor.extract(text)
    
    assert len(entities) >= 3
    
    types = [e.type for e in entities]
    assert "name" in types
    assert "date" in types
    assert "email" in types
    
    names = [e.value for e in entities if e.type == "name"]
    assert "John Doe" in names


def test_categorization():
    """Test keyword categorization."""
    categorizer = KeywordCategorizer()
    
    assert categorizer.categorize("I love Python") == MemoryCategory.PREFERENCE
    assert categorizer.categorize("I can code in Rust") == MemoryCategory.SKILL
    assert categorizer.categorize("Always write tests") == MemoryCategory.RULE
    assert categorizer.categorize("Paris is in France") == MemoryCategory.FACT
    assert categorizer.categorize("Just some random text") == MemoryCategory.CONTEXT


def test_auto_intelligence(aimemo):
    """Test automatic extraction and categorization on add_memory."""
    content = "I prefer using PostgreSQL for databases"
    
    memory_id = aimemo.add_memory(content)
    
    # Verify storage
    results = aimemo.search("PostgreSQL", limit=1)
    assert len(results) == 1
    memory = results[0]
    
    # Check category
    assert memory["category"] == MemoryCategory.PREFERENCE
    
    # Check extracted entities (PostgreSQL might be extracted as a name with our simple regex)
    # Note: Our simple regex expects "First Last", so "PostgreSQL" might not be caught as a name.
    # Let's try a clearer example for entities.
    
    content2 = "Meeting with Alice Smith on 2024-01-01"
    aimemo.add_memory(content2)
    results = aimemo.search("Alice", limit=1)
    memory = results[0]
    
    assert len(memory["metadata"]["entities"]) > 0
    entity_types = [e["type"] for e in memory["metadata"]["entities"]]
    assert "name" in entity_types
    assert "date" in entity_types


def test_category_filtering(aimemo):
    """Test filtering search results by category."""
    aimemo.add_memory("I like coffee", category=MemoryCategory.PREFERENCE)
    aimemo.add_memory("Coffee is a drink", category=MemoryCategory.FACT)
    
    prefs = aimemo.search("coffee", category=MemoryCategory.PREFERENCE)
    assert len(prefs) == 1
    assert prefs[0]["content"] == "I like coffee"
    
    facts = aimemo.search("coffee", category=MemoryCategory.FACT)
    assert len(facts) == 1
    assert facts[0]["content"] == "Coffee is a drink"


def test_context_retrieval_scoring(aimemo):
    """Test that recent memories are ranked higher."""
    # Old memory
    old_time = (datetime.utcnow() - timedelta(days=10)).isoformat()
    aimemo.store.save({
        "id": "old",
        "content": "Python is good",
        "metadata": {},
        "tags": [],
        "namespace": "test",
        "timestamp": old_time,
        "category": "fact"
    })
    
    # New memory
    new_time = datetime.utcnow().isoformat()
    aimemo.store.save({
        "id": "new",
        "content": "Python is great",
        "metadata": {},
        "tags": [],
        "namespace": "test",
        "timestamp": new_time,
        "category": "fact"
    })
    
    # Get context
    context = aimemo.get_context("Python")
    
    # New memory should appear first (or be present)
    assert "Python is great" in context
    
    # Verify order in raw retrieval
    memories = aimemo.retriever.get_relevant_context("Python", "test", recency_weight=0.6)
    assert len(memories) >= 2
    assert memories[0]["id"] == "new"  # Should be ranked higher due to recency
