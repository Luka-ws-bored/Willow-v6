"""
RAG Router for Willow v6

This module provides the routing logic for directing queries through different
processing pipelines: plugins, RAG, and fallback systems.

Implements LangChain-powered RAG pipeline with document retrieval and generation.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# LangChain imports
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
# Import the updated embeddings class
from langchain_openai import OpenAIEmbeddings
# Import OpenAI client for OpenRouter
from openai import OpenAI


class RouteType(Enum):
    """Enumeration of possible routing destinations."""
    PLUGIN = "plugin"
    RAG = "rag"
    FALLBACK = "fallback"
    ERROR = "error"


class IntentLevel(Enum):
    """Enumeration of query intent complexity levels."""
    SIMPLE = "simple"      # Direct plugin match
    COMPLEX = "complex"    # Requires RAG
    UNKNOWN = "unknown"    # Fallback needed


class RAGRouter:
    """
    Router for directing queries through appropriate processing pipelines.
    
    This class implements the routing logic described in docs/api-routing.md.
    It determines whether a query should be handled by:
    1. Direct plugin processing
    2. RAG pipeline
    3. Fallback LLM call
    4. Error response
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the RAG router.
        
        Args:
            config: Configuration dictionary for routing behavior
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # RAG components
        self.vector_store = None
        self.qa_chain = None
        self.embeddings = None
        self.llm = None
        
        # Initialize RAG pipeline
        self._initialize_rag_pipeline()
        
        self.logger.info("RAG Router initialized with LangChain pipeline")
    
    def _initialize_rag_pipeline(self) -> None:
        """Initialize the RAG pipeline components."""
        try:
            # Get RAG configuration
            rag_config = self.config.get('rag', {})
            docs_path = rag_config.get('docs_path', 'docs/data/')
            model_name = rag_config.get('model', 'gpt-3.5-turbo')
            top_k = rag_config.get('k', 3)
            
            # Initialize embeddings with OpenRouter key if provided
            api_key = self.config.get("openrouter_api_key") or None
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            
            # Load and process documents
            self._load_documents(docs_path)
            
            # Initialize OpenAI client with OpenRouter configuration
            if api_key:
                self.openai_client = OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            else:
                self.openai_client = None
            
            # Store model name for fallback
            self.model_name = model_name
            
            # Initialize QA chain
            self._initialize_chain(top_k)
            
            self.logger.info(f"RAG pipeline initialized with model: {model_name}, top_k: {top_k}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG pipeline: {e}")
            # Fallback to direct LLM if needed
            api_key = self.config.get("openrouter_api_key") or None
            if api_key:
                self.openai_client = OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            else:
                self.openai_client = None
            self.model_name = model_name
            self.vector_store = None
            self.qa_chain = None
    
    def _load_documents(self, docs_path: str) -> None:
        """
        Load documents from the specified path.
        
        Args:
            docs_path: Path to documents directory
        """
        try:
            if not os.path.exists(docs_path):
                self.logger.warning(f"Documents path {docs_path} does not exist. Creating empty vector store.")
                # Create empty vector store for now
                self.vector_store = FAISS.from_texts(
                    ["No documents available"], 
                    self.embeddings
                )
                return
            
            # Load documents
            loader = DirectoryLoader(
                docs_path,
                glob="**/*.txt",
                loader_cls=TextLoader
            )
            documents = loader.load()
            
            if not documents:
                self.logger.warning(f"No documents found in {docs_path}")
                self.vector_store = FAISS.from_texts(
                    ["No documents available"], 
                    self.embeddings
                )
                return
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            
            self.logger.info(f"Loaded {len(documents)} documents, created {len(chunks)} chunks")
            
        except Exception as e:
            self.logger.error(f"Error loading documents: {e}")
            # Create fallback vector store
            self.vector_store = FAISS.from_texts(
                ["Error loading documents"], 
                self.embeddings
            )
    
    def _initialize_chain(self, top_k: int = 3) -> None:
        """
        Initialize the retrieval-based QA chain.
        
        Args:
            top_k: Number of documents to retrieve
        """
        try:
            # Create prompt template
            prompt_template = """Use the following pieces of context to answer the question at the end. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            
            Context: {context}
            
            Question: {question}
            
            Answer:"""
            
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create retrieval QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(search_kwargs={"k": top_k}),
                chain_type_kwargs={"prompt": prompt}
            )
            
            self.logger.info(f"QA chain initialized with top_k={top_k}")
            
        except Exception as e:
            self.logger.error(f"Error initializing QA chain: {e}")
            self.qa_chain = None
    
    def route_query(self, query: str) -> str:
        """
        Route a query through the appropriate processing pipeline.
        
        Args:
            query: The user's input query
            
        Returns:
            Processed response from the appropriate pipeline
        """
        self.logger.info(f"Routing query: {query[:50]}...")
        
        # Handle empty or invalid queries
        if not query or not query.strip():
            return self._handle_empty_query()
        
        try:
            # Step 1: Intent detection
            intent = self._detect_intent(query)
            
            # Step 2: Route decision
            route_type = self._decide_route(query, intent)
            
            # Step 3: Process through selected pipeline
            response = self._process_route(query, route_type, intent)
            
            self.logger.info(f"Query routed to {route_type.value}, response generated")
            return response
            
        except Exception as e:
            self.logger.error(f"Error routing query: {e}")
            return self._handle_error(query, e)
    
    def _detect_intent(self, query: str) -> IntentLevel:
        """
        Detect the intent and complexity level of a query.
        
        Args:
            query: The user's input query
            
        Returns:
            IntentLevel indicating query complexity
        """
        # Simple keyword-based intent detection
        query_lower = query.lower()
        
        # Check for simple plugin keywords
        plugin_keywords = ['color', 'mood', 'bug', 'error', 'sql', 'prompt']
        if any(keyword in query_lower for keyword in plugin_keywords):
            return IntentLevel.SIMPLE
        
        # Check for complex queries that need RAG
        complex_indicators = ['how', 'what', 'why', 'when', 'where', 'explain', 'describe', 'tell me about']
        if any(indicator in query_lower for indicator in complex_indicators):
            return IntentLevel.COMPLEX
        
        return IntentLevel.UNKNOWN
    
    def _decide_route(self, query: str, intent: IntentLevel) -> RouteType:
        """
        Decide which processing route to take based on intent.
        
        Args:
            query: The user's input query
            intent: Detected intent level
            
        Returns:
            RouteType indicating processing pipeline
        """
        if intent == IntentLevel.SIMPLE:
            return RouteType.PLUGIN
        elif intent == IntentLevel.COMPLEX and self.qa_chain is not None:
            return RouteType.RAG
        else:
            return RouteType.FALLBACK
    
    def _process_route(self, query: str, route_type: RouteType, intent: IntentLevel) -> str:
        """
        Process the query through the selected route.
        
        Args:
            query: The user's input query
            route_type: Selected processing route
            intent: Detected intent level
            
        Returns:
            Processed response
        """
        if route_type == RouteType.PLUGIN:
            return self._process_plugin_route(query, intent)
        elif route_type == RouteType.RAG:
            return self._process_rag_route(query, intent)
        elif route_type == RouteType.FALLBACK:
            return self._process_fallback_route(query, intent)
        else:
            return self._process_error_route(query, intent)
    
    def _process_plugin_route(self, query: str, intent: IntentLevel) -> str:
        """
        Process query through plugin system.
        
        Args:
            query: The user's input query
            intent: Detected intent level
            
        Returns:
            Plugin response
        """
        # TODO: Implement actual plugin routing
        # For now, return a placeholder response
        return f"[PLUGIN ROUTE] Query: {query} (plugin system not fully implemented yet)"
    
    def _process_rag_route(self, query: str, intent: IntentLevel) -> str:
        """
        Process query through RAG pipeline using LangChain.
        
        Args:
            query: The user's input query
            intent: Detected intent level
            
        Returns:
            RAG-generated response
        """
        try:
            if self.qa_chain is None:
                self.logger.warning("RAG chain not available, falling back to direct LLM")
                return self._process_fallback_route(query, intent)
            
            # Get response from RAG chain
            response = self.qa_chain.run(query)
            
            self.logger.info("RAG response generated successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Error in RAG processing: {e}")
            return self._process_fallback_route(query, intent)
    
    def _process_fallback_route(self, query: str, intent: IntentLevel) -> str:
        """
        Process query through fallback LLM system.
        
        Args:
            query: The user's input query
            intent: Detected intent level
            
        Returns:
            Fallback LLM response
        """
        try:
            if self.openai_client is None:
                return "[FALLBACK] LLM not available. Please check your API configuration."
            
            # Use OpenAI client with OpenRouter
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": query}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            self.logger.info("Fallback LLM response generated")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in fallback processing: {e}")
            return f"[FALLBACK ERROR] Unable to process query: {str(e)}"
    
    def _process_error_route(self, query: str, intent: IntentLevel) -> str:
        """
        Handle error cases with structured error response.
        
        Args:
            query: The user's input query
            intent: Detected intent level
            
        Returns:
            Error response
        """
        return f"[ERROR ROUTE] Unable to process query: {query}"
    
    def _handle_empty_query(self) -> str:
        """
        Handle empty or invalid queries.
        
        Returns:
            Response for empty queries
        """
        return "Please provide a valid query. I'm here to help!"
    
    def _handle_error(self, query: str, error: Exception) -> str:
        """
        Handle routing errors gracefully.
        
        Args:
            query: The original query that caused the error
            error: The exception that occurred
            
        Returns:
            Error response for the user
        """
        self.logger.error(f"Routing error for query '{query}': {error}")
        
        return f"Sorry, I encountered an error while processing your query. Please try again."
    
    def get_route_stats(self) -> Dict[str, Any]:
        """
        Get statistics about routing decisions and performance.
        
        Returns:
            Dictionary containing routing statistics
        """
        # TODO: Implement actual statistics tracking
        return {
            "total_queries": 0,
            "route_distribution": {},
            "average_response_time": 0.0,
            "success_rate": 0.0,
            "rag_available": self.qa_chain is not None,
            "vector_store_size": len(self.vector_store.index_to_docstore_id) if self.vector_store else 0
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Update router configuration at runtime.
        
        Args:
            new_config: New configuration parameters
        """
        self.config.update(new_config)
        
        # Reinitialize RAG pipeline if RAG config changed
        if 'rag' in new_config:
            self._initialize_rag_pipeline()
        
        self.logger.info("Router configuration updated")


# Utility functions
def create_rag_config(docs_path: str = "docs/data/", model: str = "gpt-3.5-turbo", k: int = 3) -> Dict[str, Any]:
    """
    Create a RAG configuration dictionary.
    
    Args:
        docs_path: Path to documents directory
        model: LLM model name
        k: Number of documents to retrieve
        
    Returns:
        RAG configuration dictionary
    """
    return {
        "rag": {
            "docs_path": docs_path,
            "model": model,
            "k": k
        }
    } 