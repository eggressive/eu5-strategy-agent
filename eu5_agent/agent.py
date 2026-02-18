"""
EU5 Strategy Agent

Main agent implementation using OpenAI API with function calling.
Integrates knowledge base and web search tools.
"""

import json
import logging
import re
from typing import List, Optional, cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from .config import get_config, EU5Config
from .knowledge import EU5Knowledge
from .prompts import SYSTEM_PROMPT, TOOLS

# Set up logger for this module
logger = logging.getLogger(__name__)


class EU5Agent:
    """
    EU5 Strategy Advisor Agent using OpenAI with function calling.

    Provides expert strategic guidance by:
    1. Querying local knowledge base (primary)
    2. Falling back to web search when needed
    3. Synthesizing information into actionable advice
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        knowledge_path: Optional[str] = None,
        config: Optional[EU5Config] = None
    ):
        """
        Initialize the EU5 strategy agent.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var, or use config)
            model: OpenAI model to use (or set OPENAI_MODEL env var, or use config)
            knowledge_path: Path to knowledge base (or set EU5_KNOWLEDGE_PATH, or use config)
            config: EU5Config instance (optional, will load from env if not provided)
        """
        # Load configuration (supports .env files and environment variables)
        if config is None:
            config = get_config()

        # Allow parameters to override config
        self.api_key = api_key or config.api_key
        self.model = model or config.model

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment "
                "variable or pass api_key parameter."
            )

        # Initialize OpenAI client with base_url from config
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=config.base_url
        )

        # Initialize knowledge base
        kb_path = knowledge_path or config.knowledge_path
        self.knowledge = EU5Knowledge(kb_path)

        # Store config reference for model-specific behavior
        self.config = config
        self.max_history_messages = config.max_history_messages

        # Initialize message history with proper OpenAI types
        self.messages: List[ChatCompletionMessageParam] = []
        self.reset()

    def reset(self):
        """Reset the conversation history."""
        self.messages = [
            cast(ChatCompletionMessageParam, {"role": "system", "content": SYSTEM_PROMPT})
        ]

    def _trim_messages(self):
        """Trim conversation history to stay within max_history_messages.

        Removes complete turn groups (a user message plus all subsequent
        assistant/tool messages until the next user message) from the oldest
        end of the history.  The system prompt at index 0 and the most recent
        turn group are never dropped.
        """
        if len(self.messages) <= self.max_history_messages:
            return

        # Find turn-group boundaries: indices where role == "user"
        user_indices = [
            i for i, m in enumerate(self.messages) if m.get("role") == "user"
        ]

        if len(user_indices) <= 1:
            # Only one turn group (or none) — nothing safe to drop
            return

        # Try dropping oldest turn groups until we're within the limit.
        # Never drop the last turn group (the current question).
        for cut in range(1, len(user_indices)):
            # Keep system prompt + everything from user_indices[cut] onward
            remaining = [self.messages[0]] + self.messages[user_indices[cut]:]
            if len(remaining) <= self.max_history_messages:
                dropped = len(self.messages) - len(remaining)
                self.messages = remaining
                logger.warning(
                    "Trimmed %d old messages to stay within history limit (%d)",
                    dropped,
                    self.max_history_messages,
                )
                return

        # Even dropping all but the last turn group isn't enough — do it anyway
        # to avoid unbounded growth.
        remaining = [self.messages[0]] + self.messages[user_indices[-1]:]
        dropped = len(self.messages) - len(remaining)
        self.messages = remaining
        logger.warning(
            "Trimmed %d old messages to stay within history limit (%d)",
            dropped,
            self.max_history_messages,
        )

    def _query_knowledge(self, category: str, subcategory: Optional[str] = None) -> str:
        """
        Tool function: Query the knowledge base.

        Args:
            category: Knowledge category
            subcategory: Specific subcategory (optional)

        Returns:
            Formatted knowledge content or error message
        """
        result = self.knowledge.get_knowledge(category, subcategory)

        if result["status"] == "success":
            return f"**Source: Local Knowledge Base ({result['source']})**\n\n{result['content']}"
        elif result["status"] == "list":
            return result["content"]
        else:
            return f"Error: {result['error']}"

    def _web_search(self, query: str, num_results: int = 3) -> str:
        """
        Tool function: Search the web for EU5 information.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            Formatted search results
        """
        # Import here to avoid circular dependency
        from .search import search_eu5_wiki

        try:
            results = search_eu5_wiki(query, max_results=num_results, api_key=self.config.tavily_api_key)
            if not results:
                return f"No results found for: {query}"

            output = f"**Source: Web Search** (Query: {query})\n\n"
            for i, result in enumerate(results, 1):
                output += f"{i}. **{result['title']}**\n"
                output += f"   URL: {result['url']}\n"
                if result.get('snippet'):
                    output += f"   {result['snippet']}\n"
                output += "\n"

            return output

        except Exception as e:
            return f"Web search error: {str(e)}"

    def _execute_tool_call(self, tool_call) -> str:
        """
        Execute a tool call from OpenAI.

        Args:
            tool_call: Tool call object from OpenAI

        Returns:
            Tool execution result as string
        """
        # Type checker has incomplete stubs for tool_call.function
        function_name = tool_call.function.name  # type: ignore[attr-defined]

        try:
            arguments = json.loads(tool_call.function.arguments)  # type: ignore[attr-defined]
        except json.JSONDecodeError as exc:
            return f"Error: invalid tool arguments (JSON decode failed: {exc})"

        # Basic validation per tool to avoid KeyError and provide clear errors
        if function_name == "query_knowledge":
            if not isinstance(arguments, dict) or "category" not in arguments:
                return "Error: invalid tool arguments (missing 'category' for query_knowledge)"
            if not isinstance(arguments.get("category"), str):
                return "Error: invalid tool arguments ('category' must be a string)"
            if arguments.get("subcategory") is not None and not isinstance(arguments.get("subcategory"), str):
                return "Error: invalid tool arguments ('subcategory' must be a string if provided)"
            return self._query_knowledge(**arguments)
        elif function_name == "web_search":
            if not isinstance(arguments, dict) or "query" not in arguments:
                return "Error: invalid tool arguments (missing 'query' for web_search)"
            if not isinstance(arguments.get("query"), str):
                return "Error: invalid tool arguments ('query' must be a string)"
            if arguments.get("num_results") is not None and not isinstance(arguments.get("num_results"), int):
                return "Error: invalid tool arguments ('num_results' must be an integer if provided)"
            return self._web_search(**arguments)
        else:
            return f"Unknown tool: {function_name}"

    @staticmethod
    def _is_complex_query(user_message: str) -> bool:
        """Heuristic to identify multi-constraint or long-horizon requests."""
        lower = user_message.lower()

        complex_signals = [
            "long-term",
            "long term",
            "mid game",
            "late game",
            "campaign",
            "roadmap",
            "plan",
            "trade-off",
            "tradeoff",
            "optimize",
            "contingency",
            "fallback",
            "if ",
            "risk",
            "timeline",
            "5 year",
            "10 year",
            "15 year",
            "30 year",
        ]

        signal_count = sum(1 for s in complex_signals if s in lower)
        separators = len(re.findall(r"\b(and|while|versus|vs\.?|with)\b", lower))
        punctuation_split = lower.count(",") + lower.count(";")
        long_message = len(lower.split()) >= 20

        return signal_count >= 2 or separators >= 2 or punctuation_split >= 2 or long_message

    @staticmethod
    def _complex_mode_instruction() -> str:
        """Runtime instruction injected as a temporary system message."""
        return (
            "[Complex Query Mode Enabled]\n"
            "Treat this as a campaign-level planning question. "
            "If critical context is missing, ask up to 3 clarifying questions first. "
            "Otherwise respond with: Situation Snapshot, Objectives (Short/Mid/Long), "
            "Phased Plan (Immediate/5-year/10+ year), Risk Matrix, Pivot Triggers, "
            "and First 3 Actions. Include conservative and aggressive alternatives."
        )

    def chat(self, user_message: str, verbose: bool = False) -> str:
        """
        Send a message to the agent and get a response.

        Args:
            user_message: The user's question or prompt
            verbose: If True, print tool calls and intermediate steps

        Returns:
            The agent's response
        """
        # Add raw user message to history
        is_complex_query = self._is_complex_query(user_message)
        self.messages.append(cast(ChatCompletionMessageParam, {
            "role": "user",
            "content": user_message
        }))

        # Maximum iterations to prevent infinite loops
        # Set to 10 to allow complex queries requiring multiple tool calls
        # (web search + knowledge base lookups typically need 6-8 iterations)
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Trim history before each API call to stay within limits
            self._trim_messages()

            # Call OpenAI API
            # Build params conditionally based on the effective model
            request_messages: List[ChatCompletionMessageParam] = list(self.messages)
            if is_complex_query:
                complex_mode_message = cast(ChatCompletionMessageParam, {
                    "role": "system",
                    "content": self._complex_mode_instruction(),
                })
                request_messages = [request_messages[0], complex_mode_message, *request_messages[1:]]

            api_params: dict = {
                "model": self.model,
                "messages": request_messages,
                "tools": TOOLS,
                "tool_choice": "auto",
            }
            if EU5Config.uses_max_completion_tokens(self.model):
                api_params["max_completion_tokens"] = self.config.max_completion_tokens
            if EU5Config.supports_temperature(self.model):
                api_params["temperature"] = self.config.temperature
            response = self.client.chat.completions.create(**api_params)

            assistant_message = response.choices[0].message

            # Add assistant message to history
            # Use cast() since model_dump() returns dict[str, Any] but we know it matches
            self.messages.append(cast(ChatCompletionMessageParam, assistant_message.model_dump(exclude_unset=True)))

            # Check if assistant wants to call tools
            if assistant_message.tool_calls:
                if verbose:
                    logger.info(f"\n[Tool Calls: {len(assistant_message.tool_calls)}]")

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    if verbose:
                        # Type checker has incomplete stubs for tool_call.function
                        logger.info(f"  → {tool_call.function.name}({tool_call.function.arguments})")  # type: ignore[attr-defined]

                    # Execute the tool
                    tool_result = self._execute_tool_call(tool_call)

                    if verbose:
                        preview = tool_result[:200] + "..." if len(tool_result) > 200 else tool_result
                        logger.info(f"  ✓ Result: {preview}")

                    # Add tool result to messages
                    self.messages.append(cast(ChatCompletionMessageParam, {
                        "role": "tool",
                        "tool_call_id": tool_call.id,  # type: ignore[attr-defined]
                        "content": tool_result
                    }))

                # Continue loop to get final response after tool execution
                continue

            # No more tool calls - return final response
            if assistant_message.content:
                return assistant_message.content

        # Reached max iterations or no content generated
        return (
            "I've reached the maximum number of research steps for this query. "
            "This usually happens with very complex questions. "
            "Try asking a more specific question, or break it into smaller parts."
        )

    def interactive(self):
        """
        Start an interactive conversation session.
        Type 'quit', 'exit', or press Ctrl+C to end.
        """
        print("="*70)
        print("EU5 STRATEGY ADVISOR - Interactive Mode")
        print("="*70)
        print("Ask me anything about EU5 strategy!")
        print("Type 'quit' or 'exit' to end the session.")
        print()

        try:
            while True:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! May your empire prosper!")
                    break

                # Special command to reset conversation
                if user_input.lower() == 'reset':
                    self.reset()
                    print("\n[Conversation reset]\n")
                    continue

                # Get response
                print()
                response = self.chat(user_input, verbose=True)
                print(f"\nAgent: {response}\n")
                print("-"*70)

        except KeyboardInterrupt:
            print("\n\nGoodbye! May your empire prosper!")


# Quick test
if __name__ == "__main__":
    import sys

    # Test the agent
    agent = EU5Agent()

    if len(sys.argv) > 1:
        # Command line query
        query = " ".join(sys.argv[1:])
        print(f"Query: {query}\n")
        response = agent.chat(query, verbose=True)
        print(f"\nResponse:\n{response}")
    else:
        # Interactive mode
        agent.interactive()
