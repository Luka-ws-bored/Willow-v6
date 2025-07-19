"""
Tests for the Intent Router system in Willow v6.

Tests the intelligent routing and chaining of plugins based on user intent.
"""

import pytest
from unittest.mock import Mock, MagicMock
from willow.intent_router import IntentRouter, IntentType


class DummyPlugin:
    """Dummy plugin for testing."""
    def __init__(self, name="dummy"):
        self.name = name
    
    def run(self, text):
        return f"{self.name.upper()}: {text.upper()}"


@pytest.fixture
def mock_plugins():
    """Create mock plugins for testing."""
    return {
        "dummy": DummyPlugin("dummy"),
        "color_mood_mapper": DummyPlugin("color_mood_mapper"),
        "bug_buster": DummyPlugin("bug_buster"),
        "sql_sorcerer": DummyPlugin("sql_sorcerer"),
        "prompt_checker": DummyPlugin("prompt_checker")
    }


@pytest.fixture
def mock_rag_router():
    """Create mock RAG router."""
    rag = Mock()
    rag.route_query.return_value = "RAG response"
    return rag


@pytest.fixture
def mock_memory():
    """Create mock memory manager."""
    memory = Mock()
    memory.add_entry = Mock()
    return memory


@pytest.fixture
def intent_router(mock_plugins, mock_rag_router, mock_memory):
    """Create IntentRouter instance for testing."""
    return IntentRouter(mock_plugins, mock_rag_router, mock_memory)


class TestIntentType:
    """Test the IntentType enum."""
    
    def test_intent_types(self):
        """Test that all intent types are defined."""
        assert IntentType.SINGLE == "single"
        assert IntentType.CHAIN == "chain"
        assert IntentType.RAG == "rag"
        assert IntentType.UNKNOWN == "unknown"


class TestIntentRouter:
    """Test the IntentRouter class."""
    
    def test_initialization(self, intent_router, mock_plugins, mock_rag_router, mock_memory):
        """Test IntentRouter initialization."""
        assert intent_router.plugins == mock_plugins
        assert intent_router.rag == mock_rag_router
        assert intent_router.memory == mock_memory
    
    def test_detect_intent_single(self, intent_router):
        """Test single plugin intent detection."""
        intent = intent_router._detect_intent("dummy test")
        assert intent == IntentType.SINGLE
    
    def test_detect_intent_chain(self, intent_router):
        """Test chain intent detection."""
        intent = intent_router._detect_intent("dummy test then color happy")
        assert intent == IntentType.CHAIN
    
    def test_detect_intent_rag(self, intent_router):
        """Test RAG intent detection."""
        intent = intent_router._detect_intent("how does this work")
        assert intent == IntentType.RAG
    
    def test_detect_intent_unknown(self, intent_router):
        """Test unknown intent detection."""
        intent = intent_router._detect_intent("xyz123")
        assert intent == IntentType.UNKNOWN
    
    def test_extract_single_plugin(self, intent_router):
        """Test single plugin extraction."""
        plugin = intent_router._extract_single_plugin("dummy test")
        assert plugin == "dummy"
    
    def test_extract_single_plugin_keyword_mapping(self, intent_router):
        """Test plugin extraction via keyword mapping."""
        plugin = intent_router._extract_single_plugin("check this prompt")
        assert plugin == "prompt_checker"
    
    def test_extract_single_plugin_not_found(self, intent_router):
        """Test plugin extraction when no match found."""
        plugin = intent_router._extract_single_plugin("xyz123")
        assert plugin is None
    
    def test_extract_plugin_chain(self, intent_router):
        """Test plugin chain extraction."""
        chain = intent_router._extract_plugin_chain("dummy test then color happy")
        assert chain == ["dummy", "color_mood_mapper"]
    
    def test_extract_plugin_chain_no_matches(self, intent_router):
        """Test plugin chain extraction with no matches."""
        chain = intent_router._extract_plugin_chain("xyz then abc")
        assert chain == []
    
    def test_execute_chain(self, intent_router):
        """Test plugin chain execution."""
        chain = ["dummy", "color_mood_mapper"]
        result = intent_router._execute_chain(chain, "test input")
        assert "COLOR_MOOD_MAPPER" in result
    
    def test_execute_chain_with_error(self, intent_router):
        """Test plugin chain execution with error."""
        # Create a plugin that raises an exception
        error_plugin = Mock()
        error_plugin.run.side_effect = Exception("Test error")
        intent_router.plugins["error_plugin"] = error_plugin
        
        chain = ["dummy", "error_plugin"]
        result = intent_router._execute_chain(chain, "test input")
        assert "Error in plugin error_plugin" in result
    
    def test_route_single_plugin(self, intent_router):
        """Test routing to single plugin."""
        result = intent_router.route("dummy test")
        assert result["route"] == ["dummy"]
        assert "DUMMY" in result["output"]
        assert result["intent"] == "single"
    
    def test_route_plugin_chain(self, intent_router):
        """Test routing to plugin chain."""
        result = intent_router.route("dummy test then color happy")
        assert result["route"] == ["dummy", "color_mood_mapper"]
        assert "COLOR_MOOD_MAPPER" in result["output"]
        assert result["intent"] == "chain"
    
    def test_route_rag(self, intent_router):
        """Test routing to RAG."""
        result = intent_router.route("how does this work")
        assert result["route"] == ["rag"]
        assert result["output"] == "RAG response"
        assert result["intent"] == "rag"
    
    def test_route_unknown(self, intent_router):
        """Test routing unknown intent."""
        result = intent_router.route("xyz123")
        assert result["route"] == []
        assert "Sorry" in result["output"]
        assert result["intent"] == "unknown"
    
    def test_route_no_suitable_plugin(self, intent_router):
        """Test routing when no suitable plugin is found."""
        result = intent_router.route("test with no plugin keywords")
        assert result["route"] == []
        assert "No suitable plugin found" in result["output"]
    
    def test_route_memory_integration(self, intent_router, mock_memory):
        """Test that routing adds entries to memory."""
        intent_router.route("dummy test")
        mock_memory.add_entry.assert_called()
        
        # Check the memory entry structure
        call_args = mock_memory.add_entry.call_args[0][0]
        assert "event" in call_args
        assert "route" in call_args
        assert "query" in call_args
        assert "output" in call_args
        assert "intent" in call_args
    
    def test_get_available_plugins(self, intent_router, mock_plugins):
        """Test getting available plugins."""
        plugins = intent_router.get_available_plugins()
        expected_plugins = list(mock_plugins.keys())
        assert set(plugins) == set(expected_plugins)
    
    def test_get_plugin_info(self, intent_router):
        """Test getting plugin information."""
        info = intent_router.get_plugin_info("dummy")
        assert info["name"] == "dummy"
        assert "module" in info
        assert "description" in info
    
    def test_get_plugin_info_not_found(self, intent_router):
        """Test getting info for non-existent plugin."""
        info = intent_router.get_plugin_info("nonexistent")
        assert info is None


