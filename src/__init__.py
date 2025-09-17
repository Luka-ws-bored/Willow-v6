"""
Willow v6.0.0 - AI Automation Framework with RAG Integration

A powerful local-first AI automation framework with advanced RAG (Retrieval-Augmented
Generation) capabilities, designed for seamless fallback between multiple LLM providers
and intelligent document processing.

Key Features:
- Multi-provider LLM support (OpenAI, Anthropic, Google, Local models)
- Advanced RAG with Vector Database integration
- Async/await support throughout
- Security-first design with input validation
- Graceful degradation when dependencies are missing
- Performance optimization with caching and batching
- Comprehensive testing and monitoring

Version: 6.0.0
Release Date: 2025-09-09
License: MIT
"""

__version__ = "6.0.0"
__author__ = "Willow Development Team"
__email__ = "support@willow-ai.dev"
__license__ = "MIT"
__status__ = "Production"

# Core imports for easy access
from .main import (
    query_llm,
    async_query_llm,
    batch_query_llm,
    async_query_rag_simple,
    list_available_models,
    validate_model_name,
    validate_prompt,
    get_performance_stats,
    clear_caches,
    warm_up_models,
    RAG_AVAILABLE
)

# Configuration
from .config_loader import get_config, load_constitution

# RAG functionality (with graceful degradation)
try:
    from .rag_pipeline import (
        RAGPipeline,
        create_rag_pipeline,
        quick_rag_query,
        RAGError
    )
    RAG_PIPELINE_AVAILABLE = True
except ImportError:
    RAG_PIPELINE_AVAILABLE = False

try:
    from .utils.vector_db import (
        VectorDB,
        get_vector_db,
        VECTOR_DB_AVAILABLE
    )
except ImportError:
    VECTOR_DB_AVAILABLE = False

try:
    from .utils.rag_pipeline import (
        get_rag_pipeline
    )
    FULL_RAG_AVAILABLE = True
except ImportError:
    FULL_RAG_AVAILABLE = False

# Optional utilities
try:
    from .utils.logging_config import (
        get_willow_logger,
        setup_willow_logging,
        log_rag_operation,
        rag_logger
    )
    ENHANCED_LOGGING_AVAILABLE = True
except ImportError:
    ENHANCED_LOGGING_AVAILABLE = False

try:
    from .utils.retry_logic import (
        RAGRetryConfig,
        with_retry,
        with_async_retry,
        CircuitBreaker
    )
    RETRY_LOGIC_AVAILABLE = True
except ImportError:
    RETRY_LOGIC_AVAILABLE = False

# Capability summary
CAPABILITIES = {
    "core_llm": True,  # Always available
    "rag_simple": RAG_PIPELINE_AVAILABLE,
    "rag_full": FULL_RAG_AVAILABLE and RAG_AVAILABLE,
    "vector_db": VECTOR_DB_AVAILABLE,
    "enhanced_logging": ENHANCED_LOGGING_AVAILABLE,
    "retry_logic": RETRY_LOGIC_AVAILABLE,
    "async_support": True,  # Always available
    "security_features": True,  # Always available
    "performance_optimization": True  # Always available
}

def get_version_info():
    """Get detailed version and capability information."""
    return {
        "version": __version__,
        "status": __status__,
        "capabilities": CAPABILITIES,
        "dependencies": {
            "core": ["psutil", "rich"],
            "rag_basic": ["faiss-cpu", "sentence-transformers"],
            "rag_full": ["langchain", "langchain-community", "faiss-cpu", "sentence-transformers"],
            "evaluation": ["datasets", "ragas"],
            "gpu": ["faiss-gpu"]
        }
    }

def print_banner():
    """Print Willow v6 banner with capability summary."""
    print("🌲 Willow v6.0.0 - AI Automation Framework")
    print("=" * 50)
    print(f"Version: {__version__}")
    print(f"Status: {__status__}")
    print("\n🎯 Capabilities:")
    
    for capability, available in CAPABILITIES.items():
        status = "✅" if available else "❌"
        name = capability.replace("_", " ").title()
        print(f"   {status} {name}")
    
    # Installation suggestions
    missing_capabilities = [k for k, v in CAPABILITIES.items() if not v and k not in ["core_llm", "async_support", "security_features", "performance_optimization"]]
    
    if missing_capabilities:
        print("\n💡 To enable additional features:")
        if not CAPABILITIES["rag_simple"]:
            print("   pip install faiss-cpu sentence-transformers")
        if not CAPABILITIES["rag_full"]:
            print("   pip install langchain langchain-community")
        print("   pip install datasets ragas  # For evaluation")
    else:
        print("\n🎉 All features available!")
    
    print("\n📚 Quick Start:")
    print("   from willow import query_llm, async_query_rag_simple")
    print("   response = query_llm('Hello, Willow!')")
    if CAPABILITIES["rag_simple"]:
        print("   rag_response = await async_query_rag_simple('Query', documents=['Doc1', 'Doc2'])")
    
    print(f"\n🔗 Documentation: https://github.com/willow-ai/willow-v6")
    print("=" * 50)

# Export all public APIs
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    "get_version_info",
    "print_banner",
    "CAPABILITIES",
    
    # Core functions
    "query_llm",
    "async_query_llm",
    "batch_query_llm",
    "async_query_rag_simple",
    "list_available_models",
    "validate_model_name",
    "validate_prompt",
    "get_performance_stats",
    "clear_caches",
    "warm_up_models",
    
    # Configuration
    "get_config",
    "load_constitution",
    
    # Availability flags
    "RAG_AVAILABLE",
    "RAG_PIPELINE_AVAILABLE",
    "VECTOR_DB_AVAILABLE",
    "FULL_RAG_AVAILABLE",
    "ENHANCED_LOGGING_AVAILABLE",
    "RETRY_LOGIC_AVAILABLE"
]

# Conditionally add RAG exports
if RAG_PIPELINE_AVAILABLE:
    __all__.extend([
        "RAGPipeline",
        "create_rag_pipeline",
        "quick_rag_query",
        "RAGError"
    ])

if VECTOR_DB_AVAILABLE:
    __all__.extend([
        "VectorDB",
        "get_vector_db"
    ])

if FULL_RAG_AVAILABLE:
    __all__.extend([
        "get_rag_pipeline"
    ])

if ENHANCED_LOGGING_AVAILABLE:
    __all__.extend([
        "get_willow_logger",
        "setup_willow_logging",
        "log_rag_operation",
        "rag_logger"
    ])

if RETRY_LOGIC_AVAILABLE:
    __all__.extend([
        "RAGRetryConfig",
        "with_retry",
        "with_async_retry",
        "CircuitBreaker"
    ])


# Initialize on import
if __name__ != "__main__":
    # Show banner only when imported, not when run directly
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Willow v{__version__} initialized with capabilities: {CAPABILITIES}")


# Main execution
if __name__ == "__main__":
    # Show full banner when run directly
    print_banner()
    
    # Show detailed capability report
    version_info = get_version_info()
    print(f"\n📊 Detailed Version Info:")
    print(f"   {version_info}")