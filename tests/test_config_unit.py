"""
Unit tests for EU5 Agent configuration management (eu5_agent/config.py).

Tests cover:
- Config loading from environment variables
- Config loading from .env file
- Default values when no config provided
- API key validation
- Model-specific settings (temperature support, max_completion_tokens)
- Singleton pattern behavior
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from eu5_agent.config import EU5Config, get_config, reset_config, load_dotenv_if_present


class TestLoadDotenv:
    """Tests for .env file loading functionality."""

    def test_load_dotenv_with_file(self, tmp_path, monkeypatch):
        """Test loading .env file when it exists."""
        # Create a .env file
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR=test_value\n")
        
        # Mock the module path to point to tmp_path
        with patch("eu5_agent.config.Path") as mock_path:
            mock_path.return_value.parent.parent = tmp_path
            
            # Mock dotenv module's load_dotenv
            with patch("dotenv.load_dotenv") as mock_load:
                result = load_dotenv_if_present()
                assert result is True
                mock_load.assert_called_once()

    def test_load_dotenv_without_file(self, tmp_path):
        """Test loading .env file when it doesn't exist."""
        with patch("eu5_agent.config.Path") as mock_path:
            mock_path.return_value.parent.parent = tmp_path
            result = load_dotenv_if_present()
            assert result is False

    def test_load_dotenv_without_dotenv_package(self, monkeypatch):
        """Test behavior when python-dotenv is not installed."""
        # Simulate ImportError for dotenv
        def mock_import(name, *args, **kwargs):
            if name == "dotenv":
                raise ImportError("No module named 'dotenv'")
            return __builtins__.__import__(name, *args, **kwargs)
        
        with patch("builtins.__import__", side_effect=mock_import):
            result = load_dotenv_if_present()
            assert result is False


class TestEU5Config:
    """Tests for EU5Config class."""

    def test_init_with_environment_variables(self, mock_env):
        """Test config initialization with environment variables."""
        config = EU5Config()
        
        assert config.api_key == "sk-test-key-12345"
        assert config.model == "gpt-5-mini"
        assert config.base_url == "https://api.openai.com/v1"
        assert config.tavily_api_key == "tvly-test-key-12345"

    def test_init_with_defaults(self, clean_env):
        """Test config initialization with default values."""
        config = EU5Config()
        
        assert config.api_key is None
        assert config.model == "gpt-5-mini"  # Default
        assert config.base_url == "https://api.openai.com/v1"  # Default
        assert config.tavily_api_key is None
        assert config.knowledge_path is None  # Triggers auto-detection

    def test_api_key_from_env(self, monkeypatch):
        """Test API key loading from environment."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-my-test-key")
        config = EU5Config()
        assert config.api_key == "sk-my-test-key"

    def test_model_from_env(self, monkeypatch):
        """Test model loading from environment."""
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        config = EU5Config()
        assert config.model == "gpt-4o"

    def test_base_url_from_env(self, monkeypatch):
        """Test base URL loading from environment."""
        monkeypatch.setenv("OPENAI_BASE_URL", "https://custom.api.com/v1")
        config = EU5Config()
        assert config.base_url == "https://custom.api.com/v1"

    def test_knowledge_path_from_env(self, monkeypatch, tmp_path):
        """Test knowledge path loading from environment."""
        kb_path = str(tmp_path / "knowledge")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", kb_path)
        config = EU5Config()
        assert config.knowledge_path == kb_path

    def test_tavily_api_key_from_env(self, monkeypatch):
        """Test Tavily API key loading from environment."""
        monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-key")
        config = EU5Config()
        assert config.tavily_api_key == "tvly-test-key"


class TestModelSpecificSettings:
    """Tests for model-specific configuration settings."""

    def test_gpt5_model_temperature_support(self, monkeypatch):
        """Test that gpt-5 models don't support temperature."""
        monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")
        config = EU5Config()
        assert config.supports_temperature is False

    def test_gpt4_model_temperature_support(self, monkeypatch):
        """Test that gpt-4 models support temperature."""
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        config = EU5Config()
        assert config.supports_temperature is True

    def test_gpt5_uses_max_completion_tokens(self, monkeypatch):
        """Test that gpt-5 models use max_completion_tokens."""
        monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")
        config = EU5Config()
        assert config.uses_max_completion_tokens is True

    def test_gpt4_uses_max_tokens(self, monkeypatch):
        """Test that gpt-4 models don't use max_completion_tokens."""
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        config = EU5Config()
        assert config.uses_max_completion_tokens is False

    def test_generic_model_defaults(self, monkeypatch):
        """Test defaults for non-GPT-5 models."""
        monkeypatch.setenv("OPENAI_MODEL", "some-other-model")
        config = EU5Config()
        assert config.supports_temperature is True
        assert config.uses_max_completion_tokens is False


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_validate_with_missing_api_key(self, clean_env):
        """Test validation fails when API key is missing."""
        config = EU5Config()
        is_valid, error = config.validate()
        
        assert is_valid is False
        assert "OPENAI_API_KEY not set" in error

    def test_validate_with_missing_knowledge_path(self, monkeypatch, tmp_path):
        """Test validation fails when knowledge base doesn't exist."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(tmp_path / "nonexistent"))
        
        config = EU5Config()
        is_valid, error = config.validate()
        
        assert is_valid is False
        assert "Knowledge base not found" in error

    def test_validate_with_valid_config(self, monkeypatch, temp_knowledge_base):
        """Test validation succeeds with valid configuration."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))
        
        config = EU5Config()
        is_valid, error = config.validate()
        
        assert is_valid is True
        assert error is None


