# Architecture Overview

Learn how AIMemo works under the hood and how it integrates with your LLM applications.

## High-Level Architecture

AIMemo works by **intercepting** LLM API calls, injecting relevant context before the call, and storing conversations after:

```
┌─────────────┐
│  Your App   │
└──────┬──────┘
       │ 1. client.chat.completions.create(messages=[...])
       ▼
┌─────────────────────┐
│ AIMemo Interceptor  │
└──────┬──────────────┘
       │ 2. Search Relevant Context
       ▼
┌─────────────────────┐
│   SQL Database      │  ← Full-text search (FTS5/PostgreSQL)
│  ┌───────────────┐  │
│  │   Memories    │  │
│  │  Namespace A  │  │
│  │  Namespace B  │  │
│  └───────────────┘  │
└──────┬──────────────┘
       │ 3. Return relevant memories
       ▼
┌─────────────────────┐
│ AIMemo Interceptor  │
└──────┬──────────────┘
       │ 4. Inject Context + Forward Call
       ▼
┌─────────────────────┐
│  LLM Provider       │
│  (OpenAI/Anthropic) │
└──────┬──────────────┘
       │ 5. Return Response
       ▼
┌─────────────────────┐
│ AIMemo Interceptor  │
└──────┬──────────────┘
       │ 6. Store Conversation
       ▼
┌─────────────────────┐
│   SQL Database      │
└─────────────────────┘
       │ 7. Return Response
       ▼
┌─────────────┐
│  Your App   │
└─────────────┘
```

## Core Components

### 1. AIMemo Core (`aimemo/core.py`)

The main class that orchestrates the entire system:

```python
class AIMemo:
    """
    Main memory system that intercepts LLM calls.
    
    Components:
    - Store: Database backend (SQLite/PostgreSQL)
    - Config: Configuration settings
    - Providers: LLM provider interceptors
    - Namespace: Memory isolation
    """
    
    def enable(self):
        """Enable memory interception"""
        
    def disable(self):
        """Disable memory interception"""
        
    def add_memory(self, content, metadata, tags):
        """Manually add a memory"""
        
    def search(self, query, limit, tags):
        """Search memories by query"""
```

**Responsibilities:**
- Initialize storage backend
- Enable/disable provider interceptors
- Provide manual memory management API
- Handle namespace isolation

### 2. Storage Layer (`aimemo/storage.py`)

Abstraction over different database backends:

```python
class MemoryStore(ABC):
    """Abstract storage interface"""
    
    @abstractmethod
    def save(self, memory: Dict) -> None:
        """Save a memory"""
        
    @abstractmethod
    def search(self, query: str, namespace: str, limit: int) -> List[Dict]:
        """Search memories with full-text search"""
        
    @abstractmethod
    def clear(self, namespace: str) -> None:
        """Clear memories for a namespace"""
```

**Implementations:**
- `SQLiteStore`: Uses FTS5 for full-text search
- `PostgresStore`: Uses PostgreSQL full-text search

### 3. Provider Interceptors (`aimemo/providers.py`)

Intercept and augment LLM API calls:

```python
class OpenAIProvider:
    """Intercept OpenAI API calls"""
    
    def enable(self):
        """Patch openai.ChatCompletion.create()"""
        
    def _intercept_call(self, original_func, *args, **kwargs):
        # 1. Extract messages from call
        # 2. Search relevant context
        # 3. Inject context into messages
        # 4. Call original function
        # 5. Store conversation
        # 6. Return response
```

**Responsibilities:**
- Monkey-patch LLM provider APIs
- Extract messages and metadata
- Inject context before call
- Store conversations after call

### 4. Configuration (`aimemo/config.py`)

Centralized configuration management:

```python
class Config:
    """Configuration object"""
    
    db_path: str = "./aimemo.db"
    max_context: int = 5
    search_limit: int = 10
    enable_cache: bool = True
```

## How It Works: Step by Step

### Pre-Call: Context Injection

1. **User makes LLM call**
   ```python
   response = client.chat.completions.create(
       model="gpt-4o-mini",
       messages=[{"role": "user", "content": "How do I use FastAPI?"}]
   )
   ```

2. **AIMemo intercepts the call**
   - Extracts the user's query: "How do I use FastAPI?"
   - Searches for relevant memories in the database

3. **Full-text search**
   ```sql
   -- SQLite FTS5
   SELECT content, metadata, rank
   FROM memories_fts
   WHERE memories_fts MATCH 'FastAPI'
   AND namespace = 'default'
   ORDER BY rank
   LIMIT 5;
   ```

4. **Context injection**
   ```python
   # Original messages
   messages = [
       {"role": "user", "content": "How do I use FastAPI?"}
   ]
   
   # After context injection
   messages = [
       {"role": "system", "content": "Previous context:\n- User is building a FastAPI project\n- User prefers async/await syntax"},
       {"role": "user", "content": "How do I use FastAPI?"}
   ]
   ```

5. **Forward to LLM**
   - Modified messages sent to OpenAI/Anthropic

### Post-Call: Memory Storage

1. **LLM returns response**
   ```python
   response = {
       "choices": [{
           "message": {
               "role": "assistant",
               "content": "To use FastAPI, first install it: pip install fastapi..."
           }
       }]
   }
   ```

