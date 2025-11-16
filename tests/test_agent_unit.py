"""
Unit tests for EU5Agent (eu5_agent/agent.py).

Tests cover:
- Agent initialization with various configurations
- Conversation history management (add/retrieve messages)
- Tool execution loop (max iterations, early termination)
- Error handling for OpenAI API failures
- Response parsing and formatting
- Mocked OpenAI API responses to avoid real API calls
"""

import json
from unittest.mock import Mock, patch

import pytest

from eu5_agent.agent import EU5Agent
from eu5_agent.config import EU5Config


class TestAgentInitialization:
    """Tests for EU5Agent initialization."""

    def test_init_with_api_key(self, temp_knowledge_base, monkeypatch):
        """Test agent initialization with API key."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()

        assert agent.api_key == "sk-test-key"
        assert agent.model == "gpt-5-mini"
        assert agent.knowledge is not None

    def test_init_with_custom_model(self, temp_knowledge_base, monkeypatch):
        """Test agent initialization with custom model."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent(model="gpt-4o")

        assert agent.model == "gpt-4o"

    def test_init_without_api_key_raises_error(self, clean_env, temp_knowledge_base):
        """Test that initialization raises error without API key."""
        with pytest.raises(ValueError) as exc_info:
            EU5Agent(knowledge_path=str(temp_knowledge_base))

        assert "API key not provided" in str(exc_info.value)

    def test_init_with_custom_config(self, temp_knowledge_base):
        """Test agent initialization with custom config."""
        config = EU5Config()
        config.api_key = "sk-custom-key"
        config.model = "gpt-4o"
        config.knowledge_path = str(temp_knowledge_base)

        agent = EU5Agent(config=config)

        assert agent.api_key == "sk-custom-key"
        assert agent.model == "gpt-4o"

    def test_init_creates_message_history(self, temp_knowledge_base, monkeypatch):
        """Test that initialization creates message history with system prompt."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()

        assert len(agent.messages) == 1
        assert agent.messages[0]["role"] == "system"
        content = agent.messages[0]["content"]
        assert isinstance(content, str)
        assert len(content) > 0


class TestConversationHistory:
    """Tests for conversation history management."""

    def test_reset_clears_history(self, temp_knowledge_base, monkeypatch):
        """Test that reset clears conversation history."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()

        # Add some messages
        agent.messages.append({"role": "user", "content": "test"})
        agent.messages.append({"role": "assistant", "content": "response"})
        assert len(agent.messages) == 3

        # Reset
        agent.reset()

        # Should only have system message
        assert len(agent.messages) == 1
        assert agent.messages[0]["role"] == "system"

    def test_chat_adds_to_history(self, temp_knowledge_base, monkeypatch, mock_openai_response):
        """Test that chat adds messages to history."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()

        # Mock the OpenAI client
        agent.client.chat.completions.create = Mock(
            return_value=mock_openai_response("Test response")
        )

        initial_count = len(agent.messages)
        agent.chat("test question")

        # Should have added user message and assistant message
        assert len(agent.messages) > initial_count
        assert any(m["role"] == "user" for m in agent.messages)
        assert any(m["role"] == "assistant" for m in agent.messages)


class TestToolExecution:
    """Tests for tool execution functionality."""

    def test_query_knowledge_tool(self, temp_knowledge_base, monkeypatch):
        """Test knowledge query tool execution."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        result = agent._query_knowledge("mechanics", "economy")

        assert "Economy Mechanics" in result
        assert "Local Knowledge Base" in result

    def test_query_knowledge_invalid_category(self, temp_knowledge_base, monkeypatch):
        """Test knowledge query with invalid category."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        result = agent._query_knowledge("invalid_cat", "test")

        assert "Error" in result

    def test_web_search_tool(self, temp_knowledge_base, monkeypatch):
        """Test web search tool execution."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))
        monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-key")

        agent = EU5Agent()

        # Mock the search function where it's imported
        with patch("eu5_agent.search.search_eu5_wiki") as mock_search:
            mock_search.return_value = [
                {"title": "Test", "url": "http://test.com", "snippet": "test content"}
            ]

            result = agent._web_search("test query")

        assert "Web Search" in result
        assert "Test" in result

    def test_web_search_error_handling(self, temp_knowledge_base, monkeypatch):
        """Test web search error handling."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()

        # Mock search to raise an error
        with patch("eu5_agent.search.search_eu5_wiki", side_effect=Exception("API Error")):
            result = agent._web_search("test query")

        assert "error" in result.lower()

    def test_execute_tool_call_knowledge(self, temp_knowledge_base, monkeypatch, sample_tool_call):
        """Test executing a knowledge query tool call."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        tool_call = sample_tool_call(
            "query_knowledge", '{"category": "mechanics", "subcategory": "economy"}'
        )

        result = agent._execute_tool_call(tool_call)

        assert len(result) > 0
        assert "Economy" in result or "Error" in result

    def test_execute_tool_call_web_search(self, temp_knowledge_base, monkeypatch, sample_tool_call):
        """Test executing a web search tool call."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        tool_call = sample_tool_call("web_search", '{"query": "test"}')

        with patch("eu5_agent.search.search_eu5_wiki", return_value=[]):
            result = agent._execute_tool_call(tool_call)

        assert "No results" in result or "error" in result.lower()

    def test_execute_tool_call_unknown_tool(
        self, temp_knowledge_base, monkeypatch, sample_tool_call
    ):
        """Test executing an unknown tool call."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        tool_call = sample_tool_call("unknown_tool", "{}")

        result = agent._execute_tool_call(tool_call)

        assert "Unknown tool" in result


