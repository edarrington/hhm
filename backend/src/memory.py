"""Household memory system for capturing and retrieving household knowledge.

Uses Redis for fast retrieval and vector search capability.
Extracts family relationships, schedules, preferences, and important dates.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
import json
import logging
import uuid

logger = logging.getLogger(__name__)


class HouseholdMemory:
    """Manages household semantic memory and fact extraction."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.key_prefix = "hhm:memory"

    def add_fact(
        self,
        household_id: str,
        fact_type: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """Add a fact to household memory.
        
        Args:
            household_id: Household identifier
            fact_type: Type of fact (relationship, schedule, preference, date)
            content: Fact content
            metadata: Optional metadata (tags, source, confidence)
            
        Returns:
            Fact ID
        """
        fact_id = f"{household_id}:{fact_type}:{uuid.uuid4().hex[:8]}"
        
        fact = {
            "id": fact_id,
            "type": fact_type,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Store in Redis hash
        key = f"{self.key_prefix}:{household_id}"
        self.redis.hset(key, fact_id, json.dumps(fact))
        
        logger.info(f"Added {fact_type} fact to household {household_id}: {content[:50]}")
        return fact_id

    def get_facts_by_type(
        self,
        household_id: str,
        fact_type: str,
    ) -> list[dict]:
        """Retrieve facts by type for a household.
        
        Args:
            household_id: Household identifier
            fact_type: Type of fact to retrieve
            
        Returns:
            List of facts matching the type
        """
        key = f"{self.key_prefix}:{household_id}"
        all_facts = self.redis.hgetall(key)
        
        facts = []
        for fact_data in all_facts.values():
            fact = json.loads(fact_data)
            if fact["type"] == fact_type:
                facts.append(fact)
        
        return facts

    def get_relationships(self, household_id: str) -> list[dict]:
        """Get family relationships for household.
        
        Returns list like:
        [
            {"person": "Sarah", "relationship": "wife"},
            {"person": "Jake", "relationship": "son"},
        ]
        """
        return self.get_facts_by_type(household_id, "relationship")

    def get_preferences(self, household_id: str) -> list[dict]:
        """Get household member preferences."""
        return self.get_facts_by_type(household_id, "preference")

    def get_important_dates(self, household_id: str) -> list[dict]:
        """Get important dates (birthdays, anniversaries, etc)."""
        return self.get_facts_by_type(household_id, "date")

    def get_schedules(self, household_id: str) -> list[dict]:
        """Get recurring schedule patterns."""
        return self.get_facts_by_type(household_id, "schedule")

    def search_context(
        self,
        household_id: str,
        query: str,
    ) -> list[dict]:
        """Search household memory for relevant context.
        
        Simple keyword search for now. Will be upgraded to semantic
        search with embeddings in Phase 6.
        
        Args:
            household_id: Household identifier
            query: Search query
            
        Returns:
            Matching facts with relevance score
        """
        key = f"{self.key_prefix}:{household_id}"
        all_facts = self.redis.hgetall(key)
        
        results = []
        query_lower = query.lower()
        
        for fact_data in all_facts.values():
            fact = json.loads(fact_data)
            content_lower = fact["content"].lower()
            
            # Simple keyword matching
            if query_lower in content_lower:
                # Score based on exact match
                score = 1.0 if query_lower == content_lower else 0.7
                results.append({**fact, "score": score})
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def clear_household_memory(self, household_id: str) -> int:
        """Clear all memory for a household.
        
        Args:
            household_id: Household identifier
            
        Returns:
            Number of facts deleted
        """
        key = f"{self.key_prefix}:{household_id}"
        deleted = self.redis.delete(key)
        logger.info(f"Cleared household memory for {household_id}")
        return deleted

    def get_memory_stats(self, household_id: str) -> dict:
        """Get statistics about household memory."""
        key = f"{self.key_prefix}:{household_id}"
        
        all_facts = self.redis.hgetall(key)
        facts_by_type = {}
        
        for fact_data in all_facts.values():
            fact = json.loads(fact_data)
            fact_type = fact["type"]
            facts_by_type[fact_type] = facts_by_type.get(fact_type, 0) + 1
        
        return {
            "household_id": household_id,
            "total_facts": len(all_facts),
            "by_type": facts_by_type,
        }


class MemoryExtractor:
    """Extracts household facts from conversations."""

    @staticmethod
    def extract_relationships(text: str) -> list[dict]:
        """Extract family relationships from text.
        
        Examples:
        - "My wife Sarah"
        - "My son Jake"
        - "My brother Mike"
        """
        relationships = []
        
        # Simple pattern matching for common relationships
        patterns = [
            ("wife", "spouse"),
            ("husband", "spouse"),
            ("son", "child"),
            ("daughter", "child"),
            ("mother", "parent"),
            ("father", "parent"),
            ("brother", "sibling"),
            ("sister", "sibling"),
            ("friend", "friend"),
        ]
        
        for pattern, rel_type in patterns:
            if pattern in text.lower():
                # Very simple extraction - would use NER in production
                words = text.split()
                for i, word in enumerate(words):
                    if pattern.lower() in word.lower() and i + 1 < len(words):
                        name = words[i + 1].strip(".,")
                        relationships.append({
                            "person": name,
                            "relationship": rel_type,
                            "pattern": pattern,
                        })
        
        return relationships

    @staticmethod
    def extract_preferences(text: str) -> list[dict]:
        """Extract preferences from text."""
        # Placeholder for preference extraction
        return []

    @staticmethod
    def extract_important_dates(text: str) -> list[dict]:
        """Extract important dates (birthdays, anniversaries)."""
        # Placeholder for date extraction
        return []