2. **AIMemo stores conversation**
   ```python
   memory = {
       "id": generate_id(),
       "content": "User asked: How do I use FastAPI?\nAssistant replied: To use FastAPI...",
       "metadata": {
           "model": "gpt-4o-mini",
           "tokens": 150
       },
       "tags": ["fastapi", "question"],
       "namespace": "default",
       "timestamp": "2025-11-16T10:00:00Z"
   }
   
   store.save(memory)
   ```

3. **Return response**
   - Original response returned to user
   - User sees no difference in behavior

## Database Schema

### SQLite Schema

```sql
-- Main memories table
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSON,
    tags JSON,
    namespace TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

-- Full-text search index
CREATE VIRTUAL TABLE memories_fts USING fts5(
    content,
    namespace UNINDEXED,
    content='memories',
    content_rowid='rowid'
);

-- Indexes
CREATE INDEX idx_namespace ON memories(namespace);
CREATE INDEX idx_timestamp ON memories(timestamp);
CREATE INDEX idx_tags ON memories(tags);
```

### PostgreSQL Schema

```sql
-- Main memories table
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    tags TEXT[],
    namespace TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    search_vector tsvector
);

-- Full-text search index
CREATE INDEX memories_search_idx ON memories USING GIN(search_vector);

-- Indexes
CREATE INDEX idx_namespace ON memories(namespace);
CREATE INDEX idx_timestamp ON memories(timestamp);
CREATE INDEX idx_tags ON memories USING GIN(tags);
```

## Namespace Isolation

Namespaces provide complete memory isolation:

```python
# User A's memory
user_a = AIMemo(namespace="user_a")
user_a.add_memory("I like Python")

# User B's memory
user_b = AIMemo(namespace="user_b")
user_b.add_memory("I like JavaScript")

# Searching
user_a.search("programming")  # Returns: "I like Python"
user_b.search("programming")  # Returns: "I like JavaScript"
```

**Implementation:**
- All database queries include `WHERE namespace = ?`
- No cross-namespace data leakage
- Each namespace has isolated full-text search index

## Memory Retrieval Algorithm

### Search Scoring

1. **Full-text search** (primary ranking)
   - Uses BM25 algorithm (SQLite) or ts_rank (PostgreSQL)
   - Matches words, stems, and phrases

2. **Tag filtering** (optional)
   ```python
   results = aimemo.search(
       query="python",
       tags=["tutorial", "beginner"]
   )
   ```

3. **Recency boost** (implicit)
   - Recent memories slightly favored
   - Configurable via timestamp weighting

### Context Selection

```python
def get_context(query: str, limit: int = 5) -> str:
    # 1. Search memories
    memories = self.search(query, limit=limit)
    
    # 2. Format context
    context_parts = ["Previous context:"]
    for mem in memories:
        context_parts.append(f"- {mem['content']}")
    
    # 3. Return formatted string
    return "\n".join(context_parts)
```

## Performance Characteristics

### Latency

- **Context search**: 1-5ms (SQLite), 2-10ms (PostgreSQL)
- **Memory save**: 1-3ms (SQLite), 2-8ms (PostgreSQL)
- **Total overhead**: 5-20ms per LLM call

### Scalability

- **SQLite**: Suitable for 1-10K memories, single user
- **PostgreSQL**: Suitable for 1M+ memories, thousands of users

### Token Usage

- **Context injection**: 50-200 tokens per request (configurable)
- **Cost impact**: ~2-5% increase in token usage

## Security Considerations

### 1. Namespace Isolation

- Complete data isolation per namespace
- No cross-namespace queries possible

### 2. SQL Injection Prevention

```python
# All queries use parameterized statements
cursor.execute(
    "SELECT * FROM memories WHERE namespace = ?",
    (namespace,)
)
```

### 3. Data Encryption

- Use database-level encryption for sensitive data
- PostgreSQL: pgcrypto extension
- SQLite: SQLCipher extension

### 4. API Key Security

- Never log API keys
- Store in environment variables
- Use secret management in production

## Best Practices

### 1. Choose the Right Backend

- **Development**: SQLite (simple, zero config)
- **Production**: PostgreSQL (scalable, concurrent)

### 2. Optimize Context Limits

```python
# Balance relevance vs token cost
config = Config(max_context=5)  # Usually optimal
```

### 3. Use Namespaces

```python
# Isolate per user/tenant/session
aimemo = AIMemo(namespace=f"user_{user_id}")
```

### 4. Clean Up Old Memories

```python
# Periodic cleanup
aimemo.store.delete_old_memories(days=30)
```

## Extending AIMemo

### Custom Storage Backend

```python
from aimemo.storage import MemoryStore

class RedisStore(MemoryStore):
    def save(self, memory: Dict) -> None:
        # Implement Redis storage
        pass
    
    def search(self, query: str, namespace: str, limit: int) -> List[Dict]:
        # Implement Redis search
        pass
```

### Custom Provider

```python
from aimemo.providers import BaseProvider

class CustomProvider(BaseProvider):
    def enable(self):
        # Patch custom LLM library
        pass
```

## Next Steps

- [Configuration](configuration.md) - Configure for your needs
- [Storage Backends](storage-backends.md) - Deep dive into databases
- [API Reference](api-reference.md) - Complete API docs

