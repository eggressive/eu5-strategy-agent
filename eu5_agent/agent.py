"""
EU5 Strategy Agent

Main agent implementation using OpenAI API with function calling.
Integrates knowledge base and web search tools.
"""

import json
import os
from typing import List, Dict, Any, Optional

from openai import OpenAI

from .config import get_config, EU5Config
from .knowledge import EU5Knowledge
from .prompts import SYSTEM_PROMPT, TOOLS


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

        # Initialize message history
        self.messages: List[Dict[str, Any]] = []
        self.reset()

    def reset(self):
        """Reset the conversation history."""
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

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
            results = search_eu5_wiki(query, max_results=num_results)
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
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "query_knowledge":
            return self._query_knowledge(**arguments)
        elif function_name == "web_search":
            return self._web_search(**arguments)
        else:
            return f"Unknown tool: {function_name}"

    def chat(self, user_message: str, verbose: bool = False) -> str:
        """
        Send a message to the agent and get a response.

        Args:
            user_message: The user's question or prompt
            verbose: If True, print tool calls and intermediate steps

        Returns:
            The agent's response
        """
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        # Maximum iterations to prevent infinite loops
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call OpenAI API
            # Note: gpt-5-mini requires max_completion_tokens (not max_tokens)
            # and doesn't support temperature parameter (uses default=1)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            # Add assistant message to history
            self.messages.append(assistant_message.model_dump(exclude_unset=True))

            # Check if assistant wants to call tools
            if assistant_message.tool_calls:
                if verbose:
                    print(f"\n[Tool Calls: {len(assistant_message.tool_calls)}]")

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    if verbose:
                        print(f"  → {tool_call.function.name}({tool_call.function.arguments})")

                    # Execute the tool
                    tool_result = self._execute_tool_call(tool_call)

                    if verbose:
                        preview = tool_result[:200] + "..." if len(tool_result) > 200 else tool_result
                        print(f"  ✓ Result: {preview}")

                    # Add tool result to messages
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })

                # Continue loop to get final response after tool execution
                continue

            # No more tool calls - return final response
            if assistant_message.content:
                return assistant_message.content

            # Safety check
            if iteration >= max_iterations:
                return "Maximum iterations reached. Please try rephrasing your question."

        return "No response generated."

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