class TestIntentRouterIntegration:
    """Integration tests for Intent Router."""
    
    def test_complex_chain(self, intent_router):
        """Test complex plugin chaining."""
        result = intent_router.route("bug_buster check code then sql_sorcerer convert query")
        assert len(result["route"]) == 2
        assert "bug_buster" in result["route"]
        assert "sql_sorcerer" in result["route"]
        assert result["intent"] == "chain"
    
    def test_mixed_intents(self, intent_router):
        """Test different intent types in sequence."""
        # Single plugin
        result1 = intent_router.route("color happy")
        assert result1["intent"] == "single"
        
        # Chain
        result2 = intent_router.route("dummy test then color happy")
        assert result2["intent"] == "chain"
        
        # RAG
        result3 = intent_router.route("how does this work")
        assert result3["intent"] == "rag"
    
    def test_error_handling(self, intent_router):
        """Test error handling in routing."""
        # Test with invalid plugin
        result = intent_router.route("invalid_plugin test")
        assert "No suitable plugin found" in result["output"]
        
        # Test with empty input
        result = intent_router.route("")
        assert "Sorry" in result["output"]


class TestIntentRouterEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_plugins(self, mock_rag_router, mock_memory):
        """Test IntentRouter with no plugins."""
        router = IntentRouter({}, mock_rag_router, mock_memory)
        result = router.route("test")
        assert result["route"] == []
    
    def test_none_memory(self, mock_plugins, mock_rag_router):
        """Test IntentRouter with no memory manager."""
        router = IntentRouter(mock_plugins, mock_rag_router, None)
        result = router.route("dummy test")
        assert result["route"] == ["dummy"]
    
    def test_plugin_without_run_method(self, mock_rag_router, mock_memory):
        """Test handling of plugins without run method."""
        invalid_plugin = Mock()
        del invalid_plugin.run
        
        plugins = {"invalid": invalid_plugin}
        router = IntentRouter(plugins, mock_rag_router, mock_memory)
        
        # Should handle gracefully
        result = router.route("invalid test")
        assert "No suitable plugin found" in result["output"]
    
    def test_long_output_truncation(self, intent_router, mock_memory):
        """Test that long outputs are truncated in memory."""
        # Create a plugin that returns very long output
        long_plugin = Mock()
        long_plugin.run.return_value = "x" * 200
        
        intent_router.plugins["long_plugin"] = long_plugin
        intent_router.route("long_plugin test")
        
        # Check that memory entry has truncated output
        call_args = mock_memory.add_entry.call_args[0][0]
        output = call_args["output"]
        assert len(output) <= 103  # 100 chars + "..."
        assert output.endswith("...") 