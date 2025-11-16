# AIMemo Implementation Guide - First Features

This guide provides detailed implementation steps for the first critical features to bring AIMemo closer to Memori's capabilities.

---

## 🎯 Feature #1: Entity Extraction (2-3 days)

### Overview
Extract meaningful entities from conversations: names, dates, preferences, facts.

### File Structure
```
aimemo/
  extractors.py          # New file
  core.py                # Modify
tests/
  test_extractors.py     # New file
```

### Implementation Steps

#### Step 1: Create Base Extractor Class

```python
# aimemo/extractors.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Entity:
    """Represents an extracted entity."""
    type: str           # "person", "date", "preference", "fact"
    value: str          # The actual entity value
    context: str        # Surrounding context
    confidence: float   # 0.0 to 1.0
    position: int       # Position in text

class EntityExtractor(ABC):
    """Base class for entity extraction."""
    
    @abstractmethod
    def extract(self, text: str) -> List[Entity]:
        """Extract entities from text."""
        pass

class SimpleExtractor(EntityExtractor):
    """Simple rule-based entity extractor."""
    
    def extract(self, text: str) -> List[Entity]:
        entities = []
        entities.extend(self._extract_names(text))
        entities.extend(self._extract_dates(text))
        entities.extend(self._extract_preferences(text))
        return entities
    
    def _extract_names(self, text: str) -> List[Entity]:
        """Extract person names using simple patterns."""
        import re
        # Pattern for capitalized words (simple approach)
        pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        matches = re.finditer(pattern, text)
        
        entities = []
        for match in matches:
            entities.append(Entity(
                type="person",
                value=match.group(),
                context=self._get_context(text, match.start(), match.end()),
                confidence=0.6,  # Low confidence for simple pattern
                position=match.start()
            ))
        return entities
    
    def _extract_dates(self, text: str) -> List[Entity]:
        """Extract dates using patterns."""
        import re
        # Simple date patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2}',  # 2025-11-16
            r'\d{1,2}/\d{1,2}/\d{4}',  # 11/16/2025
            r'(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? \d{4}'
        ]
        
        entities = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(Entity(
                    type="date",
                    value=match.group(),
                    context=self._get_context(text, match.start(), match.end()),
                    confidence=0.8,
                    position=match.start()
                ))
        return entities
    
    def _extract_preferences(self, text: str) -> List[Entity]:
        """Extract user preferences."""
        import re
        # Patterns for preferences
        preference_patterns = [
            r'I (like|love|prefer|enjoy) (.+?)[\.\,\!]',
            r'I (don\'t like|hate|dislike) (.+?)[\.\,\!]',
            r'My favorite (.+?) is (.+?)[\.\,\!]',
        ]
        
        entities = []
        for pattern in preference_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(Entity(
                    type="preference",
                    value=match.group(),
                    context=self._get_context(text, match.start(), match.end()),
                    confidence=0.7,
                    position=match.start()
                ))
        return entities
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get surrounding context for an entity."""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
```

#### Step 2: Integrate into Core

```python
# aimemo/core.py
from .extractors import SimpleExtractor, Entity

class AIMemo:
    def __init__(self, ...):
        # ... existing code ...
        self.extractor = SimpleExtractor()
    
    def add_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        extract_entities: bool = True,  # New parameter
    ) -> str:
        """Add memory with optional entity extraction."""
        
        # Extract entities if enabled
        entities = []
        if extract_entities:
            entities = self.extractor.extract(content)
        
        # Update metadata with entities
        if metadata is None:
            metadata = {}
        
        metadata["entities"] = [
            {
                "type": e.type,
                "value": e.value,
                "confidence": e.confidence
            }
            for e in entities
        ]
        
        # ... rest of existing code ...
```

#### Step 3: Tests

```python
# tests/test_extractors.py
import pytest
from aimemo.extractors import SimpleExtractor, Entity

def test_extract_names():
    extractor = SimpleExtractor()
    text = "I met John Smith yesterday."
    
    entities = extractor.extract(text)
    names = [e for e in entities if e.type == "person"]
    
    assert len(names) == 1
    assert names[0].value == "John Smith"

def test_extract_dates():
    extractor = SimpleExtractor()
    text = "The meeting is on 2025-11-16."
    
    entities = extractor.extract(text)
    dates = [e for e in entities if e.type == "date"]
    
    assert len(dates) == 1
    assert dates[0].value == "2025-11-16"

def test_extract_preferences():
    extractor = SimpleExtractor()
    text = "I love Python programming."
    
    entities = extractor.extract(text)
    prefs = [e for e in entities if e.type == "preference"]
    
    assert len(prefs) >= 1
```

---

## 🎯 Feature #2: Memory Categorization (2 days)

### Overview
Categorize memories into types: FACT, PREFERENCE, SKILL, RULE, CONTEXT

### File Structure
```
aimemo/
  categorizer.py         # New file
  core.py                # Modify
  storage.py             # Modify (add category column)
```

### Implementation Steps

#### Step 1: Create Categorizer

