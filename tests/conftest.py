"""
Pytest configuration and shared fixtures for EU5 Strategy Agent tests.

This module provides:
- Mock OpenAI API responses
- Temporary knowledge base fixtures
- Mock Tavily search responses
- Configuration fixtures for testing
"""

import tempfile
from pathlib import Path
from typing import Dict, Generator, Optional
from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response."""

    def _create_response(
        content: str = "Test response", tool_calls: Optional[list] = None, finish_reason: str = "stop"
    ):
        """
        Create a mock OpenAI response.

        Args:
            content: Response content text
            tool_calls: Optional list of tool calls
            finish_reason: Completion finish reason
        """
        message = Mock()
        message.content = content
        message.tool_calls = tool_calls
        message.role = "assistant"
        message.model_dump = Mock(
            return_value={"role": "assistant", "content": content, "tool_calls": tool_calls}
        )

        choice = Mock()
        choice.message = message
        choice.finish_reason = finish_reason

        usage = Mock()
        usage.prompt_tokens = 10
        usage.completion_tokens = 20
        usage.total_tokens = 30

        response = Mock()
        response.choices = [choice]
        response.model = "gpt-5-mini"
        response.id = "chatcmpl-test123"
        response.usage = usage

        return response

    return _create_response


@pytest.fixture
def temp_knowledge_base() -> Generator[Path, None, None]:
    """
    Create a temporary knowledge base directory with sample files.

    Yields:
        Path to temporary knowledge base directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir)

        # Create directory structure
        mechanics_dir = kb_path / "mechanics"
        strategy_dir = kb_path / "strategy"
        nations_dir = kb_path / "nations"
        resources_dir = kb_path / "resources"

        mechanics_dir.mkdir()
        strategy_dir.mkdir()
        nations_dir.mkdir()
        resources_dir.mkdir()

        # Create sample mechanics files
        (mechanics_dir / "economy_mechanics.md").write_text(
            "# Economy Mechanics\n\nTest content for economy mechanics."
        )
        (mechanics_dir / "society_mechanics.md").write_text(
            "# Society Mechanics\n\nTest content for society (estates) mechanics."
        )
        (mechanics_dir / "military_mechanics.md").write_text(
            "# Military Mechanics\n\nTest content for military mechanics."
        )

        # Create sample strategy files
        (strategy_dir / "beginner_route.md").write_text(
            "# Beginner's Route\n\nTest guide for beginners."
        )
        (strategy_dir / "common_mistakes.md").write_text(
            "# Common Mistakes\n\nTest list of common mistakes."
        )

        # Create sample nation file
        (nations_dir / "nation_england.md").write_text(
            "# England Strategy\n\nTest opening strategy for England."
        )

        # Create resources file
        (resources_dir / "eu5_resources.md").write_text(
            "# EU5 Resources\n\nTest list of community resources."
        )

        yield kb_path


@pytest.fixture
def clean_env(monkeypatch) -> None:
    """
    Clean environment variables for testing.

    Removes all EU5 and OpenAI related environment variables
    and prevents .env file loading.
    """
    env_vars = [
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "OPENAI_BASE_URL",
        "EU5_KNOWLEDGE_PATH",
        "TAVILY_API_KEY",
    ]

    for var in env_vars:
        monkeypatch.delenv(var, raising=False)

    # Prevent .env file loading during tests
    monkeypatch.setattr("eu5_agent.config.load_dotenv_if_present", lambda: False)


@pytest.fixture
def mock_env(monkeypatch) -> Dict[str, str]:
    """
    Set up mock environment variables for testing.

    Returns:
        Dictionary of environment variables set
    """
    env_vars = {
        "OPENAI_API_KEY": "sk-test-key-12345",
        "OPENAI_MODEL": "gpt-5-mini",
        "OPENAI_BASE_URL": "https://api.openai.com/v1",
        "TAVILY_API_KEY": "tvly-test-key-12345",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


@pytest.fixture
def sample_tool_call():
    """Create a sample tool call object for testing."""

    def _create_tool_call(
        function_name: str = "query_knowledge",
        arguments: str = '{"category": "mechanics", "subcategory": "economy"}',
    ):
        """
        Create a mock tool call.

        Args:
            function_name: Name of the function being called
            arguments: JSON string of function arguments
        """
        tool_call = Mock()
        tool_call.id = "call_test123"
        tool_call.function = Mock()
        tool_call.function.name = function_name
        tool_call.function.arguments = arguments
        tool_call.type = "function"

        return tool_call

    return _create_tool_call


@pytest.fixture(autouse=True)
def reset_config_singleton():
    """
    Reset the config singleton between tests.

    This ensures each test gets a fresh configuration instance.
    """
    from eu5_agent.config import reset_config

    reset_config()
    yield
    reset_config()
