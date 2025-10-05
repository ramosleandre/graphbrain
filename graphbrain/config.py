"""
Centralized configuration management for Graphbrain.

This module provides configuration loading from environment variables,
.env files, and defaults using Pydantic for validation.
"""

import os
from typing import Optional, Literal
from pathlib import Path

try:
    from pydantic import BaseModel, Field
    from pydantic_settings import BaseSettings
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


if PYDANTIC_AVAILABLE:
    class GraphbrainConfig(BaseSettings):
        """
        Centralized configuration for Graphbrain.

        Loads settings from environment variables and .env file.
        """

        # API Keys
        google_api_key: Optional[str] = Field(None, alias="GOOGLE_API_KEY")
        openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
        anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")

        # Backend Configuration
        default_backend: Literal["leveldb", "sqlite"] = Field("leveldb", alias="GRAPHBRAIN_BACKEND")

        # Embeddings Configuration
        default_embedder: Literal["sentence-transformers", "vertex-ai", "openai"] = Field(
            "sentence-transformers",
            alias="GRAPHBRAIN_EMBEDDER"
        )
        embedder_model: Optional[str] = Field(None, alias="GRAPHBRAIN_EMBEDDER_MODEL")
        embedding_cache_enabled: bool = Field(True, alias="GRAPHBRAIN_EMBEDDING_CACHE")
        embedding_cache_dir: Path = Field(
            Path.home() / ".cache" / "graphbrain" / "embeddings",
            alias="GRAPHBRAIN_EMBEDDING_CACHE_DIR"
        )

        # Vector Store Configuration
        chroma_persist_dir: Optional[str] = Field(None, alias="CHROMA_PERSIST_DIR")

        # BigQuery Configuration (for future BigQuery vector store)
        gcp_project_id: Optional[str] = Field(None, alias="GCP_PROJECT_ID")
        bq_dataset: Optional[str] = Field(None, alias="BQ_DATASET")
        bq_table: Optional[str] = Field(None, alias="BQ_TABLE")

        # Feature Flags
        enable_llm_parsing: bool = Field(False, alias="GRAPHBRAIN_ENABLE_LLM_PARSING")

        # Logging
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
            "INFO",
            alias="GRAPHBRAIN_LOG_LEVEL"
        )
        log_format: Literal["text", "json"] = Field("text", alias="GRAPHBRAIN_LOG_FORMAT")

        # Security
        query_timeout_seconds: int = Field(30, alias="GRAPHBRAIN_QUERY_TIMEOUT")
        max_pattern_depth: int = Field(10, alias="GRAPHBRAIN_MAX_PATTERN_DEPTH")

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False


    # Global config instance
    _config: Optional[GraphbrainConfig] = None


    def get_config(reload: bool = False) -> GraphbrainConfig:
        """
        Get the global configuration instance.

        Args:
            reload: Force reload configuration from environment

        Returns:
            GraphbrainConfig instance
        """
        global _config
        if _config is None or reload:
            _config = GraphbrainConfig()
        return _config


    def validate_api_key(provider: str) -> str:
        """
        Validate and retrieve API key for a provider.

        Args:
            provider: Provider name ('google', 'openai', 'anthropic')

        Returns:
            API key string

        Raises:
            ValueError: If API key is not configured
        """
        config = get_config()

        key_mapping = {
            "google": config.google_api_key,
            "vertex-ai": config.google_api_key,
            "openai": config.openai_api_key,
            "anthropic": config.anthropic_api_key,
        }

        api_key = key_mapping.get(provider.lower())

        if not api_key:
            raise ValueError(
                f"API key for '{provider}' not found. "
                f"Please set the appropriate environment variable in your .env file. "
                f"See .env.example for reference."
            )

        return api_key

else:
    # Fallback for when Pydantic is not available
    import warnings

    warnings.warn(
        "Pydantic not available. Install with: pip install pydantic pydantic-settings. "
        "Using basic configuration fallback.",
        RuntimeWarning
    )

    class GraphbrainConfig:
        """Basic configuration fallback without Pydantic."""

        def __init__(self):
            # Load from environment
            self.google_api_key = os.getenv("GOOGLE_API_KEY")
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

            self.default_backend = os.getenv("GRAPHBRAIN_BACKEND", "leveldb")
            self.default_embedder = os.getenv("GRAPHBRAIN_EMBEDDER", "sentence-transformers")
            self.embedder_model = os.getenv("GRAPHBRAIN_EMBEDDER_MODEL")

            self.embedding_cache_enabled = os.getenv("GRAPHBRAIN_EMBEDDING_CACHE", "true").lower() == "true"
            self.embedding_cache_dir = Path(
                os.getenv(
                    "GRAPHBRAIN_EMBEDDING_CACHE_DIR",
                    str(Path.home() / ".cache" / "graphbrain" / "embeddings")
                )
            )

            self.chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR")
            self.gcp_project_id = os.getenv("GCP_PROJECT_ID")
            self.bq_dataset = os.getenv("BQ_DATASET")
            self.bq_table = os.getenv("BQ_TABLE")

            self.enable_llm_parsing = os.getenv("GRAPHBRAIN_ENABLE_LLM_PARSING", "false").lower() == "true"
            self.log_level = os.getenv("GRAPHBRAIN_LOG_LEVEL", "INFO")
            self.log_format = os.getenv("GRAPHBRAIN_LOG_FORMAT", "text")

            self.query_timeout_seconds = int(os.getenv("GRAPHBRAIN_QUERY_TIMEOUT", "30"))
            self.max_pattern_depth = int(os.getenv("GRAPHBRAIN_MAX_PATTERN_DEPTH", "10"))


    _config = None


    def get_config(reload: bool = False) -> GraphbrainConfig:
        global _config
        if _config is None or reload:
            _config = GraphbrainConfig()
        return _config


    def validate_api_key(provider: str) -> str:
        config = get_config()

        key_mapping = {
            "google": config.google_api_key,
            "vertex-ai": config.google_api_key,
            "openai": config.openai_api_key,
            "anthropic": config.anthropic_api_key,
        }

        api_key = key_mapping.get(provider.lower())

        if not api_key:
            raise ValueError(
                f"API key for '{provider}' not found. "
                f"Please set the appropriate environment variable in your .env file. "
                f"See .env.example for reference."
            )

        return api_key


# Convenience exports
__all__ = [
    'GraphbrainConfig',
    'get_config',
    'validate_api_key',
    'PYDANTIC_AVAILABLE'
]