```python
# aimemo/categorizer.py
from enum import Enum
from typing import List, Dict
import re

class MemoryCategory(Enum):
    """Memory category types."""
    FACT = "fact"               # Objective information
    PREFERENCE = "preference"   # User likes/dislikes
    SKILL = "skill"             # User capabilities
    RULE = "rule"               # Business logic, constraints
    CONTEXT = "context"         # Background information
    UNKNOWN = "unknown"         # Uncategorized

class MemoryCategorizer:
    """Categorize memories based on content."""
    
    def __init__(self):
        self.patterns = {
            MemoryCategory.PREFERENCE: [
                r'\b(like|love|prefer|enjoy|hate|dislike)\b',
                r'\bfavorite\b',
                r'\b(want|need)\b'
            ],
            MemoryCategory.SKILL: [
                r'\b(can|able to|know how to|learned|studied)\b',
                r'\b(expert|proficient|familiar) with\b',
                r'\b(programming|coding|building|developing)\b'
            ],
            MemoryCategory.RULE: [
                r'\b(must|should|always|never|required)\b',
                r'\b(policy|rule|requirement)\b',
                r'\b(allowed|forbidden|prohibited)\b'
            ],
            MemoryCategory.FACT: [
                r'\b(is|are|was|were)\b',
                r'\b\d+\b',  # Contains numbers
                r'\b(named|called|known as)\b'
            ]
        }
    
    def categorize(self, content: str) -> MemoryCategory:
        """Categorize memory content."""
        content_lower = content.lower()
        
        scores = {cat: 0 for cat in MemoryCategory}
        
        # Score each category based on pattern matches
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, content_lower))
                scores[category] += matches
        
        # Get highest scoring category
        max_score = max(scores.values())
        if max_score == 0:
            return MemoryCategory.UNKNOWN
        
        return max(scores, key=scores.get)
    
    def categorize_with_confidence(self, content: str) -> tuple[MemoryCategory, float]:
        """Categorize with confidence score."""
        category = self.categorize(content)
        
        # Calculate confidence (simple approach)
        content_lower = content.lower()
        matches = 0
        total_patterns = 0
        
        if category in self.patterns:
            for pattern in self.patterns[category]:
                total_patterns += 1
                if re.search(pattern, content_lower):
                    matches += 1
        
        confidence = matches / max(total_patterns, 1)
        return category, confidence
```

#### Step 2: Update Storage Schema

```python
# aimemo/storage.py - Modify SQLiteStore

def _init_db(self):
    """Initialize database schema."""
    with sqlite3.connect(self.db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                metadata TEXT,
                tags TEXT,
                category TEXT DEFAULT 'unknown',  -- NEW
                namespace TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add index for category
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON memories(category)
        """)
        
        # ... rest of schema ...

def search(
    self,
    query: str,
    namespace: str,
    limit: int = 5,
    tags: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,  # NEW
) -> List[Dict[str, Any]]:
    """Search with category filter."""
    # ... existing code with category filter ...
```

#### Step 3: Integrate into Core

```python
# aimemo/core.py
from .categorizer import MemoryCategorizer, MemoryCategory

class AIMemo:
    def __init__(self, ...):
        # ... existing code ...
        self.categorizer = MemoryCategorizer()
    
    def add_memory(self, content: str, ...):
        """Add memory with categorization."""
        
        # Categorize memory
        category, confidence = self.categorizer.categorize_with_confidence(content)
        
        # Update metadata
        if metadata is None:
            metadata = {}
        metadata["category_confidence"] = confidence
        
        memory = {
            # ... existing fields ...
            "category": category.value,
        }
        
        self.store.save(memory)
```

---

## 🎯 Feature #3: Memory Modes (3-4 days)

### Overview
Implement conscious mode (working memory) and auto mode (dynamic search).

### File Structure
```
aimemo/
  modes.py               # New file
  core.py                # Modify
```

### Implementation Steps

#### Step 1: Create Modes System

