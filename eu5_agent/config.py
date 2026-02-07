"""
EU5 Standalone Configuration

Simple configuration loader that supports:
1. Environment variables (primary)
2. .env file (fallback)
3. Default values

Keeps the standalone agent lightweight and independent.
"""

import os
from pathlib import Path
from typing import Optional


def _parse_float(value: Optional[str], default: float) -> float:
    """Parse an env var as float, returning default on failure."""
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _parse_int(value: Optional[str], default: int) -> int:
    """Parse an env var as int, returning default on failure."""
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def load_dotenv_if_present():
    """Load .env file if it exists (using python-dotenv if available)."""
    try:
        from dotenv import load_dotenv
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return True
    except ImportError:
        # python-dotenv not installed, skip
        pass
    return False


class EU5Config:
    """
    Configuration for EU5 Standalone Agent.

    Loads settings in this priority order:
    1. Environment variables
    2. .env file (if python-dotenv installed)
    3. Default values
    """

    def __init__(self):
        """Initialize configuration from environment."""
        # Try to load .env file
        load_dotenv_if_present()

        # OpenAI API Configuration
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        # Knowledge Base Configuration
        # Set to None to trigger auto-detection in knowledge.py
        # Auto-detection uses the packaged knowledge at eu5_agent/knowledge
        self.knowledge_path = os.getenv("EU5_KNOWLEDGE_PATH", None)

        # Web Search Configuration (Optional)
        # Tavily provides AI-optimized search when knowledge base is insufficient
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")

        # Configurable API parameters with sensible defaults
        self.temperature = _parse_float(os.getenv("OPENAI_TEMPERATURE"), default=0.7)
        self.max_completion_tokens = _parse_int(
            os.getenv("OPENAI_MAX_COMPLETION_TOKENS"), default=4096
        )

    @staticmethod
    def supports_temperature(model: str) -> bool:
        """Check if the model supports temperature parameter."""
        # gpt-5 models don't support temperature (only default=1)
        if model and "gpt-5" in model:
            return False
        return True

    @staticmethod
    def uses_max_completion_tokens(model: str) -> bool:
        """Check if model uses max_completion_tokens instead of max_tokens."""
        # gpt-5 models use max_completion_tokens
        if model and "gpt-5" in model:
            return True
        return False

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate configuration.

        Returns:
            (is_valid, error_message)
        """
        if not self.api_key:
            return False, (
                "OPENAI_API_KEY not set. Please set it via:\n"
                "  export OPENAI_API_KEY='your-key-here'\n"
                "Or create a .env file with:\n"
                "  OPENAI_API_KEY=your-key-here"
            )

        # If a knowledge path wasn't explicitly configured, attempt to
        # auto-detect the packaged knowledge base that lives inside the
        # package (EU5Knowledge handles package-relative resolution). If
        # auto-detection succeeds, consider configuration valid.
        if self.knowledge_path is None:
            try:
                # Import here to avoid importing EU5Knowledge at module import
                # time and to keep dependencies minimal during simple config
                # checks. If packaged knowledge is missing, EU5Knowledge will
                # raise FileNotFoundError which we convert to a validation
                # error message.
                from .knowledge import EU5Knowledge

                # Attempt to construct (this triggers auto-detection). No
                # need to use the instance afterward.
                EU5Knowledge()
            except FileNotFoundError:
                return False, (
                    "Knowledge base could not be detected locally.\n"
                    "Set EU5_KNOWLEDGE_PATH environment variable or ensure\n"
                    "the packaged knowledge files exist in the package's 'knowledge/' directory."
                )
        else:
            knowledge_path = Path(self.knowledge_path)
            if not knowledge_path.exists():
                return False, (
                    f"Knowledge base not found at: {self.knowledge_path}\n"
                    f"Set EU5_KNOWLEDGE_PATH to correct location."
                )

        return True, None

    def get_api_params(self) -> dict:
        """
        Get API parameters for OpenAI client.

        Returns:
            Dictionary with api_key and base_url
        """
        return {
            "api_key": self.api_key,
            "base_url": self.base_url
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        masked_key = f"{self.api_key[:10]}...{self.api_key[-4:]}" if self.api_key else "NOT SET"
        tavily_status = "SET" if self.tavily_api_key else "NOT SET (web search disabled)"
        return (
            f"EU5Config(\n"
            f"  model={self.model}\n"
            f"  api_key={masked_key}\n"
            f"  knowledge_path={self.knowledge_path}\n"
            f"  tavily_api_key={tavily_status}\n"
            f"  temperature={self.temperature}\n"
            f"  max_completion_tokens={self.max_completion_tokens}\n"
            f")"
        )


# Singleton instance
_config = None


def get_config() -> EU5Config:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = EU5Config()
    return _config


def reset_config():
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None


# Quick test
if __name__ == "__main__":
    config = get_config()
    print("EU5 Standalone Configuration")
    print("=" * 70)
    print(config)
    print()

    is_valid, error = config.validate()
    if is_valid:
        print("✓ Configuration is valid")
    else:
        print(f"✗ Configuration error:\n{error}")
