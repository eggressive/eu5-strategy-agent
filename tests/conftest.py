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
from typing import Dict, Generator
from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response."""

    def _create_response(
        content: str = "Test response", tool_calls: list = None, finish_reason: str = "stop"
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
def mock_openai_client(mock_openai_response):
    """Create a mock OpenAI client."""
    client = Mock()
    client.chat = Mock()
    client.chat.completions = Mock()
    client.chat.completions.create = Mock(
        return_value=mock_openai_response("Test response from OpenAI")
    )
    return client


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
def mock_tavily_response():
    """Create a mock Tavily API response."""

    def _create_response(query: str = "test query", num_results: int = 3):
        """
        Create a mock Tavily search response.

        Args:
            query: Search query
            num_results: Number of results to return
        """
        results = []
        for i in range(num_results):
            results.append(
                {
                    "title": f"Test Result {i+1}",
                    "url": f"https://eu5.paradoxwikis.com/test-{i+1}",
                    "content": f"Test content for result {i+1}. " * 20,  # ~300 chars
                    "score": 0.9 - (i * 0.1),
                }
            )

        return {"results": results}

    return _create_response


@pytest.fixture
def mock_tavily_client(mock_tavily_response):
    """Create a mock Tavily client."""
    client = Mock()
    client.search = Mock(return_value=mock_tavily_response())
    return client


@pytest.fixture
def clean_env(monkeypatch) -> None:
    """
    Clean environment variables for testing.

    Removes all EU5 and OpenAI related environment variables.
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


@pytest.fixture
def mock_dotenv(monkeypatch):
    """Mock the dotenv loading functionality."""

    def mock_load_dotenv(*args, **kwargs):
        return True

    monkeypatch.setattr("eu5_agent.config.load_dotenv", mock_load_dotenv, raising=False)


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


@pytest.fixture
def sample_markdown_files():
    """Provide sample markdown content for testing."""
    return {
        "economy": "# Economy\n\nDucats, trade, and production.",
        "society": "# Society\n\nEstates, privileges, and agendas.",
        "beginner": "# Beginner Guide\n\nStart with a strong nation.",
        "england": "# England\n\nConquer Scotland first.",
    }
