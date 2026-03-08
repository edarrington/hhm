"""Tests for household memory system."""

import pytest
from src.memory import HouseholdMemory, MemoryExtractor
import json


class MockRedis:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self.data = {}
    
    def hset(self, key, field, value):
        if key not in self.data:
            self.data[key] = {}
        self.data[key][field] = value
        return 1
    
    def hgetall(self, key):
        return self.data.get(key, {})
    
    def delete(self, key):
        if key in self.data:
            count = len(self.data[key])
            del self.data[key]
            return count
        return 0
    
    def clear(self):
        """Clear all data."""
        self.data.clear()


@pytest.fixture
def memory_client():
    """Create a memory client for testing with mock Redis."""
    redis_client = MockRedis()
    return HouseholdMemory(redis_client)


def test_add_fact(memory_client):
    """Test adding a fact to household memory."""
    household_id = "test-household"
    fact_id = memory_client.add_fact(
        household_id,
        "relationship",
        "Sarah is the wife",
        metadata={"confidence": 0.95},
    )
    
    assert fact_id
    assert "test-household" in fact_id
    assert "relationship" in fact_id


def test_get_facts_by_type(memory_client):
    """Test retrieving facts by type."""
    household_id = "test-household"
    
    # Add some facts
    fact_id1 = memory_client.add_fact(household_id, "relationship", "Sarah is the wife")
    fact_id2 = memory_client.add_fact(household_id, "relationship", "Jake is the son")
    fact_id3 = memory_client.add_fact(household_id, "preference", "Likes morning coffee")
    
    # Retrieve relationships
    relationships = memory_client.get_facts_by_type(household_id, "relationship")
    assert len(relationships) == 2
    assert all(f["type"] == "relationship" for f in relationships)


def test_get_relationships(memory_client):
    """Test retrieving family relationships."""
    household_id = "test-household"
    
    memory_client.add_fact(household_id, "relationship", "Sarah is the wife")
    memory_client.add_fact(household_id, "relationship", "Jake is the son")
    
    relationships = memory_client.get_relationships(household_id)
    assert len(relationships) == 2


def test_search_context(memory_client):
    """Test searching household memory."""
    household_id = "test-household"
    
    memory_client.add_fact(household_id, "relationship", "Sarah is the wife")
    memory_client.add_fact(household_id, "schedule", "Jake has soccer on Saturdays")
    
    # Search for Sarah
    results = memory_client.search_context(household_id, "Sarah")
    assert len(results) > 0
    assert "Sarah" in results[0]["content"]


def test_extract_relationships():
    """Test relationship extraction from text."""
    text = "My wife Sarah and my son Jake"
    relationships = MemoryExtractor.extract_relationships(text)
    
    # Should extract at least one relationship
    assert len(relationships) > 0


def test_get_memory_stats(memory_client):
    """Test getting memory statistics."""
    household_id = "test-household"
    
    memory_client.add_fact(household_id, "relationship", "Sarah is the wife")
    memory_client.add_fact(household_id, "relationship", "Jake is the son")
    memory_client.add_fact(household_id, "preference", "Likes coffee")
    
    stats = memory_client.get_memory_stats(household_id)
    
    assert stats["total_facts"] == 3
    assert stats["by_type"]["relationship"] == 2
    assert stats["by_type"]["preference"] == 1


def test_clear_household_memory(memory_client):
    """Test clearing household memory."""
    household_id = "test-household"
    
    memory_client.add_fact(household_id, "relationship", "Sarah is the wife")
    memory_client.add_fact(household_id, "preference", "Likes coffee")
    
    # Should have 2 facts
    stats = memory_client.get_memory_stats(household_id)
    assert stats["total_facts"] == 2
    
    # Clear memory
    deleted = memory_client.clear_household_memory(household_id)
    assert deleted > 0
    
    # Should have 0 facts now
    stats = memory_client.get_memory_stats(household_id)
    assert stats["total_facts"] == 0