```python
# aimemo/modes.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from collections import deque
from datetime import datetime, timedelta

class MemoryMode(ABC):
    """Base class for memory injection modes."""
    
    @abstractmethod
    def get_context(self, query: str, aimemo: Any) -> str:
        """Get context for a query."""
        pass

class ConsciousMode(MemoryMode):
    """Working memory - maintains recent context in memory."""
    
    def __init__(self, max_memories: int = 10, ttl_minutes: int = 30):
        self.max_memories = max_memories
        self.ttl = timedelta(minutes=ttl_minutes)
        self.working_memory = deque(maxlen=max_memories)
    
    def add_to_working_memory(self, content: str, metadata: Dict = None):
        """Add to working memory."""
        self.working_memory.append({
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow()
        })
    
    def get_context(self, query: str, aimemo: Any) -> str:
        """Get context from working memory."""
        # Remove expired memories
        cutoff = datetime.utcnow() - self.ttl
        valid_memories = [
            m for m in self.working_memory
            if m["timestamp"] > cutoff
        ]
        self.working_memory = deque(valid_memories, maxlen=self.max_memories)
        
        if not self.working_memory:
            return ""
        
        # Format working memory as context
        context_parts = ["Recent working memory:"]
        for mem in self.working_memory:
            context_parts.append(f"- {mem['content']}")
        
        return "\n".join(context_parts)

class AutoMode(MemoryMode):
    """Dynamic search - searches database for relevant context."""
    
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
    
    def get_context(self, query: str, aimemo: Any) -> str:
        """Get context via dynamic search."""
        memories = aimemo.search(query, limit=self.max_results)
        
        if not memories:
            return ""
        
        context_parts = ["Relevant memories:"]
        for mem in memories:
            context_parts.append(f"- {mem['content']}")
        
        return "\n".join(context_parts)

class CombinedMode(MemoryMode):
    """Combined - both working memory and dynamic search."""
    
    def __init__(
        self,
        working_memory_size: int = 5,
        search_results: int = 3,
        ttl_minutes: int = 30
    ):
        self.conscious = ConsciousMode(working_memory_size, ttl_minutes)
        self.auto = AutoMode(search_results)
    
    def get_context(self, query: str, aimemo: Any) -> str:
        """Get combined context."""
        contexts = []
        
        # Get working memory
        conscious_ctx = self.conscious.get_context(query, aimemo)
        if conscious_ctx:
            contexts.append(conscious_ctx)
        
        # Get search results
        auto_ctx = self.auto.get_context(query, aimemo)
        if auto_ctx:
            contexts.append(auto_ctx)
        
        return "\n\n".join(contexts)
```

#### Step 2: Integrate into Core

```python
# aimemo/core.py
from .modes import ConsciousMode, AutoMode, CombinedMode

class AIMemo:
    def __init__(
        self,
        store: Optional[MemoryStore] = None,
        config: Optional[Config] = None,
        namespace: str = "default",
        auto_enable: bool = False,
        conscious_ingest: bool = False,  # NEW
        auto_ingest: bool = False,        # NEW
    ):
        # ... existing code ...
        
        # Set up memory mode
        if conscious_ingest and auto_ingest:
            self.mode = CombinedMode()
        elif conscious_ingest:
            self.mode = ConsciousMode()
        elif auto_ingest:
            self.mode = AutoMode()
        else:
            self.mode = AutoMode()  # Default
    
    def get_context(self, query: str, limit: int = 5) -> str:
        """Get context using configured mode."""
        return self.mode.get_context(query, self)
```

#### Step 3: Update Providers

```python
# aimemo/providers.py - OpenAIProvider

@staticmethod
def _store_conversation(messages: List[Dict], response: Any, aimemo: "AIMemo"):
    """Store and update working memory."""
    # ... existing storage code ...
    
    # Update working memory if using conscious mode
    if isinstance(aimemo.mode, (ConsciousMode, CombinedMode)):
        if user_msg and assistant_msg:
            aimemo.mode.conscious.add_to_working_memory(
                f"User: {user_msg}\nAssistant: {assistant_msg}",
                {"type": "conversation"}
            )
```

---

## 🚀 Quick Start Implementation

### Day 1: Entity Extraction
- [ ] Create `aimemo/extractors.py`
- [ ] Implement `SimpleExtractor`
- [ ] Add tests
- [ ] Integrate into `core.py`
- [ ] Test end-to-end

### Day 2: Memory Categorization
- [ ] Create `aimemo/categorizer.py`
- [ ] Update database schema
- [ ] Add category to storage
- [ ] Add tests
- [ ] Integrate into `core.py`

### Day 3-4: Memory Modes
- [ ] Create `aimemo/modes.py`
- [ ] Implement all three modes
- [ ] Add tests
- [ ] Integrate into `core.py` and providers
- [ ] Test with OpenAI/Anthropic

### Day 5: Testing & Documentation
- [ ] Write comprehensive tests
- [ ] Update documentation
- [ ] Create examples
- [ ] Run test suite
- [ ] Create PR

---

## 🧪 Testing Strategy

### Unit Tests
```python
# Test entity extraction
pytest tests/test_extractors.py -v

# Test categorization
pytest tests/test_categorizer.py -v

# Test modes
pytest tests/test_modes.py -v
```

### Integration Tests
```python
# Test with real LLM calls
pytest tests/test_integration.py -v --run-integration
```

### Manual Testing
```python
from aimemo import AIMemo
from openai import OpenAI

# Test conscious mode
aimemo = AIMemo(conscious_ingest=True)
aimemo.enable()

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "I love Python"}]
)

# Check working memory
print(aimemo.mode.working_memory)
```

---

## 📚 Next Steps

After implementing these three features:

1. **LiteLLM Integration** - Support 100+ models
2. **Vector Embeddings** - Semantic search
3. **Memory Agents** - Background processing
4. **LangChain Integration** - Framework support

---

## 💡 Tips

- Start with simple implementations
- Add tests as you go
- Keep backward compatibility
- Update documentation
- Get community feedback early

---

**Good luck with the implementation!** 🚀

