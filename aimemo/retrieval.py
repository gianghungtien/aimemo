"""
Context retrieval system for AIMemo.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import math

from .storage import MemoryStore


class ContextRetriever:
    """
    Handles retrieval of relevant context from memory.
    """
    
    def __init__(self, store: MemoryStore):
        self.store = store
    
    def get_relevant_context(
        self,
        query: str,
        namespace: str,
        limit: int = 5,
        category: Optional[str] = None,
        recency_weight: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context with scoring.
        
        Args:
            query: Search query
            namespace: Memory namespace
            limit: Number of results
            category: Filter by category
            recency_weight: Weight for recency score (0.0 to 1.0)
            
        Returns:
            List of ranked memories
        """
        # Get more candidates than needed to re-rank
        candidates = self.store.search(
            query=query,
            namespace=namespace,
            limit=limit * 3,
            category=category
        )
        
        if not candidates:
            return []
        
        # Score candidates
        scored_candidates = []
        now = datetime.utcnow()
        
        for mem in candidates:
            # Base score from search rank (implicit in order)
            # We assign a normalized score based on position
            rank_score = 1.0 - (candidates.index(mem) / len(candidates))
            
            # Recency score
            try:
                timestamp = datetime.fromisoformat(mem["timestamp"])
                age = (now - timestamp).total_seconds()
                # Decay function: 1 / (1 + log(age in hours + 1))
                age_hours = age / 3600
                recency_score = 1.0 / (1.0 + math.log1p(age_hours))
            except (ValueError, TypeError):
                recency_score = 0.5
            
            # Combined score
            final_score = (rank_score * (1 - recency_weight)) + (recency_score * recency_weight)
            
            scored_candidates.append((final_score, mem))
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        # Return top N
        return [item[1] for item in scored_candidates[:limit]]
    
    def format_context(self, memories: List[Dict[str, Any]]) -> str:
        """
        Format memories into a context string.
        
        Args:
            memories: List of memory dicts
            
        Returns:
            Formatted string
        """
        if not memories:
            return ""
        
        parts = ["Previous context:"]
        for mem in memories:
            # Include category if available
            prefix = f"[{mem['category'].upper()}] " if mem.get("category") else ""
            parts.append(f"- {prefix}{mem['content']}")
            
        return "\n".join(parts)
