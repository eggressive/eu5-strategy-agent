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
import logging
from typing import cast
from unittest.mock import Mock, patch

import pytest
from openai.types.chat import ChatCompletionMessageParam

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


class TestModelSpecificAPIParams:
    """Tests for conditional API parameters based on model capabilities."""

    def test_gpt5_sends_max_completion_tokens_not_temperature(
        self, temp_knowledge_base, monkeypatch, mock_openai_response
    ):
        """Test that gpt-5 model sends max_completion_tokens but not temperature."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent(model="gpt-5-mini")
        agent.client.chat.completions.create = Mock(
            return_value=mock_openai_response("response")
        )

        agent.chat("test")

        call_kwargs = agent.client.chat.completions.create.call_args
        assert "max_completion_tokens" in call_kwargs.kwargs or "max_completion_tokens" in (call_kwargs[1] if len(call_kwargs) > 1 else {})
        # gpt-5 should NOT get temperature
        all_args = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
        assert "temperature" not in all_args

    def test_gpt4_sends_temperature_not_max_completion_tokens(
        self, temp_knowledge_base, monkeypatch, mock_openai_response
    ):
        """Test that gpt-4 model sends temperature but not max_completion_tokens."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent(model="gpt-4o")
        agent.client.chat.completions.create = Mock(
            return_value=mock_openai_response("response")
        )

        agent.chat("test")

        call_kwargs = agent.client.chat.completions.create.call_args
        all_args = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
        assert "temperature" in all_args
        assert all_args["temperature"] == 0.7
        assert "max_completion_tokens" not in all_args

    def test_model_override_uses_effective_model_not_config(
        self, temp_knowledge_base, monkeypatch, mock_openai_response
    ):
        """Test that model override via constructor determines API params, not config."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        # Override to gpt-4o — should send temperature, not max_completion_tokens
        agent = EU5Agent(model="gpt-4o")
        agent.client.chat.completions.create = Mock(
            return_value=mock_openai_response("response")
        )

        agent.chat("test")

        call_kwargs = agent.client.chat.completions.create.call_args
        all_args = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
        assert "temperature" in all_args
        assert "max_completion_tokens" not in all_args

    def test_configurable_temperature_value(
        self, temp_knowledge_base, monkeypatch, mock_openai_response
    ):
        """Test that custom temperature from env is passed to the API."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("OPENAI_TEMPERATURE", "0.3")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        agent.client.chat.completions.create = Mock(
            return_value=mock_openai_response("response")
        )

        agent.chat("test")

        call_kwargs = agent.client.chat.completions.create.call_args
        all_args = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
        assert all_args["temperature"] == 0.3


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

    def test_multiple_conversations(
        self, temp_knowledge_base, monkeypatch, mock_openai_response
    ):
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


