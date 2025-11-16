# Configuration Guide

Learn how to configure AIMemo for your specific needs.

## Configuration Methods

AIMemo can be configured in three ways (in order of precedence):

1. **Direct initialization** - Pass parameters to `AIMemo()`
2. **Environment variables** - Set `AIMEMO_*` variables
3. **Config file** - Use a `aimemo.config.json` file

## Basic Configuration

### Initialization Parameters

```python
from aimemo import AIMemo, SQLiteStore, Config

aimemo = AIMemo(
    store=SQLiteStore("./my_memory.db"),  # Storage backend
    config=Config(max_context=10),         # Configuration object
    namespace="default",                   # Memory namespace
    auto_enable=False                      # Auto-enable on init
)
```

### Config Object

```python
from aimemo import Config

config = Config(
    db_path="./aimemo.db",      # Database path (SQLite)
    max_context=5,              # Max memories to inject
    search_limit=10,            # Default search limit
    enable_cache=True,          # Enable memory caching
)

aimemo = AIMemo(config=config)
```

## Environment Variables

Set environment variables for global configuration:

```bash
# Database
export AIMEMO_DB_PATH="./my_memory.db"

# Memory Settings
export AIMEMO_MAX_CONTEXT=10
export AIMEMO_SEARCH_LIMIT=20

# LLM Provider Keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Using .env Files

Create a `.env` file in your project root:

```env
# AIMemo Configuration
AIMEMO_DB_PATH=./aimemo.db
AIMEMO_MAX_CONTEXT=10
AIMEMO_SEARCH_LIMIT=20

# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Load with python-dotenv:

```python
from dotenv import load_dotenv
from aimemo import AIMemo

load_dotenv()  # Load .env file

aimemo = AIMemo()  # Uses environment variables
aimemo.enable()
```

## Storage Backend Configuration

### SQLite (Default)

```python
from aimemo import AIMemo, SQLiteStore

# Using default path
aimemo = AIMemo()  # Uses ./aimemo.db

# Custom path
store = SQLiteStore("/path/to/memory.db")
aimemo = AIMemo(store=store)
```

### PostgreSQL

```python
from aimemo import AIMemo, PostgresStore

# Connection string
store = PostgresStore("postgresql://user:password@localhost:5432/aimemo")
aimemo = AIMemo(store=store)

# Or using environment variable
# export AIMEMO_POSTGRES_URL="postgresql://..."
store = PostgresStore.from_env()
aimemo = AIMemo(store=store)
```

**Connection String Formats:**

| Database | Format |
|----------|--------|
| PostgreSQL | `postgresql://user:pass@host:port/database` |
| Neon | `postgresql://user:pass@ep-*.neon.tech/aimemo` |
| Supabase | `postgresql://postgres:pass@db.*.supabase.co/postgres` |

## Namespace Configuration

Namespaces isolate memories for different users or contexts:

```python
from aimemo import AIMemo

# Single namespace
aimemo = AIMemo(namespace="production")

# Dynamic namespaces per user
def get_user_memory(user_id: str):
    return AIMemo(namespace=f"user_{user_id}")

user_memory = get_user_memory("alice")
admin_memory = get_user_memory("admin")
```

## Advanced Configuration

### Memory Limits

Control how much context is injected:

```python
from aimemo import AIMemo, Config

config = Config(
    max_context=5,        # Max memories in context
    search_limit=20,      # Max search results
    min_relevance=0.5,    # Minimum relevance score
)

aimemo = AIMemo(config=config)
```

### Custom Metadata

Add custom metadata to memories:

```python
aimemo = AIMemo(namespace="app")

aimemo.add_memory(
    content="User completed tutorial",
    metadata={
        "user_id": "user_123",
        "timestamp": "2025-01-01T10:00:00Z",
        "source": "onboarding",
        "importance": 8,
    },
    tags=["milestone", "onboarding"]
)
```

### Search Configuration

Customize search behavior:

```python
# Search with filters
results = aimemo.search(
    query="python tutorial",
    limit=10,
    tags=["learning", "python"]
)

# Get context with custom limit
context = aimemo.get_context(
    query="FastAPI authentication",
    limit=3
)
```

## Production Configuration

### Example Production Setup

```python
import os
from aimemo import AIMemo, PostgresStore, Config

# Production configuration
config = Config(
    max_context=10,
    search_limit=50,
    enable_cache=True,
)

# PostgreSQL for production
store = PostgresStore(
    os.getenv("DATABASE_URL"),
    pool_size=20,
    max_overflow=10
)

# Initialize with namespace per tenant
def get_tenant_memory(tenant_id: str):
    return AIMemo(
        store=store,
        config=config,
        namespace=f"tenant_{tenant_id}"
    )
```

### Environment Variables for Production

```bash
# Database
DATABASE_URL=postgresql://user:pass@db.example.com:5432/aimemo

# Memory Configuration
AIMEMO_MAX_CONTEXT=10
AIMEMO_SEARCH_LIMIT=50
AIMEMO_ENABLE_CACHE=true

# LLM Provider
OPENAI_API_KEY=sk-...

# Application
APP_ENV=production
LOG_LEVEL=info
```

## Configuration File

Create `aimemo.config.json`:

```json
{
  "database": {
    "path": "./aimemo.db",
    "type": "sqlite"
  },
  "memory": {
    "max_context": 10,
    "search_limit": 20,
    "enable_cache": true
  },
  "defaults": {
    "namespace": "default"
  }
}
```

Load configuration:

```python
from aimemo import AIMemo, Config

config = Config.from_file("aimemo.config.json")
aimemo = AIMemo(config=config)
```

## Provider-Specific Configuration

### OpenAI

```python
import openai
from aimemo import AIMemo

# Set OpenAI API key
openai.api_key = "sk-..."

aimemo = AIMemo()
aimemo.enable()

# OpenAI calls are now intercepted
```

### Anthropic

```python
import anthropic
from aimemo import AIMemo

client = anthropic.Anthropic(api_key="sk-ant-...")

aimemo = AIMemo()
aimemo.enable()

# Anthropic calls are now intercepted
```

## Best Practices

### 1. Use Namespaces for Multi-Tenant Apps

```python
# Isolate memories per user/tenant
aimemo = AIMemo(namespace=f"tenant_{tenant_id}")
```

### 2. Use PostgreSQL in Production

```python
# SQLite for development
dev_memory = AIMemo()  # Uses SQLite

# PostgreSQL for production
prod_memory = AIMemo(
    store=PostgresStore(os.getenv("DATABASE_URL"))
)
```

### 3. Configure Context Limits

```python
# Balance between relevance and token usage
config = Config(max_context=5)  # 5-10 is usually optimal
```

### 4. Use Environment Variables

```python
# Don't hardcode credentials
store = PostgresStore(os.getenv("DATABASE_URL"))
```

## Next Steps

- [Architecture](architecture.md) - Understand how configuration affects behavior
- [Storage Backends](storage-backends.md) - Deep dive into database options
- [API Reference](api-reference.md) - Complete API documentation

