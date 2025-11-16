# Troubleshooting Guide

Common issues and solutions when using AIMemo.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Memory Not Working](#memory-not-working)
3. [No Context Being Injected](#no-context-being-injected)
4. [Database Errors](#database-errors)
5. [Performance Issues](#performance-issues)
6. [LLM Provider Issues](#llm-provider-issues)
7. [Namespace Issues](#namespace-issues)
8. [Import Errors](#import-errors)

---

## Installation Issues

### Problem: `pip install aimemo` fails

**Symptoms:**
```bash
ERROR: Could not find a version that satisfies the requirement aimemo
```

**Solutions:**

1. **Update pip:**
   ```bash
   pip install --upgrade pip
   ```

2. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

3. **Install from source:**
   ```bash
   git clone https://github.com/gianghungtien/aimemo.git
   cd aimemo
   pip install -e .
   ```

### Problem: PostgreSQL dependencies fail to install

**Symptoms:**
```bash
ERROR: Failed building wheel for psycopg2
```

**Solutions:**

1. **Install system dependencies (Ubuntu/Debian):**
   ```bash
   sudo apt-get install python3-dev libpq-dev
   pip install aimemo[postgres]
   ```

2. **Install system dependencies (macOS):**
   ```bash
   brew install postgresql
   pip install aimemo[postgres]
   ```

3. **Use binary package:**
   ```bash
   pip install psycopg2-binary
   ```

---

## Memory Not Working

### Problem: LLM doesn't remember previous context

**Symptoms:**
- Previous conversations not recalled
- Context not injected

**Checklist:**

1. **Did you call `enable()`?**
   ```python
   aimemo = AIMemo()
   aimemo.enable()  # ← Don't forget this!
   ```

2. **Are you using the same namespace?**
   ```python
   # Good - same namespace
   aimemo1 = AIMemo(namespace="user_123")
   aimemo1.enable()
   
   # Bad - different namespace
   aimemo2 = AIMemo(namespace="user_456")  # Different memories!
   ```

3. **Check if memories are saved:**
   ```python
   results = aimemo.search("", limit=10)
   print(f"Total memories: {len(results)}")
   
   if len(results) == 0:
       print("No memories found!")
   ```

4. **Verify interception is working:**
   ```python
   # Add a test memory
   aimemo.add_memory("Test memory content")
   
   # Search for it
   results = aimemo.search("test")
   print(f"Found {len(results)} memories")
   ```

---

## No Context Being Injected

### Problem: Memories exist but aren't used

**Symptoms:**
- `search()` returns results
- But LLM doesn't use context

**Solutions:**

1. **Check max_context setting:**
   ```python
   from aimemo import Config
   
   config = Config(max_context=10)  # Increase if needed
   aimemo = AIMemo(config=config)
   ```

2. **Verify search relevance:**
   ```python
   # Test search with your query
   results = aimemo.search("your query here", limit=5)
   
   for i, mem in enumerate(results):
       print(f"{i+1}. {mem['content']}")
   
   # If no results, memories aren't relevant
   ```

3. **Add more specific memories:**
   ```python
   # Good - specific
   aimemo.add_memory(
       "User is building a FastAPI project with PostgreSQL",
       tags=["project", "fastapi", "postgresql"]
   )
   
   # Bad - too generic
   aimemo.add_memory("User likes programming")
   ```

---

## Database Errors

### Problem: SQLite database locked

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**

1. **Close other connections:**
   ```python
   # Don't create multiple AIMemo instances with same DB
   
   # Bad
   memo1 = AIMemo()
   memo2 = AIMemo()  # Can cause locking
   
   # Good
   memo = AIMemo()
   memo.enable()
   ```

2. **Use PostgreSQL for concurrent access:**
   ```python
   from aimemo import PostgresStore
   
   store = PostgresStore("postgresql://...")
   aimemo = AIMemo(store=store)
   ```

3. **Increase timeout:**
   ```python
   import sqlite3
   
   # In storage.py, increase timeout
   conn = sqlite3.connect("aimemo.db", timeout=30)
   ```

### Problem: PostgreSQL connection fails

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
```

**Solutions:**

1. **Check connection string:**
   ```python
   # Correct format
   connection_string = "postgresql://user:password@host:port/database"
   
   # Common mistakes:
   # - Missing port (should be :5432)
   # - Wrong password (check for special characters)
   # - Wrong database name
   ```

2. **Test connection:**
   ```python
   import psycopg2
   
   try:
       conn = psycopg2.connect("postgresql://...")
       print("Connection successful!")
   except Exception as e:
       print(f"Connection failed: {e}")
   ```

3. **Check PostgreSQL is running:**
   ```bash
   # Local PostgreSQL
   sudo systemctl status postgresql
   
   # Docker
   docker ps | grep postgres
   ```

4. **Check firewall/network:**
   ```bash
   # Test connection
   psql -h localhost -U user -d aimemo
   ```

### Problem: Database schema errors

**Symptoms:**
```
sqlite3.OperationalError: no such table: memories
```

**Solutions:**

1. **Delete and recreate database:**
   ```python
   import os
   
   # Remove old database
   if os.path.exists("aimemo.db"):
       os.remove("aimemo.db")
   
   # Reinitialize
   aimemo = AIMemo()
   aimemo.enable()
   ```

2. **Manual schema creation:**
   ```python
   from aimemo.storage import SQLiteStore
   
   store = SQLiteStore("aimemo.db")
   store.initialize_schema()  # Force schema creation
   ```

---

## Performance Issues

### Problem: Slow search queries

**Symptoms:**
- `search()` takes > 1 second
- Context injection is slow

**Solutions:**

1. **Check database size:**
   ```python
   import os
   
   db_size = os.path.getsize("aimemo.db") / (1024 * 1024)
   print(f"Database size: {db_size:.2f} MB")
   
   # If > 100MB, consider cleanup
   ```

2. **Reduce search limit:**
   ```python
   # Faster
   results = aimemo.search("query", limit=5)
   
   # Slower
   results = aimemo.search("query", limit=100)
   ```

3. **Clear old memories:**
   ```python
   from datetime import datetime, timedelta
   
   # Remove memories older than 30 days
   cutoff_date = datetime.now() - timedelta(days=30)
   aimemo.store.delete_old_memories(cutoff_date)
   ```

4. **Use PostgreSQL for large datasets:**
   ```python
   # SQLite: Good for < 10K memories
   # PostgreSQL: Good for 10K+ memories
   
   from aimemo import PostgresStore
   
   store = PostgresStore("postgresql://...")
   aimemo = AIMemo(store=store)
   ```

### Problem: High memory usage

**Symptoms:**
- Python process uses too much RAM
- Out of memory errors

**Solutions:**

1. **Disable caching:**
   ```python
   from aimemo import Config
   
   config = Config(enable_cache=False)
   aimemo = AIMemo(config=config)
   ```

2. **Use pagination for large queries:**
   ```python
   # Bad - loads all results
   all_results = aimemo.search("", limit=10000)
   
   # Good - paginate
   page_size = 100
   for offset in range(0, 10000, page_size):
       results = aimemo.store.search_paginated(
           query="",
           limit=page_size,
           offset=offset
       )
       process_results(results)
   ```

---

## LLM Provider Issues

### Problem: OpenAI API errors

**Symptoms:**
```
openai.error.AuthenticationError: Invalid API key
```

**Solutions:**

1. **Check API key:**
   ```python
   import os
   
   api_key = os.getenv("OPENAI_API_KEY")
   if not api_key:
       print("OPENAI_API_KEY not set!")
   else:
       print(f"API key: {api_key[:10]}...")
   ```

2. **Set API key correctly:**
   ```python
   import openai
   
   openai.api_key = "sk-..."
   
   # Or use environment variable
   # export OPENAI_API_KEY="sk-..."
   ```

3. **Test OpenAI connection:**
   ```python
   from openai import OpenAI
   
   client = OpenAI()
   
   try:
       response = client.chat.completions.create(
           model="gpt-4o-mini",
           messages=[{"role": "user", "content": "Test"}]
       )
       print("OpenAI connection works!")
   except Exception as e:
       print(f"OpenAI error: {e}")
   ```

### Problem: Anthropic API not intercepted

**Symptoms:**
- Anthropic works but memory doesn't

**Solutions:**

1. **Verify Anthropic support:**
   ```python
   # AIMemo currently supports OpenAI primarily
   # Check version for Anthropic support
   
   from aimemo import __version__
   print(f"AIMemo version: {__version__}")
   ```

2. **Use OpenAI compatibility mode:**
   ```python
   # If Anthropic has OpenAI-compatible API
   from openai import OpenAI
   
   client = OpenAI(
       base_url="https://api.anthropic.com/v1",
       api_key="sk-ant-..."
   )
   ```

---

## Namespace Issues

### Problem: Can't find memories from another namespace

**Symptoms:**
- Memories saved in one namespace
- Can't access from another

**Solutions:**

1. **Check namespace:**
   ```python
   # Memories are isolated by namespace
   
   memo1 = AIMemo(namespace="user_1")
   memo1.add_memory("User 1 memory")
   
   memo2 = AIMemo(namespace="user_2")
   results = memo2.search("memory")  # Won't find user_1's memory
   
   # This is by design for isolation
   ```

2. **Search across namespaces (if needed):**
   ```python
   # Not recommended, but possible
   
   def search_all_namespaces(query: str):
       namespaces = aimemo.store.get_all_namespaces()
       all_results = []
       
       for ns in namespaces:
           memo = AIMemo(namespace=ns)
           results = memo.search(query)
           all_results.extend(results)
       
       return all_results
   ```

### Problem: Namespace conflicts

**Symptoms:**
- Different users seeing each other's memories

**Solutions:**

1. **Use unique namespaces:**
   ```python
   # Good - unique per user
   aimemo = AIMemo(namespace=f"user_{user_id}")
   
   # Bad - same namespace for all users
   aimemo = AIMemo(namespace="default")  # Don't do this!
   ```

2. **Verify namespace isolation:**
   ```python
   # Test isolation
   memo1 = AIMemo(namespace="test_1")
   memo1.add_memory("Secret 1")
   
   memo2 = AIMemo(namespace="test_2")
   results = memo2.search("Secret")
   
   assert len(results) == 0, "Namespace leak detected!"
   ```

---

## Import Errors

### Problem: Cannot import AIMemo

**Symptoms:**
```python
ImportError: cannot import name 'AIMemo' from 'aimemo'
```

**Solutions:**

1. **Check installation:**
   ```bash
   pip list | grep aimemo
   
   # If not found
   pip install aimemo
   ```

2. **Check import statement:**
   ```python
   # Correct
   from aimemo import AIMemo
   
   # Incorrect
   from AIMemo import AIMemo  # Wrong capitalization
   import aimemo.AIMemo  # Wrong path
   ```

3. **Check for naming conflicts:**
   ```bash
   # Don't name your file aimemo.py
   # It will conflict with the package
   
   # Bad
   # aimemo.py  ← Your file
   
   # Good
   # my_app.py
   ```

---

## Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("aimemo")
logger.setLevel(logging.DEBUG)

# Now use AIMemo
from aimemo import AIMemo

aimemo = AIMemo()
aimemo.enable()

# You'll see detailed logs
```

---

## Getting Help

If you're still stuck:

1. **Check GitHub Issues:**
   - [https://github.com/gianghungtien/aimemo/issues](https://github.com/gianghungtien/aimemo/issues)

2. **Create a minimal reproduction:**
   ```python
   from aimemo import AIMemo
   from openai import OpenAI
   
   # Minimal code that shows the issue
   aimemo = AIMemo()
   aimemo.enable()
   
   # ... your issue here ...
   ```

3. **Include version info:**
   ```python
   from aimemo import __version__
   print(f"AIMemo version: {__version__}")
   
   import sys
   print(f"Python version: {sys.version}")
   
   import openai
   print(f"OpenAI version: {openai.__version__}")
   ```

4. **Contact:**
   - **Email**: gianghungtien@gmail.com
   - **GitHub Issues**: Create a new issue with details

---

## Next Steps

- [Quick Start](quickstart.md) - Get started with AIMemo
- [Configuration](configuration.md) - Configuration options
- [API Reference](api-reference.md) - Complete API documentation

