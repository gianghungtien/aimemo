# AIMemo

**Memory System for AI Conversations**

AIMemo is a lightweight memory layer that enables AI agents to remember context across conversations. Build AI applications that truly understand and remember your users.

[![PyPI version](https://badge.fury.io/py/aimemo.svg)](https://badge.fury.io/py/aimemo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

- **Automatic Memory**: Intercepts LLM calls and injects relevant context
- **Multiple Backends**: SQLite, PostgreSQL support out of the box
- **Zero Config**: Works with sensible defaults, configure when needed
- **LLM Agnostic**: Supports OpenAI, Anthropic, and more
- **Namespace Isolation**: Perfect for multi-user applications
- **Full-Text Search**: Fast memory retrieval with FTS5/PostgreSQL search

## 📦 Installation

```bash
pip install aimemo
```

For PostgreSQL support:
```bash
pip install aimemo[postgres]
```

## ⚡ Quick Start

```python
from aimemo import AIMemo
from openai import OpenAI

# Initialize AIMemo
aimemo = AIMemo()
aimemo.enable()

# Use OpenAI normally - memory is automatic!
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "I'm building a FastAPI project"}]
)

# Later conversation - context is automatically injected
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "How do I add authentication?"}]
)
# The model remembers your FastAPI project!
```

## 💡 Use Cases

- **Personal AI Assistants**: Remember user preferences and history
- **Customer Support Bots**: Maintain context across support sessions  
- **Research Assistants**: Keep track of research topics and findings
- **Multi-Agent Systems**: Share memory between multiple AI agents
- **Learning Apps**: Track student progress and learning patterns

## 🔧 Configuration

### Database Options

**SQLite** (default):
```python
from aimemo import AIMemo

aimemo = AIMemo()  # Uses aimemo.db by default
```

**PostgreSQL**:
```python
from aimemo import AIMemo, PostgresStore

store = PostgresStore("postgresql://user:pass@localhost/aimemo")
aimemo = AIMemo(store=store)
```

### Environment Variables

```bash
export AIMEMO_DB_PATH="./my_memory.db"
export AIMEMO_MAX_CONTEXT=10
```

### Manual Memory Management

```python
from aimemo import AIMemo

aimemo = AIMemo(namespace="user_123")

# Add memories manually
aimemo.add_memory(
    content="User prefers dark mode",
    tags=["preference", "ui"],
    metadata={"priority": "high"}
)

# Search memories
results = aimemo.search("dark mode", limit=5)

# Get formatted context
context = aimemo.get_context("user interface preferences")
```

### Multi-User Applications

```python
from aimemo import AIMemo

# Each user gets their own namespace
user_memory = AIMemo(namespace=f"user_{user_id}")
user_memory.enable()

# Memories are isolated per user
```

## 📚 Examples

Check out the [examples/](examples/) directory:

- **basic_usage.py** - Simple conversation with memory
- **manual_memory.py** - Manual memory management
- **postgres_example.py** - Using PostgreSQL backend
- **context_manager.py** - Context manager pattern

## 🧪 Testing

```bash
pip install pytest
pytest tests/
```

## 🛠️ Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black aimemo tests examples
```

## 📖 Documentation

Full documentation is available in the [docs/](docs/) directory:

- **[Quick Start Guide](docs/quickstart.md)** - Get started in 5 minutes
- **[Configuration Guide](docs/configuration.md)** - Configure AIMemo for your needs
- **[Architecture Overview](docs/architecture.md)** - How AIMemo works under the hood
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Storage Backends](docs/storage-backends.md)** - Database configuration details
- **[Examples](docs/examples.md)** - More code examples and use cases
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

### Core API

**AIMemo**
- `enable()` - Start intercepting LLM calls
- `disable()` - Stop intercepting
- `add_memory(content, metadata, tags)` - Add memory manually
- `search(query, limit)` - Search memories
- `get_context(query, limit)` - Get formatted context
- `clear(namespace)` - Clear memories

**Storage Backends**
- `SQLiteStore(db_path)` - SQLite storage
- `PostgresStore(connection_string)` - PostgreSQL storage

### Architecture

AIMemo works by intercepting LLM API calls:

1. **Pre-call**: Searches relevant memories based on user query
2. **Injection**: Adds context to the conversation
3. **Post-call**: Stores the conversation for future reference

All automatically, with zero code changes!

## 🤝 Contributing

We love contributions! ❤️ AIMemo is an open-source project and we welcome contributions of all kinds:

- 🐛 **Bug Reports**: Found a bug? [Open an issue](https://github.com/gianghungtien/aimemo/issues)
- 💡 **Feature Requests**: Have an idea? [Share it with us](https://github.com/gianghungtien/aimemo/issues)
- 📝 **Documentation**: Help improve our docs
- 🔧 **Code**: Submit a Pull Request

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run tests**: `pytest tests/`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Setup

```bash
# Clone the repository
git clone https://github.com/gianghungtien/aimemo.git
cd aimemo

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black aimemo tests examples
```

**First time contributing?** Check out issues labeled [`good first issue`](https://github.com/gianghungtien/aimemo/labels/good%20first%20issue) to get started!

### Contributors

Thanks to all the amazing people who have contributed to AIMemo! 🙏

<a href="https://github.com/gianghungtien/aimemo/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=gianghungtien/aimemo" />
</a>

## 📄 License

MIT License - see LICENSE file for details.

## 🙋 Support & Community

Need help? We're here for you!

- 💬 **GitHub Discussions**: Ask questions and share ideas
- 🐛 **GitHub Issues**: [Report bugs or request features](https://github.com/gianghungtien/aimemo/issues)
- 📧 **Email**: gianghungtien@gmail.com

### Show Your Support

If you find AIMemo helpful, please consider:

- ⭐ **Star this repository** to show your support
- 🐦 **Share it** with your friends and colleagues
- 📝 **Write about it** in your blog or social media
- 🤝 **Contribute** to make it even better

---

<div align="center">

**Built with ❤️ by Jason**

[⭐ Star on GitHub](https://github.com/gianghungtien/aimemo) • [📖 Documentation](docs/) • [🐛 Report Bug](https://github.com/gianghungtien/aimemo/issues) • [💡 Request Feature](https://github.com/gianghungtien/aimemo/issues)

</div>