class TestConfigHelpers:
    """Tests for config helper methods."""

    def test_get_api_params(self, mock_env):
        """Test getting API parameters."""
        config = EU5Config()
        params = config.get_api_params()
        
        assert params["api_key"] == "sk-test-key-12345"
        assert params["base_url"] == "https://api.openai.com/v1"

    def test_repr_masks_api_key(self, monkeypatch):
        """Test that __repr__ masks the API key."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-1234567890abcdefghij")
        config = EU5Config()
        repr_str = repr(config)
        
        # Check that first 10 chars and last 4 are shown
        assert "sk-1234567" in repr_str  # First part
        assert "ghij" in repr_str  # Last 4 chars
        assert "..." in repr_str  # Ellipsis separator
        assert "api_key=" in repr_str
        # Middle should be hidden
        assert "abcdef" not in repr_str

    def test_repr_with_no_api_key(self, clean_env):
        """Test __repr__ when API key is not set."""
        config = EU5Config()
        repr_str = repr(config)
        
        assert "NOT SET" in repr_str

    def test_repr_with_tavily_key(self, monkeypatch):
        """Test __repr__ shows Tavily status."""
        monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-key")
        config = EU5Config()
        repr_str = repr(config)
        
        assert "SET" in repr_str

    def test_repr_without_tavily_key(self, clean_env):
        """Test __repr__ when Tavily is not configured."""
        config = EU5Config()
        repr_str = repr(config)
        
        assert "NOT SET (web search disabled)" in repr_str


class TestConfigSingleton:
    """Tests for singleton pattern behavior."""

    def test_get_config_returns_singleton(self):
        """Test that get_config returns the same instance."""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2

    def test_reset_config_creates_new_instance(self):
        """Test that reset_config clears the singleton."""
        config1 = get_config()
        reset_config()
        config2 = get_config()
        
        assert config1 is not config2

    def test_reset_config_multiple_times(self):
        """Test that reset_config can be called multiple times."""
        get_config()
        reset_config()
        reset_config()  # Should not raise
        config = get_config()
        
        assert config is not None
        assert isinstance(config, EU5Config)

    def test_singleton_preserves_state(self, monkeypatch):
        """Test that singleton preserves state across calls."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        
        config1 = get_config()
        api_key1 = config1.api_key
        
        config2 = get_config()
        api_key2 = config2.api_key
        
        assert api_key1 == api_key2
        assert api_key1 == "sk-test-key"


class TestConfigIntegration:
    """Integration tests for configuration."""

    def test_full_config_flow(self, monkeypatch, temp_knowledge_base):
        """Test complete configuration flow."""
        # Set environment
        monkeypatch.setenv("OPENAI_API_KEY", "sk-integration-test")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))
        monkeypatch.setenv("TAVILY_API_KEY", "tvly-integration-test")
        
        # Create config
        config = EU5Config()
        
        # Verify all settings
        assert config.api_key == "sk-integration-test"
        assert config.model == "gpt-5-mini"
        assert config.knowledge_path == str(temp_knowledge_base)
        assert config.tavily_api_key == "tvly-integration-test"
        
        # Verify model settings
        assert config.supports_temperature is False
        assert config.uses_max_completion_tokens is True
        
        # Verify validation
        is_valid, error = config.validate()
        assert is_valid is True
        assert error is None

    def test_config_with_partial_environment(self, monkeypatch):
        """Test configuration with only some environment variables set."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-partial-test")
        # Don't set other variables, use defaults
        
        config = EU5Config()
        
        assert config.api_key == "sk-partial-test"
        assert config.model == "gpt-5-mini"  # Default
        assert config.base_url == "https://api.openai.com/v1"  # Default
        assert config.tavily_api_key is None  # Not set