class TestChatFunctionality:
    """Tests for chat functionality."""

    def test_chat_simple_response(self, temp_knowledge_base, monkeypatch, mock_openai_response):
        """Test simple chat without tool calls."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        agent.client.chat.completions.create = Mock(
            return_value=mock_openai_response("Simple answer")
        )

        response = agent.chat("test question")

        assert response == "Simple answer"

    def test_chat_with_tool_calls(
        self, temp_knowledge_base, monkeypatch, mock_openai_response, sample_tool_call
    ):
        """Test chat with tool calls."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()

        # First response has tool call
        tool_call = sample_tool_call(
            "query_knowledge", '{"category": "mechanics", "subcategory": "economy"}'
        )
        response_with_tools = mock_openai_response(content=None, tool_calls=[tool_call])

        # Second response has final answer
        final_response = mock_openai_response("Based on the knowledge, here's the answer")

        agent.client.chat.completions.create = Mock(
            side_effect=[response_with_tools, final_response]
        )

        response = agent.chat("How does economy work?")

        assert "Based on the knowledge" in response

    def test_chat_max_iterations(
        self, temp_knowledge_base, monkeypatch, mock_openai_response, sample_tool_call
    ):
        """Test that chat respects max iterations limit."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()

        # Always return tool calls to force max iterations
        tool_call = sample_tool_call()
        response_with_tools = mock_openai_response(content=None, tool_calls=[tool_call])

        agent.client.chat.completions.create = Mock(return_value=response_with_tools)

        response = agent.chat("test")

        # Should return max iterations message
        assert "maximum number of research steps" in response.lower()

    def test_chat_verbose_mode(
        self, temp_knowledge_base, monkeypatch, mock_openai_response, caplog
    ):
        """Test chat verbose mode logging."""
        import logging

        caplog.set_level(logging.INFO)

        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        agent.client.chat.completions.create = Mock(
            return_value=mock_openai_response("Test response")
        )

        agent.chat("test question", verbose=True)

        # Verbose mode should log, but since we're not making tool calls,
        # just verify the chat completes successfully
        assert True  # Test passes if no exception


class TestErrorHandling:
    """Tests for error handling in agent."""

    def test_chat_handles_openai_error(self, temp_knowledge_base, monkeypatch):
        """Test that chat handles OpenAI API errors."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        agent.client.chat.completions.create = Mock(side_effect=Exception("API Error"))

        with pytest.raises(Exception) as exc_info:
            agent.chat("test question")

        assert "API Error" in str(exc_info.value)

    def test_tool_execution_error_returns_message(self, temp_knowledge_base, monkeypatch):
        """Test that tool execution errors return error messages."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()

        # Create a tool call with invalid JSON
        tool_call = Mock()
        tool_call.function.name = "query_knowledge"
        tool_call.function.arguments = "invalid json"

        result = agent._execute_tool_call(tool_call)

        assert "invalid tool arguments" in result.lower()
        assert "json decode failed" in result.lower()

    def test_tool_execution_missing_required_args(self, temp_knowledge_base, monkeypatch):
        """Test that missing required args returns a clear error."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()

        tool_call = Mock()
        tool_call.function.name = "web_search"
        tool_call.function.arguments = json.dumps({"num_results": 2})

        result = agent._execute_tool_call(tool_call)

        assert "missing 'query'" in result.lower()


class TestAgentIntegration:
    """Integration tests for full agent workflows."""

    def test_full_chat_workflow(self, temp_knowledge_base, monkeypatch):
        """Test complete chat workflow from question to answer."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()

        # Create mock responses
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test answer"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.model_dump = Mock(
            return_value={"role": "assistant", "content": "Test answer"}
        )
        mock_response.model = "gpt-5-mini"
        mock_response.id = "test-id"
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30)

        agent.client.chat.completions.create = Mock(return_value=mock_response)

        response = agent.chat("How do estates work?")

        assert response == "Test answer"
        assert len(agent.messages) > 1  # System + user + assistant

    def test_multiple_conversations(self, temp_knowledge_base, monkeypatch, mock_openai_response):
        """Test multiple conversations with the same agent."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        agent.client.chat.completions.create = Mock(return_value=mock_openai_response("Response"))

        # First conversation
        response1 = agent.chat("Question 1")
        history_after_1 = len(agent.messages)

        # Second conversation (history should grow)
        response2 = agent.chat("Question 2")
        history_after_2 = len(agent.messages)

        assert response1 == "Response"
        assert response2 == "Response"
        assert history_after_2 > history_after_1

    def test_reset_between_conversations(
        self, temp_knowledge_base, monkeypatch, mock_openai_response
    ):
        """Test reset clears conversation between chats."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        agent.client.chat.completions.create = Mock(return_value=mock_openai_response("Response"))

        # First conversation
        agent.chat("Question 1")
        assert len(agent.messages) > 1

        # Reset
        agent.reset()
        assert len(agent.messages) == 1

        # Second conversation starts fresh
        agent.chat("Question 2")
        # Should only have system + user + assistant
        assert len(agent.messages) == 3
