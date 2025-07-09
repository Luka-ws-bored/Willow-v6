"""
Intent Router for Willow v6

This module provides intelligent routing and chaining of plugins based on
user intent detection and natural language processing.
"""

from enum import Enum
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Enumeration of possible intent types."""
    SINGLE = "single"      # Single plugin execution
    CHAIN = "chain"        # Multiple plugins in sequence
    RAG = "rag"           # RAG pipeline processing
    UNKNOWN = "unknown"    # Unknown intent


class IntentRouter:
    """
    Intelligent router for determining and executing plugin chains.
    
    Analyzes user queries to determine the appropriate processing pipeline
    and can chain multiple plugins together for complex workflows.
    """
    
    def __init__(self, plugins: dict, rag_router, memory_manager):
        """
        Initialize the intent router.
        
        Args:
            plugins: Dictionary of available plugins
            rag_router: RAG router instance
            memory_manager: Memory manager instance
        """
        self.plugins = plugins
        self.rag = rag_router
        self.memory = memory_manager
        
        logger.info(f"Intent router initialized with {len(plugins)} plugins")
    
    def route(self, query: str) -> dict:
        """
        Route a query through the appropriate processing pipeline.
        
        Args:
            query: User input query
            
        Returns:
            Dictionary containing route information and output
        """
        logger.info(f"Routing query: {query[:50]}...")
        
        # Detect intent
        intent = self._detect_intent(query)
        logger.info(f"🔍 Detected intent: {intent}")
        self.memory.add_entry({
            "type": "intent",
            "input": query,
            "intent": intent.name
        })
        
        # Route based on intent
        if intent == IntentType.SINGLE:
            plugin = self._extract_single_plugin(query)
            if plugin:
                output = self.plugins[plugin].run(query)
                route = [plugin]
            else:
                output = "No suitable plugin found for your query."
                route = []
                
        elif intent == IntentType.CHAIN:
            chain = self._extract_plugin_chain(query)
            if chain:
                output = self._execute_chain(chain, query)
                route = chain
            else:
                output = "Could not determine plugin chain from your query."
                route = []
                
        elif intent == IntentType.RAG:
            output = self.rag.route_query(query)
            route = ["rag"]
            
        else:
            # Fallback to RAG for unknown intents
            output = self.rag.route_query(query)
            route = ["rag"]
        
        # Log the routing decision
        result = {"route": route, "output": output, "intent": intent.value}
        
        # Add to memory
        if self.memory:
            self.memory.add_entry({
                "event": "Intent routed",
                "route": route,
                "query": query,
                "output": output[:100] + "..." if len(output) > 100 else output,
                "intent": intent.value
            })
        
        logger.info(f"Query routed to {route} with intent {intent.value}")
        return result
    
    def _detect_intent(self, query: str) -> IntentType:
        """
        Detect the intent of a query.
        
        Args:
            query: User input query
            
        Returns:
            Detected intent type
        """
        lowered = query.lower()

        # Explicit chaining
        if " then " in lowered or " and then " in lowered or " after that " in lowered:
            return IntentType.CHAIN

        # Direct plugin keyword match
        plugin_keywords = []
        for plugin_name in self.plugins.keys():
            plugin_keywords.extend(plugin_name.replace("_", " ").split())
        
        if any(plugin in lowered for plugin in plugin_keywords):
            return IntentType.SINGLE

        # Basic question detection triggers fallback (RAG)
        if lowered.startswith(("what", "who", "when", "where", "why", "how", "explain", "tell me", "define")):
            return IntentType.RAG

        # Unknown — fallback to RAG
        return IntentType.RAG
    
    def _extract_single_plugin(self, query: str) -> Optional[str]:
        """
        Extract the appropriate single plugin for a query.
        
        Args:
            query: User input query
            
        Returns:
            Plugin name if found, None otherwise
        """
        query_lower = query.lower()
        
        # Check each plugin for keyword matches
        for plugin_name in self.plugins.keys():
            plugin_keywords = plugin_name.replace("_", " ").split()
            
            # Check if any plugin keyword is in the query
            if any(keyword in query_lower for keyword in plugin_keywords):
                logger.debug(f"Matched plugin '{plugin_name}' for query")
                return plugin_name
        
        # Fallback: check for specific keywords
        keyword_mapping = {
            "color": "color_mood_mapper",
            "mood": "color_mood_mapper",
            "bug": "bug_buster",
            "error": "bug_buster",
            "code": "bug_buster",
            "sql": "sql_sorcerer",
            "query": "sql_sorcerer",
            "database": "sql_sorcerer",
            "prompt": "prompt_checker",
            "check": "prompt_checker",
            "analyze": "prompt_checker"
        }
        
        for keyword, plugin_name in keyword_mapping.items():
            if keyword in query_lower and plugin_name in self.plugins:
                logger.debug(f"Keyword '{keyword}' matched plugin '{plugin_name}'")
                return plugin_name
        
        return None
    
    def _extract_plugin_chain(self, query: str) -> List[str]:
        """
        Extract a chain of plugins from a query.
        
        Args:
            query: User input query
            
        Returns:
            List of plugin names in execution order
        """
        query_lower = query.lower()
        plugins = []
        
        # Split by chaining keywords
        chain_keywords = ["then", "and then", "after that", "next", "followed by"]
        parts = [query_lower]
        
        for keyword in chain_keywords:
            if keyword in query_lower:
                parts = query_lower.split(keyword)
                break
        
        # Extract plugins from each part
        for part in parts:
            plugin = self._extract_single_plugin(part.strip())
            if plugin and plugin not in plugins:
                plugins.append(plugin)
        
        logger.debug(f"Extracted plugin chain: {plugins}")
        return plugins
    
    def _execute_chain(self, chain: List[str], query: str) -> str:
        """
        Execute a chain of plugins in sequence.
        
        Args:
            chain: List of plugin names to execute
            query: Original input query
            
        Returns:
            Final output after chain execution
        """
        logger.info(f"Executing plugin chain: {' → '.join(chain)}")
        
        result = query
        for i, plugin_name in enumerate(chain):
            try:
                logger.debug(f"Executing plugin {i+1}/{len(chain)}: {plugin_name}")
                result = self.plugins[plugin_name].run(result)
                
                # Add intermediate result to memory
                if self.memory:
                    self.memory.add_entry({
                        "event": "Chain step executed",
                        "step": i + 1,
                        "plugin": plugin_name,
                        "input": query if i == 0 else f"Step {i} output",
                        "output": result[:100] + "..." if len(result) > 100 else result
                    })
                    
            except Exception as e:
                logger.error(f"Error executing plugin {plugin_name}: {e}")
                result = f"Error in plugin {plugin_name}: {str(e)}"
                break
        
        return result
    
    def get_available_plugins(self) -> List[str]:
        """
        Get list of available plugins.
        
        Returns:
            List of plugin names
        """
        return list(self.plugins.keys())
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin information dictionary
        """
        if plugin_name not in self.plugins:
            return None
        
        plugin = self.plugins[plugin_name]
        return {
            "name": plugin_name,
            "module": plugin.__module__,
            "description": getattr(plugin, "__doc__", "No description available")
        } 