"""
Secure configuration loader for Willow v6.
Handles environment variables, validates configs, and protects sensitive data.
Optimized for performance with caching and lazy loading.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import cached_property, lru_cache
import weakref
import time
from threading import RLock


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class SecureConfigLoader:
    """Secure configuration management with environment variable support and advanced caching."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the configuration loader.
        
        Args:
            project_root: Root directory of the project. If None, auto-detected.
        """
        self.project_root = project_root or self._detect_project_root()
        self._constitution_cache: Optional[Dict[str, Any]] = None
        self._config_cache: Dict[str, Any] = {}
        self._env_cache: Dict[str, Optional[str]] = {}  # Cache environment variables
        self._last_cache_time = 0.0
        self._cache_ttl = 300.0  # 5 minutes cache TTL
        self._cache_lock = RLock()  # Thread-safe caching
        
        # Validate environment
        self._validate_environment()
    
    @lru_cache(maxsize=1)
    def _detect_project_root(self) -> Path:
        """Auto-detect project root directory (cached)."""
        current = Path(__file__).parent
        
        # Look for project markers
        markers = ['requirements.txt', 'config.yaml', '.git']
        
        for _ in range(5):  # Limit search depth
            if any((current / marker).exists() for marker in markers):
                return current
            current = current.parent
        
        # Fallback to parent of src directory
        return Path(__file__).parent.parent
    
    def _validate_environment(self) -> None:
        """Validate required environment variables and project structure."""
        # Check if project root exists and is accessible
        if not self.project_root.exists():
            raise ConfigurationError(f"Project root not found: {self.project_root}")
        
        # Warn about missing optional environment variables
        optional_vars = [
            'OPENAI_API_KEY',
            'GOOGLE_API_KEY', 
            'ANTHROPIC_API_KEY',
            'WILLOW_LOG_LEVEL'
        ]
        
        missing_vars = []
        for var in optional_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logging.info(f"Optional environment variables not set: {', '.join(missing_vars)}")
    
    def _is_cache_valid(self) -> bool:
        """Check if configuration cache is still valid."""
        return (time.time() - self._last_cache_time) < self._cache_ttl
    
    def _update_cache_time(self) -> None:
        """Update cache timestamp."""
        self._last_cache_time = time.time()
    
    def invalidate_cache(self) -> None:
        """Manually invalidate all configuration caches."""
        with self._cache_lock:
            self._constitution_cache = None
            self._config_cache.clear()
            self._env_cache.clear()
            self._last_cache_time = 0.0
            logging.info("Configuration cache invalidated")
    
    @cached_property  
    def constitution(self) -> Dict[str, Any]:
        """Load and validate the core constitution configuration (cached with thread safety).
        
        Returns:
            Validated constitution configuration
            
        Raises:
            ConfigurationError: If constitution file is invalid or missing
        """
        with self._cache_lock:
            if self._constitution_cache is not None and self._is_cache_valid():
                return self._constitution_cache
            
            config_paths = [
                self.project_root / 'willow-dev' / 'config' / 'core_constitution.json',
                self.project_root / 'config' / 'core_constitution.json',
                self.project_root / 'core_constitution.json'
            ]
            
            constitution_path = None
            for path in config_paths:
                if path.exists():
                    constitution_path = path
                    break
            
            if not constitution_path:
                raise ConfigurationError(
                    f"Constitution file not found in any of: {[str(p) for p in config_paths]}"
                )
            
            try:
                with open(constitution_path, 'r', encoding='utf-8') as f:
                    constitution = json.load(f)
                
                # Validate required sections efficiently
                required_sections = ['Identity', 'Rules', 'Prompt Library', 'Modules']
                missing_sections = [s for s in required_sections if s not in constitution]
                
                if missing_sections:
                    raise ConfigurationError(
                        f"Constitution missing required sections: {missing_sections}"
                    )
                
                # Validate Identity section
                identity = constitution.get('Identity', {})
                required_identity_fields = ['name', 'version', 'description']
                missing_fields = [f for f in required_identity_fields if f not in identity]
                
                if missing_fields:
                    raise ConfigurationError(
                        f"Constitution Identity section missing fields: {missing_fields}"
                    )
                
                self._constitution_cache = constitution
                self._update_cache_time()
                logging.info(f"Constitution loaded successfully from: {constitution_path}")
                return constitution
                
            except json.JSONDecodeError as e:
                raise ConfigurationError(f"Invalid JSON in constitution file: {e}")
            except Exception as e:
                raise ConfigurationError(f"Error loading constitution: {e}")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Safely retrieve API key for a service.
        
        Args:
            service: Service name (e.g., 'openai', 'google', 'anthropic')
            
        Returns:
            API key if available, None otherwise
        """
        key_mapping = {
            'openai': 'OPENAI_API_KEY',
            'google': 'GOOGLE_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'gemini': 'GOOGLE_API_KEY'
        }
        
        env_var = key_mapping.get(service.lower())
        if not env_var:
            logging.warning(f"Unknown service for API key: {service}")
            return None
        
        api_key = os.getenv(env_var)
        if not api_key:
            logging.warning(f"API key not found for {service} (env var: {env_var})")
            return None
        
        # Basic validation - check if it looks like a valid key
        if len(api_key.strip()) < 10:
            logging.warning(f"API key for {service} appears invalid (too short)")
            return None
        
        return api_key.strip()
    
    def _get_env_cached(self, key: str, default: str = '') -> str:
        """Get environment variable with caching for performance.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Environment variable value or default
        """
        if key in self._env_cache:
            cached_value = self._env_cache[key]
            return cached_value if cached_value is not None else default
        
        value = os.getenv(key)
        self._env_cache[key] = value
        return value if value is not None else default
    
    def get_log_level(self) -> str:
        """Get configured log level with caching.
        
        Returns:
            Log level string (default: 'INFO')
        """
        level = self._get_env_cached('WILLOW_LOG_LEVEL', 'INFO').upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        if level not in valid_levels:
            logging.warning(f"Invalid log level '{level}', using INFO")
            return 'INFO'
        
        return level
    
    @lru_cache(maxsize=1)
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration with defaults and caching.
        
        Returns:
            Model configuration dictionary
        """
        return {
            'valid_models': [
                'goekdenizguelmez/josiefied-qwen3:1.7b',
                'qwen3:0.6b',
                'nomic-embed-text:latest'
            ],
            'default_timeout': int(self._get_env_cached('WILLOW_DEFAULT_TIMEOUT', '15')),
            'max_prompt_length': int(self._get_env_cached('WILLOW_MAX_PROMPT_LENGTH', '50000')),
            'model_timeouts': {
                'goekdenizguelmez/josiefied-qwen3:1.7b': int(self._get_env_cached('WILLOW_PRIMARY_TIMEOUT', '90')),
                'default': int(self._get_env_cached('WILLOW_DEFAULT_TIMEOUT', '15'))
            }
        }


# Global instance - initialized lazily
_config_loader: Optional[SecureConfigLoader] = None


def get_config() -> SecureConfigLoader:
    """Get the global configuration loader instance.
    
    Returns:
        SecureConfigLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = SecureConfigLoader()
    return _config_loader


def load_constitution() -> Dict[str, Any]:
    """Load constitution using the secure config loader.
    
    Returns:
        Constitution configuration
    """
    return get_config().constitution