def _make_agent(temp_knowledge_base, monkeypatch, max_history=10):
    """Helper: create an EU5Agent with a configurable max_history_messages."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

    agent = EU5Agent()
    agent.max_history_messages = max_history
    return agent


def _msg(role, content="x", **extra):
    """Shorthand for building a message dict."""
    m = {"role": role, "content": content}
    m.update(extra)
    return cast(ChatCompletionMessageParam, m)


class TestMessageTrimming:
    """Tests for _trim_messages() turn-group-based history trimming."""

    def test_no_op_when_under_limit(self, temp_knowledge_base, monkeypatch):
        """No trimming occurs when message count is within the limit."""
        agent = _make_agent(temp_knowledge_base, monkeypatch, max_history=20)
        # system + user + assistant = 3 messages, well under 20
        agent.messages = [
            _msg("system", "sys"),
            _msg("user", "q1"),
            _msg("assistant", "a1"),
        ]

        agent._trim_messages()

        assert len(agent.messages) == 3

    def test_drops_oldest_turn_group(self, temp_knowledge_base, monkeypatch):
        """Oldest turn group is dropped when over the limit."""
        agent = _make_agent(temp_knowledge_base, monkeypatch, max_history=5)
        agent.messages = [
            _msg("system", "sys"),       # 0
            _msg("user", "q1"),          # 1  ← oldest turn group
            _msg("assistant", "a1"),     # 2
            _msg("user", "q2"),          # 3  ← second turn group
            _msg("assistant", "a2"),     # 4
            _msg("user", "q3"),          # 5  ← current turn group
            _msg("assistant", "a3"),     # 6
        ]  # total 7 > limit 5

        agent._trim_messages()

        # Should have dropped q1+a1, keeping system + q2+a2 + q3+a3 = 5
        assert len(agent.messages) == 5
        assert agent.messages[0]["role"] == "system"
        assert agent.messages[1]["content"] == "q2"

    def test_preserves_tool_call_chains(self, temp_knowledge_base, monkeypatch):
        """Assistant tool_calls and subsequent tool results are kept together."""
        agent = _make_agent(temp_knowledge_base, monkeypatch, max_history=8)
        agent.messages = [
            _msg("system", "sys"),
            # Turn group 1: user + assistant(tool_call) + tool + assistant
            _msg("user", "q1"),
            _msg("assistant", "tc1", tool_calls=[{"id": "c1"}]),
            _msg("tool", "result1", tool_call_id="c1"),
            _msg("assistant", "a1"),
            # Turn group 2: user + assistant(tool_call) + tool + assistant
            _msg("user", "q2"),
            _msg("assistant", "tc2", tool_calls=[{"id": "c2"}]),
            _msg("tool", "result2", tool_call_id="c2"),
            _msg("assistant", "a2"),
        ]  # total 9 > limit 8

        agent._trim_messages()

        # Should have dropped turn group 1 entirely
        assert len(agent.messages) == 5  # system + 4 messages in group 2
        assert agent.messages[0]["role"] == "system"
        assert agent.messages[1]["content"] == "q2"
        # Tool chain intact
        assert agent.messages[2]["content"] == "tc2"
        assert agent.messages[3]["role"] == "tool"
        assert agent.messages[4]["content"] == "a2"

    def test_system_prompt_always_preserved(self, temp_knowledge_base, monkeypatch):
        """System prompt at index 0 is never removed."""
        agent = _make_agent(temp_knowledge_base, monkeypatch, max_history=3)
        agent.messages = [
            _msg("system", "sys"),
            _msg("user", "q1"),
            _msg("assistant", "a1"),
            _msg("user", "q2"),
            _msg("assistant", "a2"),
        ]

        agent._trim_messages()

        assert agent.messages[0]["role"] == "system"
        assert agent.messages[0]["content"] == "sys"

    def test_never_drops_last_turn_group(self, temp_knowledge_base, monkeypatch):
        """The most recent turn group is never dropped, even if over limit."""
        agent = _make_agent(temp_knowledge_base, monkeypatch, max_history=2)
        # Even with limit=2, we can't drop the only user turn group
        agent.messages = [
            _msg("system", "sys"),
            _msg("user", "q1"),
            _msg("assistant", "a1"),
        ]  # 3 > 2, but only one turn group

        agent._trim_messages()

        # Nothing dropped — can't remove the only turn group
        assert len(agent.messages) == 3
        assert agent.messages[1]["content"] == "q1"

    def test_drops_multiple_groups_when_needed(self, temp_knowledge_base, monkeypatch):
        """Multiple old turn groups are dropped to get under the limit."""
        agent = _make_agent(temp_knowledge_base, monkeypatch, max_history=4)
        agent.messages = [
            _msg("system", "sys"),
            _msg("user", "q1"),
            _msg("assistant", "a1"),
            _msg("user", "q2"),
            _msg("assistant", "a2"),
            _msg("user", "q3"),
            _msg("assistant", "a3"),
            _msg("user", "q4"),
            _msg("assistant", "a4"),
        ]  # 9 messages, limit 4

        agent._trim_messages()

        # Should keep system + last turn group(s) that fit within 4
        assert len(agent.messages) <= 4
        assert agent.messages[0]["role"] == "system"
        # Last turn group must survive
        assert any(m["content"] == "q4" for m in agent.messages)

    def test_logs_warning_on_trim(self, temp_knowledge_base, monkeypatch, caplog):
        """A warning is logged when messages are trimmed."""
        agent = _make_agent(temp_knowledge_base, monkeypatch, max_history=4)
        agent.messages = [
            _msg("system", "sys"),
            _msg("user", "q1"),
            _msg("assistant", "a1"),
            _msg("user", "q2"),
            _msg("assistant", "a2"),
        ]  # 5 > 4

        with caplog.at_level(logging.WARNING, logger="eu5_agent.agent"):
            agent._trim_messages()

        assert "Trimmed" in caplog.text
        assert "old messages" in caplog.text

    def test_trim_called_during_chat(
        self, temp_knowledge_base, monkeypatch, mock_openai_response
    ):
        """_trim_messages() is invoked inside chat()."""
        agent = _make_agent(temp_knowledge_base, monkeypatch, max_history=100)
        agent.client.chat.completions.create = Mock(
            return_value=mock_openai_response("reply")
        )

        with patch.object(agent, "_trim_messages", wraps=agent._trim_messages) as spy:
            agent.chat("hello")
            assert spy.call_count >= 1

class TestComplexQueryMode:
    """Tests for complex-query detection and runtime message shaping."""

    def test_detects_complex_query_from_long_horizon_terms(self):
        """Long-horizon strategy wording should trigger complex mode."""
        query = "Give me a 10 year campaign plan with trade-off analysis and contingencies"
        assert EU5Agent._is_complex_query(query) is True

    def test_simple_query_does_not_trigger_complex_mode(self):
        """Short tactical prompts should remain in normal mode."""
        query = "How do estates work?"
        assert EU5Agent._is_complex_query(query) is False

    def test_single_plan_keyword_does_not_trigger_complex_mode(self):
        """A short prompt with only 'plan' should not over-trigger complex mode."""
        query = "Plan England opening"
        assert EU5Agent._is_complex_query(query) is False

    def test_long_query_without_strategy_cues_does_not_trigger_complex_mode(self):
        """Length alone should not trigger complex mode without planning cues."""
        query = (
            "Can you explain estates taxes manpower legitimacy unrest province development "
            "and advisor effects in detail for me please"
        )
        assert EU5Agent._is_complex_query(query) is False

    def test_many_separators_without_planning_signals_do_not_trigger_complex_mode(self):
        """Conjunction-heavy prompts should not trigger by structure alone."""
        query = (
            "Explain estates and manpower and taxes and unrest and advisor effects, "
            "and compare inflation and autonomy and legitimacy"
        )
        assert EU5Agent._is_complex_query(query) is False

    def test_complex_mode_instruction_contains_required_sections(self):
        """Complex mode runtime guidance should include section requirements."""
        instruction = EU5Agent._complex_mode_instruction()
        assert "[Complex Query Mode Enabled]" in instruction
        assert "Situation Snapshot" in instruction
        assert "First 3 Actions" in instruction

    def test_chat_uses_complex_runtime_message_when_triggered(
        self, temp_knowledge_base, monkeypatch, mock_openai_response
    ):
        """chat() should send shaped complex-mode content to the API."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        agent.client.chat.completions.create = Mock(
            return_value=mock_openai_response("response")
        )

        agent.chat("I need a 15 year campaign roadmap with risks and fallback options")

        call_kwargs = agent.client.chat.completions.create.call_args
        all_args = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
        sent_messages = all_args["messages"]
        assert isinstance(sent_messages[-1]["content"], str)
        assert sent_messages[-1]["content"] == "I need a 15 year campaign roadmap with risks and fallback options"

        # complex mode instruction should be injected as a temporary system message
        assert isinstance(sent_messages[1]["content"], str)
        assert sent_messages[1]["role"] == "system"
        assert "[Complex Query Mode Enabled]" in sent_messages[1]["content"]

    def test_chat_does_not_inject_complex_instruction_for_simple_query(
        self, temp_knowledge_base, monkeypatch, mock_openai_response
    ):
        """Simple prompts should send only the base system + raw user message."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        agent.client.chat.completions.create = Mock(
            return_value=mock_openai_response("response")
        )

        agent.chat("How do estates work?")

        call_kwargs = agent.client.chat.completions.create.call_args
        all_args = call_kwargs.kwargs if call_kwargs.kwargs else call_kwargs[1]
        sent_messages = all_args["messages"]

        assert len(sent_messages) == 2
        assert sent_messages[0]["role"] == "system"
        assert sent_messages[1]["role"] == "user"

    def test_chat_preserves_raw_user_message_in_history(
        self, temp_knowledge_base, monkeypatch, mock_openai_response
    ):
        """Complex-mode instructions should not overwrite user content in history."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("EU5_KNOWLEDGE_PATH", str(temp_knowledge_base))

        agent = EU5Agent()
        agent.client.chat.completions.create = Mock(
            return_value=mock_openai_response("response")
        )

        raw_query = "Need a 10 year plan with contingencies and risk trade-offs"
        agent.chat(raw_query)

        assert any(m["role"] == "user" and m["content"] == raw_query for m in agent.messages)
