"""
Entity extraction system for AIMemo.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Entity:
    """Extracted entity from text."""
    name: str
    type: str
    value: Any
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class EntityExtractor(ABC):
    """Abstract base class for entity extractors."""
    
    @abstractmethod
    def extract(self, text: str) -> List[Entity]:
        """
        Extract entities from text.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted entities
        """
        pass


class RegexEntityExtractor(EntityExtractor):
    """Basic entity extractor using regex patterns."""
    
    def __init__(self):
        self.patterns = {
            "email": re.compile(r'[\w\.-]+@[\w\.-]+\.\w+'),
            "date": re.compile(r'\d{4}-\d{2}-\d{2}'),
            # Simple name extraction (capitalized words, very basic)
            # In a real system, use NLP libraries like spaCy
            "name": re.compile(r'(?<!^)(?<!\.\s)[A-Z][a-z]+ [A-Z][a-z]+'),
        }
    
    def extract(self, text: str) -> List[Entity]:
        entities = []
        
        for type_name, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                entities.append(Entity(
                    name=match.group(),
                    type=type_name,
                    value=match.group(),
                    confidence=0.8,
                    metadata={"span": match.span()}
                ))
                
        return entities
