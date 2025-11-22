"""
Configuration management for AIMemo
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import json
try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class Config:
    """
    Configuration for AIMemo.
    
    Attributes:
        db_path: Path to SQLite database
        db_connection: PostgreSQL connection string (if using Postgres)
        max_context_memories: Maximum memories to inject as context
        enable_openai: Enable OpenAI interceptor
        enable_anthropic: Enable Anthropic interceptor
        enable_extraction: Enable entity extraction
        enable_categorization: Enable memory categorization
        extraction_confidence_threshold: Minimum confidence for extracted entities
        working_memory_limit: Maximum items in working memory
    """
    
    db_path: str = field(default_factory=lambda: os.getenv("AIMEMO_DB_PATH", "aimemo.db"))
    db_connection: Optional[str] = field(default_factory=lambda: os.getenv("AIMEMO_DB_CONNECTION"))
    max_context_memories: int = field(default_factory=lambda: int(os.getenv("AIMEMO_MAX_CONTEXT", "5")))
    enable_openai: bool = field(default_factory=lambda: os.getenv("AIMEMO_ENABLE_OPENAI", "true").lower() == "true")
    enable_anthropic: bool = field(default_factory=lambda: os.getenv("AIMEMO_ENABLE_ANTHROPIC", "true").lower() == "true")
    enable_extraction: bool = field(default_factory=lambda: os.getenv("AIMEMO_ENABLE_EXTRACTION", "true").lower() == "true")
    enable_categorization: bool = field(default_factory=lambda: os.getenv("AIMEMO_ENABLE_CATEGORIZATION", "true").lower() == "true")
    extraction_confidence_threshold: float = field(default_factory=lambda: float(os.getenv("AIMEMO_EXTRACTION_THRESHOLD", "0.8")))
    working_memory_limit: int = field(default_factory=lambda: int(os.getenv("AIMEMO_WORKING_MEMORY_LIMIT", "5")))
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls()
    
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def load_from_file(cls, path: str) -> "Config":
        """Load config from JSON or YAML file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
            
        with open(path, "r") as f:
            if path.endswith(".json"):
                data = json.load(f)
            elif path.endswith((".yaml", ".yml")):
                if yaml is None:
                    raise ImportError("PyYAML is required for YAML config support")
                data = yaml.safe_load(f)
            else:
                raise ValueError("Unsupported config file format. Use .json or .yaml")
                
        return cls.from_dict(data)

