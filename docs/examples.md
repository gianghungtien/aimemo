# Examples

Comprehensive code examples for using AIMemo in various scenarios.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Multi-User Applications](#multi-user-applications)
3. [Manual Memory Management](#manual-memory-management)
4. [Context Manager Pattern](#context-manager-pattern)
5. [PostgreSQL Backend](#postgresql-backend)
6. [FastAPI Integration](#fastapi-integration)
7. [Personal Assistant](#personal-assistant)
8. [Customer Support Bot](#customer-support-bot)
9. [Research Assistant](#research-assistant)
10. [Multi-Agent System](#multi-agent-system)

---

## Basic Usage

Simple conversation with automatic memory:

```python
from aimemo import AIMemo
from openai import OpenAI

# Initialize
aimemo = AIMemo()
aimemo.enable()

client = OpenAI()

# First conversation
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "I'm building a FastAPI project"}]
)
print(response.choices[0].message.content)

# Later conversation - context is automatically injected
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "How do I add authentication?"}]
)
print(response.choices[0].message.content)
# The model remembers your FastAPI project!
```

---

## Multi-User Applications

Isolate memories per user:

```python
from aimemo import AIMemo
from openai import OpenAI
from typing import Dict

class UserMemoryManager:
    """Manage memories for multiple users"""
    
    def __init__(self):
        self.memories: Dict[str, AIMemo] = {}
        self.client = OpenAI()
    
    def get_user_memory(self, user_id: str) -> AIMemo:
        """Get or create memory for user"""
        if user_id not in self.memories:
            memory = AIMemo(namespace=f"user_{user_id}")
            memory.enable()
            self.memories[user_id] = memory
        
        return self.memories[user_id]
    
    def chat(self, user_id: str, message: str) -> str:
        """Chat with memory context"""
        memory = self.get_user_memory(user_id)
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}]
        )
        
        return response.choices[0].message.content

# Usage
manager = UserMemoryManager()

# User Alice
alice_response = manager.chat("alice", "I like Python programming")

# User Bob (completely isolated)
bob_response = manager.chat("bob", "I prefer JavaScript")

# Later conversations remember user context
alice_response = manager.chat("alice", "What language do I like?")
# Response: "You mentioned you like Python programming"
```

---

## Manual Memory Management

Directly manage memories:

```python
from aimemo import AIMemo

aimemo = AIMemo(namespace="manual_example")

# Add memories manually
aimemo.add_memory(
    content="User prefers dark mode",
    tags=["preference", "ui"],
    metadata={
        "priority": "high",
        "source": "settings",
        "user_action": "toggle_dark_mode"
    }
)

aimemo.add_memory(
    content="User completed Python tutorial",
    tags=["milestone", "learning"],
    metadata={
        "course": "python-basics",
        "completion_date": "2025-11-16"
    }
)

# Search memories
print("Searching for 'python':")
results = aimemo.search("python", limit=5)
for mem in results:
    print(f"- {mem['content']}")
    print(f"  Tags: {mem['tags']}")
    print(f"  Metadata: {mem['metadata']}")

# Search with tag filter
print("\nSearching for preferences:")
results = aimemo.search("preferences", tags=["preference"])
for mem in results:
    print(f"- {mem['content']}")

# Get formatted context
context = aimemo.get_context("user preferences and learning")
print(f"\nContext:\n{context}")

# Clear memories
aimemo.clear()
print("\nMemories cleared")
```

---

## Context Manager Pattern

Use AIMemo with context manager:

```python
from aimemo import AIMemo
from openai import OpenAI

client = OpenAI()

def process_conversation(session_id: str, messages: list):
    """Process conversation with session memory"""
    
    with AIMemo(namespace=f"session_{session_id}") as aimemo:
        # Memory automatically enabled
        
        for msg in messages:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": msg}]
            )
            
            print(f"User: {msg}")
            print(f"Assistant: {response.choices[0].message.content}\n")
    
    # Memory automatically disabled after context

# Usage
messages = [
    "I'm learning machine learning",
    "What are neural networks?",
    "How do I implement one in Python?"
]

process_conversation("session_123", messages)
```

---

## PostgreSQL Backend

Using PostgreSQL for production:

```python
from aimemo import AIMemo, PostgresStore
from openai import OpenAI
import os

# Initialize PostgreSQL store
store = PostgresStore(
    os.getenv("DATABASE_URL"),
    pool_size=20,
    max_overflow=10
)

# Create AIMemo instance
aimemo = AIMemo(
    store=store,
    namespace="production"
)
aimemo.enable()

# Use normally
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)

# Memories are stored in PostgreSQL
```

---

## FastAPI Integration

Build a multi-user API with memory:

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from aimemo import AIMemo, PostgresStore
from openai import OpenAI
import os

app = FastAPI()

# Initialize store
store = PostgresStore(os.getenv("DATABASE_URL"))
client = OpenAI()

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

def get_user_memory(user_id: str) -> AIMemo:
    """Get memory for user"""
    memory = AIMemo(
        store=store,
        namespace=f"user_{user_id}"
    )
    memory.enable()
    return memory

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with memory"""
    
    # Get user-specific memory
    memory = get_user_memory(request.user_id)
    
    try:
        # Create chat completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": request.message}]
        )
        
        return ChatResponse(
            response=response.choices[0].message.content
        )
    
    finally:
        memory.disable()

@app.get("/memories/{user_id}")
async def get_memories(user_id: str, query: str = ""):
    """Get user memories"""
    
    memory = AIMemo(
        store=store,
        namespace=f"user_{user_id}"
    )
    
    if query:
        results = memory.search(query, limit=10)
    else:
        results = memory.search("", limit=10)
    
    return {"memories": results}

@app.delete("/memories/{user_id}")
async def clear_memories(user_id: str):
    """Clear user memories"""
    
    memory = AIMemo(
        store=store,
        namespace=f"user_{user_id}"
    )
    memory.clear()
    
    return {"message": f"Memories cleared for user {user_id}"}

# Run: uvicorn main:app --reload
```

---

## Personal Assistant

Build a personal AI assistant with memory:

```python
from aimemo import AIMemo
from openai import OpenAI
from datetime import datetime

class PersonalAssistant:
    """Personal AI assistant with memory"""
    
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.memory = AIMemo(namespace=f"assistant_{user_name}")
        self.memory.enable()
        self.client = OpenAI()
    
    def chat(self, message: str) -> str:
        """Chat with the assistant"""
        
        # Add timestamp to context
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        system_message = {
            "role": "system",
            "content": f"You are a helpful personal assistant for {self.user_name}. Current time: {current_time}"
        }
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                system_message,
                {"role": "user", "content": message}
            ]
        )
        
        return response.choices[0].message.content
    
    def add_reminder(self, reminder: str):
        """Add a reminder"""
        self.memory.add_memory(
            content=f"Reminder: {reminder}",
            tags=["reminder"],
            metadata={"created_at": datetime.now().isoformat()}
        )
    
    def get_reminders(self):
        """Get all reminders"""
        return self.memory.search("reminder", tags=["reminder"], limit=20)

# Usage
assistant = PersonalAssistant("Alice")

# Chat
print(assistant.chat("I have a meeting tomorrow at 2 PM"))
print(assistant.chat("What's on my schedule?"))

# Add reminder
assistant.add_reminder("Buy groceries")
assistant.add_reminder("Call mom")

# Get reminders
reminders = assistant.get_reminders()
for reminder in reminders:
    print(f"- {reminder['content']}")
```

---

## Customer Support Bot

Customer support with conversation history:

```python
from aimemo import AIMemo, PostgresStore
from openai import OpenAI
from typing import List, Dict

class CustomerSupportBot:
    """Customer support bot with memory"""
    
    def __init__(self, database_url: str):
        self.store = PostgresStore(database_url)
        self.client = OpenAI()
    
    def get_customer_memory(self, customer_id: str) -> AIMemo:
        """Get memory for customer"""
        memory = AIMemo(
            store=self.store,
            namespace=f"customer_{customer_id}"
        )
        memory.enable()
        return memory
    
    def handle_support_query(
        self,
        customer_id: str,
        query: str
    ) -> str:
        """Handle customer support query"""
        
        memory = self.get_customer_memory(customer_id)
        
        # Get customer context
        context = memory.get_context("customer information", limit=5)
        
        system_message = {
            "role": "system",
            "content": f"""You are a customer support assistant.
            
Customer Context:
{context}

Provide helpful and empathetic support."""
        }
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                system_message,
                {"role": "user", "content": query}
            ]
        )
        
        return response.choices[0].message.content
    
    def add_customer_note(
        self,
        customer_id: str,
        note: str,
        category: str
    ):
        """Add a note about customer"""
        memory = self.get_customer_memory(customer_id)
        
        memory.add_memory(
            content=note,
            tags=["note", category],
            metadata={
                "category": category,
                "timestamp": datetime.now().isoformat()
            }
        )

# Usage
bot = CustomerSupportBot("postgresql://...")

# Customer conversation
response = bot.handle_support_query(
    "customer_123",
    "I'm having trouble with my order"
)
print(response)

# Add note
bot.add_customer_note(
    "customer_123",
    "Customer prefers email communication",
    "preference"
)

# Future conversation remembers context
response = bot.handle_support_query(
    "customer_123",
    "Can you contact me about the issue?"
)
# Bot knows customer prefers email
```

---

## Research Assistant

Research assistant that remembers findings:

```python
from aimemo import AIMemo
from openai import OpenAI

class ResearchAssistant:
    """Research assistant with memory"""
    
    def __init__(self, research_topic: str):
        self.topic = research_topic
        self.memory = AIMemo(namespace=f"research_{research_topic}")
        self.memory.enable()
        self.client = OpenAI()
    
    def research_query(self, query: str) -> str:
        """Process research query"""
        
        # Get related findings
        context = self.memory.get_context(query, limit=5)
        
        system_message = {
            "role": "system",
            "content": f"""You are a research assistant helping with: {self.topic}

Previous findings:
{context}

Provide thorough, well-researched answers."""
        }
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                system_message,
                {"role": "user", "content": query}
            ]
        )
        
        return response.choices[0].message.content
    
    def add_finding(self, finding: str, source: str = None):
        """Add a research finding"""
        metadata = {}
        if source:
            metadata["source"] = source
        
        self.memory.add_memory(
            content=finding,
            tags=["finding", self.topic],
            metadata=metadata
        )
    
    def summarize_findings(self) -> str:
        """Summarize all findings"""
        findings = self.memory.search(self.topic, limit=50)
        
        findings_text = "\n".join([f"- {f['content']}" for f in findings])
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"Summarize these research findings:\n\n{findings_text}"
            }]
        )
        
        return response.choices[0].message.content

# Usage
assistant = ResearchAssistant("machine_learning")

# Research queries
print(assistant.research_query("What are transformers?"))
print(assistant.research_query("How do attention mechanisms work?"))

# Add findings
assistant.add_finding(
    "Transformers use self-attention to process sequences",
    source="Attention Is All You Need paper"
)

# Summarize
summary = assistant.summarize_findings()
print(f"\nResearch Summary:\n{summary}")
```

---

## Multi-Agent System

Multiple agents sharing memory:

```python
from aimemo import AIMemo, PostgresStore
from openai import OpenAI
from typing import List

class Agent:
    """Base agent class"""
    
    def __init__(self, name: str, role: str, shared_memory: AIMemo):
        self.name = name
        self.role = role
        self.memory = shared_memory
        self.client = OpenAI()
    
    def process(self, task: str) -> str:
        """Process a task"""
        
        context = self.memory.get_context(task, limit=5)
        
        system_message = {
            "role": "system",
            "content": f"""You are {self.name}, a {self.role}.
            
Previous team context:
{context}

Complete your task and share findings."""
        }
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                system_message,
                {"role": "user", "content": task}
            ]
        )
        
        result = response.choices[0].message.content
        
        # Share finding with team
        self.memory.add_memory(
            content=f"{self.name} ({self.role}): {result}",
            tags=["team", self.role],
            metadata={"agent": self.name}
        )
        
        return result

class MultiAgentSystem:
    """System with multiple collaborative agents"""
    
    def __init__(self, project_name: str):
        # Shared memory for all agents
        self.shared_memory = AIMemo(namespace=f"project_{project_name}")
        self.shared_memory.enable()
        self.agents: List[Agent] = []
    
    def add_agent(self, name: str, role: str):
        """Add an agent to the system"""
        agent = Agent(name, role, self.shared_memory)
        self.agents.append(agent)
    
    def collaborate(self, task: str) -> Dict[str, str]:
        """All agents collaborate on a task"""
        results = {}
        
        for agent in self.agents:
            result = agent.process(task)
            results[agent.name] = result
            print(f"{agent.name}: {result}\n")
        
        return results

# Usage
system = MultiAgentSystem("web_app")

# Add agents
system.add_agent("Alice", "Backend Developer")
system.add_agent("Bob", "Frontend Developer")
system.add_agent("Charlie", "DevOps Engineer")

# Collaborative task
print("Task: Build authentication system\n")
results = system.collaborate("Design and implement user authentication")

# Each agent sees what others have done via shared memory
```

---

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Configuration](configuration.md) - Configuration options
- [Architecture](architecture.md) - How AIMemo works

