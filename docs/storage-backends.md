# Storage Backends

Deep dive into AIMemo's database storage options.

## Overview

AIMemo supports multiple SQL database backends for storing memories. Choose based on your use case:

| Backend    | Best For                  | Scalability    | Setup        |
|------------|---------------------------|----------------|--------------|
| SQLite     | Development, single user  | 1-10K memories | Zero config  |
| PostgreSQL | Production, multi-user    | 1M+ memories   | Requires DB  |

## SQLite Backend

### Overview

SQLite is the default backend - perfect for development and single-user applications.

**Features:**
- Zero configuration required
- File-based database
- FTS5 full-text search
- Fast for small to medium datasets

### Usage

```python
from aimemo import AIMemo, SQLiteStore

# Default path (./aimemo.db)
aimemo = AIMemo()

# Custom path
store = SQLiteStore("/path/to/memory.db")
aimemo = AIMemo(store=store)

# In-memory database (testing)
store = SQLiteStore(":memory:")
aimemo = AIMemo(store=store)
```

### Configuration

```python
from aimemo import SQLiteStore

store = SQLiteStore(
    db_path="./my_memory.db",
    # SQLite options
)
```

### Schema

```sql
-- Main memories table
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    metadata TEXT,              -- JSON as text
    tags TEXT,                  -- JSON array as text
    namespace TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

-- Full-text search index (FTS5)
CREATE VIRTUAL TABLE memories_fts USING fts5(
    content,
    namespace UNINDEXED,
    content='memories',
    content_rowid='rowid'
);

-- Indexes
CREATE INDEX idx_namespace ON memories(namespace);
CREATE INDEX idx_timestamp ON memories(timestamp);
```

### Full-Text Search

SQLite uses FTS5 (Full-Text Search 5):

```python
# Search implementation
results = aimemo.search("FastAPI authentication")

# Equivalent SQL
"""
SELECT m.id, m.content, m.metadata, m.tags, m.timestamp
FROM memories m
JOIN memories_fts fts ON m.rowid = fts.rowid
WHERE fts.memories_fts MATCH 'FastAPI authentication'
  AND m.namespace = 'default'
ORDER BY fts.rank
LIMIT 5;
"""
```

**FTS5 Features:**
- Word stemming (running → run)
- Phrase matching ("exact phrase")
- Boolean operators (AND, OR, NOT)
- Prefix matching (auth*)

### Performance

**Latency:**
- Write: 1-3ms
- Search: 1-5ms
- Context injection: 2-10ms

**Scalability:**
- Optimal: < 10K memories
- Max: ~100K memories
- Single writer (no concurrent writes)

### Backup

```python
import shutil

# Backup database file
shutil.copy("./aimemo.db", "./backup/aimemo_backup.db")
```

### Best Practices

1. **Use for development**
   ```python
   # Development
   dev_memory = AIMemo()  # Simple!
   ```

2. **Not for production multi-user apps**
   - Single writer limitation
   - File locking issues

3. **Regular backups**
   ```python
   import schedule
   
   def backup_db():
       shutil.copy("./aimemo.db", f"./backup/aimemo_{timestamp}.db")
   
   schedule.every().day.at("02:00").do(backup_db)
   ```

---

## PostgreSQL Backend

### Overview

PostgreSQL is recommended for production applications.

**Features:**
- Concurrent reads/writes
- Full-text search with ts_vector
- JSONB support for metadata
- Array support for tags
- Scalable to millions of memories

### Installation

```bash
pip install aimemo[postgres]
```

This installs `psycopg2` or `psycopg2-binary`.

### Usage

```python
from aimemo import AIMemo, PostgresStore

# Basic connection
store = PostgresStore("postgresql://user:password@localhost:5432/aimemo")
aimemo = AIMemo(store=store)

# With connection pooling
store = PostgresStore(
    "postgresql://user:password@localhost:5432/aimemo",
    pool_size=20,
    max_overflow=10
)
aimemo = AIMemo(store=store)
```

### Connection Strings

**Local PostgreSQL:**
```
postgresql://user:password@localhost:5432/aimemo
```

**Neon (Serverless Postgres):**
```
postgresql://user:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/aimemo
```

**Supabase:**
```
postgresql://postgres.xxxxx:password@aws-0-us-west-1.pooler.supabase.com:5432/postgres
```

**Amazon RDS:**
```
postgresql://user:password@mydb.abc123.us-east-1.rds.amazonaws.com:5432/aimemo
```

### Schema

```sql
-- Main memories table
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,                    -- Native JSON support
    tags TEXT[],                       -- Native array support
    namespace TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    search_vector tsvector             -- Full-text search vector
);

-- Full-text search index
CREATE INDEX memories_search_idx ON memories USING GIN(search_vector);

-- Regular indexes
CREATE INDEX idx_namespace ON memories(namespace);
CREATE INDEX idx_timestamp ON memories(timestamp DESC);
CREATE INDEX idx_tags ON memories USING GIN(tags);
CREATE INDEX idx_metadata ON memories USING GIN(metadata);
```

### Full-Text Search

PostgreSQL uses tsvector and tsquery:

```python
# Search implementation
results = aimemo.search("FastAPI authentication")

# Equivalent SQL
"""
SELECT id, content, metadata, tags, timestamp,
       ts_rank(search_vector, query) AS rank
FROM memories,
     to_tsquery('english', 'FastAPI & authentication') query
WHERE search_vector @@ query
  AND namespace = 'default'
ORDER BY rank DESC
LIMIT 5;
"""
```

**Features:**
- Language-specific stemming
- Stop word removal
- Phrase matching
- Ranking by relevance

### Connection Pooling

