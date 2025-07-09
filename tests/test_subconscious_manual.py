import pytest
from willow.memory import MemoryManager
from willow.subconscious import Subconscious

@pytest.fixture
def memory(tmp_path):
    file = tmp_path / "mem.json"
    mm = MemoryManager(str(file))
    return mm

def test_dream_manual(memory, capsys):
    # seed memory
    memory.add_entry({"event": "test", "data": "entry1"})
    memory.add_entry({"event": "test", "data": "entry2"})
    sub = Subconscious(memory, dream_interval=999999)
    summary = sub.dream()
    assert "Dream summary:" in summary
    assert "entry1" in summary
    assert "entry2" in summary

def test_dream_with_empty_memory(memory):
    """Test dream command with empty memory"""
    sub = Subconscious(memory, dream_interval=999999)
    summary = sub.dream()
    assert "Dream summary:" in summary
    # Should handle empty memory gracefully
    assert len(summary) > 0

def test_dream_adds_to_memory(memory):
    """Test that dream command adds entry to memory"""
    initial_count = len(memory.get_recent(100))
    sub = Subconscious(memory, dream_interval=999999)
    sub.dream()
    final_count = len(memory.get_recent(100))
    assert final_count == initial_count + 1
    
    # Check that the new entry is a dream_manual event
    recent = memory.get_recent(1)
    assert recent[0].get("event") == "dream_manual" 