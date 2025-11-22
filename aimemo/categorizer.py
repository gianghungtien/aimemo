"""
Memory categorization system for AIMemo.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional


class MemoryCategory(str, Enum):
    """Categories of memories."""
    FACT = "fact"
    PREFERENCE = "preference"
    SKILL = "skill"
    RULE = "rule"
    CONTEXT = "context"
    UNKNOWN = "unknown"


class MemoryCategorizer(ABC):
    """Abstract base class for memory categorizers."""
    
    @abstractmethod
    def categorize(self, text: str) -> MemoryCategory:
        """
        Categorize a memory based on its content.
        
        Args:
            text: Memory content
            
        Returns:
            MemoryCategory
        """
        pass


class KeywordCategorizer(MemoryCategorizer):
    """Simple categorizer based on keywords."""
    
    def __init__(self):
        self.keywords = {
            MemoryCategory.PREFERENCE: ["like", "love", "hate", "prefer", "enjoy", "want"],
            MemoryCategory.SKILL: ["can", "know", "able to", "expert", "proficient"],
            MemoryCategory.RULE: ["always", "never", "must", "should", "rule"],
            MemoryCategory.FACT: ["is a", "located", "born", "defined as", "is in"],
        }
    
    def categorize(self, text: str) -> MemoryCategory:
        text_lower = text.lower()
        
        # Check for keywords
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                if f" {keyword} " in f" {text_lower} ":
                    return category
        
        # Default to context if no specific keywords found
        return MemoryCategory.CONTEXT
