# API Reference

Complete API documentation for AIMemo.

## Core Classes

### AIMemo

Main entry point for the memory system.

```python
class AIMemo:
    def __init__(
        self,
        store: Optional[MemoryStore] = None,
        config: Optional[Config] = None,
        namespace: str = "default",
        auto_enable: bool = False,
    )
```

**Parameters:**
- `store` (MemoryStore, optional): Storage backend. Defaults to SQLiteStore.
- `config` (Config, optional): Configuration object. Defaults to default Config.
- `namespace` (str): Namespace for memory isolation. Default: "default"
- `auto_enable` (bool): Automatically enable on initialization. Default: False

**Example:**
```python
from aimemo import AIMemo, PostgresStore, Config

config = Config(max_context=10)
store = PostgresStore("postgresql://...")
aimemo = AIMemo(store=store, config=config, namespace="user_123")
```

#### Methods

##### `enable()`

Enable memory interception for LLM calls.

```python
def enable(self) -> None
```

**Example:**
```python
aimemo = AIMemo()
aimemo.enable()  # Start intercepting LLM calls
```

##### `disable()`

Disable memory interception.

```python
def disable(self) -> None
```

**Example:**
```python
aimemo.disable()  # Stop intercepting
```

##### `add_memory()`

Manually add a memory.

```python
def add_memory(
    self,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
) -> str
```

**Parameters:**
- `content` (str): Memory content
- `metadata` (dict, optional): Additional metadata
- `tags` (list, optional): Tags for categorization

**Returns:**
- `str`: Memory ID

**Example:**
```python
memory_id = aimemo.add_memory(
    content="User prefers dark mode",
    tags=["preference", "ui"],
    metadata={"priority": "high", "source": "settings"}
)
print(f"Memory ID: {memory_id}")
```

##### `search()`

Search memories by query.

```python
def search(
    self,
    query: str,
    limit: int = 5,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]
```

**Parameters:**
- `query` (str): Search query
- `limit` (int): Maximum number of results. Default: 5
- `tags` (list, optional): Filter by tags

**Returns:**
- `List[Dict]`: List of matching memories

**Example:**
```python
# Basic search
results = aimemo.search("Python tutorial", limit=10)

# Search with tag filter
results = aimemo.search(
    query="authentication",
    tags=["security", "fastapi"],
    limit=5
)

for memory in results:
    print(f"- {memory['content']}")
    print(f"  Tags: {memory['tags']}")
```

##### `get_context()`

Get formatted context for a query.

```python
def get_context(self, query: str, limit: int = 5) -> str
```

**Parameters:**
- `query` (str): Query to find context for
- `limit` (int): Number of memories to retrieve. Default: 5

**Returns:**
- `str`: Formatted context string

**Example:**
```python
context = aimemo.get_context("FastAPI authentication", limit=3)
print(context)
# Output:
# Previous context:
# - User is building a FastAPI project
# - User asked about JWT authentication
# - User prefers async/await syntax
```

##### `clear()`

Clear memories for a namespace.

```python
def clear(self, namespace: Optional[str] = None) -> None
```

**Parameters:**
- `namespace` (str, optional): Namespace to clear. Defaults to current namespace.

**Example:**
```python
# Clear current namespace
aimemo.clear()

# Clear specific namespace
aimemo.clear(namespace="user_123")
```

##### Context Manager Support

AIMemo can be used as a context manager:

```python
with AIMemo(namespace="session_123") as aimemo:
    # Memory is automatically enabled
    client.chat.completions.create(...)
# Memory is automatically disabled
```

---

## Storage Classes

### MemoryStore (Abstract Base Class)

```python
class MemoryStore(ABC):
    @abstractmethod
    def save(self, memory: Dict[str, Any]) -> None
    
    @abstractmethod
    def search(
        self,
        query: str,
        namespace: str,
        limit: int,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]
    
    @abstractmethod
    def clear(self, namespace: str) -> None
```

### SQLiteStore

SQLite-based storage with FTS5 full-text search.

```python
class SQLiteStore(MemoryStore):
    def __init__(self, db_path: str = "./aimemo.db")
```

**Parameters:**
- `db_path` (str): Path to SQLite database file. Default: "./aimemo.db"

**Example:**
```python
from aimemo import SQLiteStore, AIMemo

# Default path
store = SQLiteStore()

# Custom path
store = SQLiteStore("/path/to/memory.db")

aimemo = AIMemo(store=store)
```

**Methods:**
- Inherits all methods from `MemoryStore`
- Uses FTS5 for full-text search
- Automatic index creation

### PostgresStore

PostgreSQL-based storage with full-text search.

```python
class PostgresStore(MemoryStore):
    def __init__(
        self,
        connection_string: str,
        pool_size: int = 5,
        max_overflow: int = 10
    )
```

**Parameters:**
- `connection_string` (str): PostgreSQL connection string
- `pool_size` (int): Connection pool size. Default: 5
- `max_overflow` (int): Max overflow connections. Default: 10

**Example:**
```python
from aimemo import PostgresStore, AIMemo

# Basic connection
store = PostgresStore("postgresql://user:pass@localhost/aimemo")

# With connection pooling
store = PostgresStore(
    "postgresql://user:pass@localhost/aimemo",
    pool_size=20,
    max_overflow=10
)

aimemo = AIMemo(store=store)
```

**Methods:**
- Inherits all methods from `MemoryStore`
- Uses PostgreSQL full-text search
- Connection pooling support
- Automatic schema creation