```python
from aimemo import PostgresStore

store = PostgresStore(
    "postgresql://user:pass@localhost/aimemo",
    pool_size=20,         # Max connections in pool
    max_overflow=10,      # Max connections beyond pool_size
    pool_timeout=30,      # Timeout waiting for connection
    pool_recycle=3600     # Recycle connections after 1 hour
)
```

### Performance

**Latency:**
- Write: 2-8ms
- Search: 2-10ms
- Context injection: 5-20ms

**Scalability:**
- Optimal: 10K - 1M memories
- Max: 10M+ memories
- Concurrent reads/writes

**Query optimization:**
```sql
-- Analyze table for query planning
ANALYZE memories;

-- Vacuum to reclaim space
VACUUM memories;
```

### Monitoring

```python
# Check connection pool status
store.get_pool_status()
# Returns: {'size': 20, 'overflow': 5, 'checked_in': 18, 'checked_out': 7}

# Get table stats
store.get_table_stats()
# Returns: {'total_memories': 50000, 'namespaces': 100, 'avg_size': 256}
```

### Backup

```bash
# Backup database
pg_dump -U user -d aimemo > aimemo_backup.sql

# Restore database
psql -U user -d aimemo < aimemo_backup.sql

# Backup specific namespace
pg_dump -U user -d aimemo -t memories \
  --where="namespace='user_123'" > user_123_backup.sql
```

### Best Practices

1. **Use connection pooling**
   ```python
   store = PostgresStore(
       connection_string,
       pool_size=20,
       max_overflow=10
   )
   ```

2. **Index optimization**
   ```sql
   -- Check index usage
   SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
   FROM pg_stat_user_indexes
   WHERE schemaname = 'public';
   ```

3. **Regular maintenance**
   ```sql
   -- Weekly vacuum
   VACUUM ANALYZE memories;
   
   -- Reindex if needed
   REINDEX TABLE memories;
   ```

4. **Partitioning for large datasets**
   ```sql
   -- Partition by namespace
   CREATE TABLE memories_user_123 PARTITION OF memories
   FOR VALUES IN ('user_123');
   ```

---

## Comparison

### Feature Comparison

| Feature              | SQLite               | PostgreSQL           |
|----------------------|----------------------|----------------------|
| Setup                | Zero config          | Requires DB          |
| Concurrency          | Single writer        | Multiple readers/writers |
| Full-text search     | FTS5                 | tsvector/tsquery     |
| Metadata storage     | TEXT (JSON)          | JSONB (native)       |
| Tags storage         | TEXT (JSON array)    | TEXT[] (native array) |
| Connection pooling   | N/A                  | ✓                    |
| Scalability          | 10K memories         | 10M+ memories        |
| Backup               | File copy            | pg_dump              |
| Migration            | Easy (file-based)    | pg_dump/restore      |

### Performance Comparison

**10K memories:**
- SQLite: 2-5ms search
- PostgreSQL: 3-8ms search

**100K memories:**
- SQLite: 10-20ms search
- PostgreSQL: 5-15ms search

**1M memories:**
- SQLite: 50-100ms search
- PostgreSQL: 10-30ms search

### Cost Comparison

**SQLite:**
- Free (file-based)
- No hosting costs

**PostgreSQL:**
- Managed hosting: $5-50/month
- Self-hosted: Server costs

**Recommendation:**
- Development: SQLite
- Production < 1000 users: PostgreSQL Basic ($5-10/month)
- Production > 1000 users: PostgreSQL Standard ($20-50/month)

---

## Migration

### SQLite to PostgreSQL

```python
from aimemo import SQLiteStore, PostgresStore

# Source (SQLite)
sqlite_store = SQLiteStore("./aimemo.db")

# Destination (PostgreSQL)
postgres_store = PostgresStore("postgresql://user:pass@localhost/aimemo")

# Migration function
def migrate(source, destination):
    # Get all namespaces
    namespaces = source.get_all_namespaces()
    
    for namespace in namespaces:
        # Get all memories for namespace
        memories = source.get_all_memories(namespace)
        
        # Save to destination
        for memory in memories:
            destination.save(memory)
        
        print(f"Migrated {len(memories)} memories from namespace '{namespace}'")

# Run migration
migrate(sqlite_store, postgres_store)
```

### PostgreSQL to SQLite

```python
def migrate_to_sqlite(postgres_store, sqlite_store):
    namespaces = postgres_store.get_all_namespaces()
    
    for namespace in namespaces:
        memories = postgres_store.get_all_memories(namespace)
        
        for memory in memories:
            sqlite_store.save(memory)
        
        print(f"Migrated {len(memories)} memories to SQLite")

migrate_to_sqlite(postgres_store, sqlite_store)
```

---

## Custom Backend

### Implementing a Custom Store

```python
from aimemo.storage import MemoryStore
from typing import Dict, List, Any, Optional

class CustomStore(MemoryStore):
    """Custom storage backend"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._connect()
    
    def _connect(self):
        """Initialize connection"""
        pass
    
    def save(self, memory: Dict[str, Any]) -> None:
        """Save a memory"""
        # Implement save logic
        pass
    
    def search(
        self,
        query: str,
        namespace: str,
        limit: int,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search memories"""
        # Implement search logic
        pass
    
    def clear(self, namespace: str) -> None:
        """Clear memories for namespace"""
        # Implement clear logic
        pass
    
    def get_all_namespaces(self) -> List[str]:
        """Get all namespaces"""
        # Implement namespace listing
        pass
```

### Usage

```python
from aimemo import AIMemo

custom_store = CustomStore("custom://connection")
aimemo = AIMemo(store=custom_store)
```

---

## Next Steps

- [Configuration](configuration.md) - Configure storage
- [Architecture](architecture.md) - Understand storage architecture
- [API Reference](api-reference.md) - Storage API docs

