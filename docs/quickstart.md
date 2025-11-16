# Quick Start Guide

Get up and running with AIMemo in 5 minutes!

## Installation

### Basic Installation

```bash
pip install aimemo
```

### With PostgreSQL Support

```bash
pip install aimemo[postgres]
```

### Development Installation

```bash
git clone https://github.com/gianghungtien/aimemo.git
cd aimemo
pip install -e ".[dev]"
```

## Basic Usage

### 1. Simple Memory Setup

The simplest way to add memory to your LLM application:

```python
from aimemo import AIMemo
from openai import OpenAI

# Initialize AIMemo with defaults (SQLite)
aimemo = AIMemo()
aimemo.enable()

# Use OpenAI normally - memory is automatic!
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "I'm working on a Python project"}]
)

print(response.choices[0].message.content)
```

### 2. Using PostgreSQL

For production applications:

```python
from aimemo import AIMemo, PostgresStore

# Connect to PostgreSQL
store = PostgresStore("postgresql://user:pass@localhost/aimemo")
aimemo = AIMemo(store=store)
aimemo.enable()

# Your LLM calls now have persistent memory
```

### 3. Multi-User Applications

Isolate memories per user with namespaces:

```python
from aimemo import AIMemo

def get_user_memory(user_id: str) -> AIMemo:
    """Get isolated memory for each user"""
    return AIMemo(namespace=f"user_{user_id}")

# User 1's conversation
user1_memory = get_user_memory("user_123")
user1_memory.enable()

# User 2's conversation (completely isolated)
user2_memory = get_user_memory("user_456")
user2_memory.enable()
```

### 4. Manual Memory Management

Add and search memories directly:

```python
from aimemo import AIMemo

aimemo = AIMemo(namespace="my_app")

# Add a memory
aimemo.add_memory(
    content="User prefers dark mode",
    tags=["preference", "ui"],
    metadata={"priority": "high"}
)

# Search memories
results = aimemo.search("dark mode", limit=5)

for memory in results:
    print(f"- {memory['content']}")

# Get formatted context
context = aimemo.get_context("user interface preferences")
print(context)
```

### 5. Context Manager Pattern

Use AIMemo as a context manager for automatic cleanup:

```python
from aimemo import AIMemo
from openai import OpenAI

client = OpenAI()

with AIMemo(namespace="session_123") as aimemo:
    # Memory is enabled within this block
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello!"}]
    )
# Memory is automatically disabled after the block
```

## Environment Variables

Configure AIMemo using environment variables:

```bash
export AIMEMO_DB_PATH="./my_memory.db"
export AIMEMO_MAX_CONTEXT=10
export OPENAI_API_KEY="sk-..."
```

Or create a `.env` file:

```env
AIMEMO_DB_PATH=./my_memory.db
AIMEMO_MAX_CONTEXT=10
OPENAI_API_KEY=sk-...
```

## Next Steps

- [Configuration Guide](configuration.md) - Learn all configuration options
- [Architecture Overview](architecture.md) - Understand how AIMemo works
- [API Reference](api-reference.md) - Explore the complete API
- [Examples](examples.md) - See more code examples

## Common Issues

### Memory Not Working?

Make sure you've called `aimemo.enable()`:

```python
aimemo = AIMemo()
aimemo.enable()  # Don't forget this!
```

### No Context Being Injected?

Check that you have previous memories:

```python
# Add a test memory
aimemo.add_memory("This is a test memory")

# Verify it's saved
results = aimemo.search("test")
print(f"Found {len(results)} memories")
```

For more troubleshooting, see [Troubleshooting Guide](troubleshooting.md).

