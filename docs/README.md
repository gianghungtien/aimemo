# AIMemo Documentation

Welcome to the AIMemo documentation! AIMemo is an open-source memory engine for LLMs, AI agents, and multi-agent systems.

## Table of Contents

- [Quick Start](quickstart.md) - Get started in 5 minutes
- [Configuration](configuration.md) - Configure AIMemo for your needs
- [Architecture](architecture.md) - How AIMemo works under the hood
- [API Reference](api-reference.md) - Complete API documentation
- [Storage Backends](storage-backends.md) - Database configuration
- [Examples](examples.md) - Code examples and use cases
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## What is AIMemo?

AIMemo enables any LLM to remember conversations, learn from interactions, and maintain context across sessions with a single line: `aimemo.enable()`. Memory is stored in standard SQL databases (SQLite, PostgreSQL) that you fully own and control.

### Key Features

- **One-line Integration**: Works with OpenAI, Anthropic, and any LLM framework
- **SQL-Native Storage**: Portable, queryable, and auditable memory
- **Zero Vendor Lock-in**: Export your memory and move anywhere
- **Namespace Isolation**: Perfect for multi-user applications
- **Full-Text Search**: Fast memory retrieval with FTS5/PostgreSQL search

## Quick Example

```python
from aimemo import AIMemo
from openai import OpenAI

# Initialize AIMemo
aimemo = AIMemo()
aimemo.enable()

client = OpenAI()

# First conversation
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "I'm building a FastAPI project"}]
)

# Later conversation - AIMemo automatically provides context
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Help me add authentication"}]
)
# LLM automatically knows about your FastAPI project!
```

## Installation

```bash
pip install aimemo
```

For PostgreSQL support:
```bash
pip install aimemo[postgres]
```

## Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/gianghungtien/aimemo/issues)
- **Email**: gianghungtien@gmail.com

## License

MIT License - see [LICENSE](../LICENSE) file for details.

---

Built with ❤️ by Jason