---

## Configuration

### Config

Configuration object for AIMemo.

```python
class Config:
    def __init__(
        self,
        db_path: str = "./aimemo.db",
        max_context: int = 5,
        search_limit: int = 10,
        enable_cache: bool = True,
    )
```

**Parameters:**
- `db_path` (str): Database path for SQLite. Default: "./aimemo.db"
- `max_context` (int): Maximum memories to inject as context. Default: 5
- `search_limit` (int): Default search limit. Default: 10
- `enable_cache` (bool): Enable memory caching. Default: True

**Example:**
```python
from aimemo import Config, AIMemo

config = Config(
    db_path="./my_memory.db",
    max_context=10,
    search_limit=20,
    enable_cache=True
)

aimemo = AIMemo(config=config)
```

#### Class Methods

##### `from_env()`

Create config from environment variables.

```python
@classmethod
def from_env(cls) -> Config
```

**Example:**
```python
# Set environment variables
# export AIMEMO_DB_PATH="./memory.db"
# export AIMEMO_MAX_CONTEXT=10

from aimemo import Config

config = Config.from_env()
```

##### `from_file()`

Load config from JSON file.

```python
@classmethod
def from_file(cls, path: str) -> Config
```

**Parameters:**
- `path` (str): Path to JSON config file

**Example:**
```python
from aimemo import Config

config = Config.from_file("./aimemo.config.json")
```

---

## Provider Classes

### OpenAIProvider

Intercepts OpenAI API calls (automatically initialized).

**Supported libraries:**
- `openai` (official SDK)

### AnthropicProvider

Intercepts Anthropic API calls (automatically initialized).

**Supported libraries:**
- `anthropic` (official SDK)

---

## Data Structures

### Memory Object

Structure of a memory object:

```python
{
    "id": str,              # Unique memory ID
    "content": str,         # Memory content
    "metadata": dict,       # Custom metadata
    "tags": List[str],      # Tags for categorization
    "namespace": str,       # Namespace (isolation)
    "timestamp": str,       # ISO 8601 timestamp
}
```

**Example:**
```python
memory = {
    "id": "a1b2c3d4e5f6",
    "content": "User prefers dark mode",
    "metadata": {
        "user_id": "user_123",
        "source": "settings",
        "priority": "high"
    },
    "tags": ["preference", "ui"],
    "namespace": "user_123",
    "timestamp": "2025-11-16T10:00:00Z"
}
```

---

## Environment Variables

### Configuration

- `AIMEMO_DB_PATH`: Database path (SQLite)
- `AIMEMO_MAX_CONTEXT`: Max context memories
- `AIMEMO_SEARCH_LIMIT`: Default search limit
- `AIMEMO_ENABLE_CACHE`: Enable caching (true/false)

### LLM Provider Keys

- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key

### PostgreSQL

- `AIMEMO_POSTGRES_URL`: PostgreSQL connection string

**Example `.env` file:**
```env
AIMEMO_DB_PATH=./aimemo.db
AIMEMO_MAX_CONTEXT=10
AIMEMO_SEARCH_LIMIT=20

OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

AIMEMO_POSTGRES_URL=postgresql://user:pass@localhost/aimemo
```

---

## Exceptions

### AIMemoError

Base exception for all AIMemo errors.

```python
class AIMemoError(Exception):
    pass
```

### StorageError

Storage-related errors.

```python
class StorageError(AIMemoError):
    pass
```

### ProviderError

LLM provider-related errors.

```python
class ProviderError(AIMemoError):
    pass
```

**Example:**
```python
from aimemo import AIMemo, StorageError

try:
    aimemo = AIMemo(store=PostgresStore("invalid://connection"))
except StorageError as e:
    print(f"Storage error: {e}")
```

---

## Type Hints

### Memory Type

```python
from typing import TypedDict, List, Dict, Any

class Memory(TypedDict):
    id: str
    content: str
    metadata: Dict[str, Any]
    tags: List[str]
    namespace: str
    timestamp: str
```

### Search Result Type

```python
from typing import List

SearchResults = List[Memory]
```

---

## Constants

```python
# Default values
DEFAULT_DB_PATH = "./aimemo.db"
DEFAULT_MAX_CONTEXT = 5
DEFAULT_SEARCH_LIMIT = 10
DEFAULT_NAMESPACE = "default"

# Version
__version__ = "1.0.1"
```

---

## Complete Example

```python
from aimemo import AIMemo, PostgresStore, Config
from openai import OpenAI

# 1. Configure
config = Config(
    max_context=10,
    search_limit=20
)

# 2. Initialize storage
store = PostgresStore("postgresql://user:pass@localhost/aimemo")

# 3. Create AIMemo instance
aimemo = AIMemo(
    store=store,
    config=config,
    namespace="user_123"
)

# 4. Enable interception
aimemo.enable()

# 5. Add manual memory
aimemo.add_memory(
    content="User is building a FastAPI project",
    tags=["project", "fastapi"],
    metadata={"priority": "high"}
)

# 6. Use OpenAI with memory
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "How do I add authentication?"}]
)

# 7. Search memories
results = aimemo.search("fastapi authentication", limit=5)

# 8. Get context
context = aimemo.get_context("authentication")

# 9. Clean up
aimemo.disable()
```

---

## Next Steps

- [Quick Start](quickstart.md) - Get started quickly
- [Configuration](configuration.md) - Configure AIMemo
- [Examples](examples.md) - See code examples

