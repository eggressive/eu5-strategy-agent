"""
EU5 Strategy Agent CLI

Beautiful command-line interface using Rich for formatting.
"""

import argparse
import os
import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print as rprint

from .agent import EU5Agent


console = Console()


def print_banner():
    """Print a nice banner for the CLI."""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                   EU5 STRATEGY ADVISOR                            ║
║                  Standalone Edition v1.0                          ║
╚═══════════════════════════════════════════════════════════════════╝

Expert strategic guidance for Europa Universalis 5 (1337-1837)
Powered by GPT-5-Mini with comprehensive knowledge base coverage
"""
    console.print(banner, style="bold cyan")


def print_help():
    """Print help information about the CLI."""
    help_text = """
**Available Commands:**
- Type your EU5 strategy question to get advice
- `reset` - Start a new conversation
- `help` - Show this help message
- `quit` or `exit` - Exit the program

**Example Questions:**
- "How do estates work in EU5?"
- "What are the best opening moves for England?"
- "I'm new to EU5. Which nation should I start with?"
- "How does the market system work?"
- "What are common beginner mistakes?"
"""
    console.print(Panel(Markdown(help_text), title="Help", border_style="green"))


def run_interactive(agent: EU5Agent):
    """
    Run the agent in interactive mode with rich formatting.

    Args:
        agent: The EU5Agent instance
    """
    print_banner()
    print_help()

    console.print("\n[bold green]Ready![/bold green] Ask me anything about EU5 strategy.\n")

    try:
        while True:
            # Get user input
            user_input = Prompt.ask("[bold yellow]You[/bold yellow]").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print("\n[bold cyan]Goodbye! May your empire prosper![/bold cyan]\n")
                break

            if user_input.lower() == 'reset':
                agent.reset()
                console.print("\n[dim]Conversation reset[/dim]\n")
                continue

            if user_input.lower() == 'help':
                print_help()
                continue

            # Show thinking indicator
            with console.status("[bold green]Analyzing your question...", spinner="dots"):
                try:
                    response = agent.chat(user_input, verbose=False)
                except Exception as e:
                    console.print(f"\n[bold red]Error:[/bold red] {str(e)}\n")
                    continue

            # Display response with markdown formatting
            console.print()
            console.print(Panel(
                Markdown(response),
                title="[bold cyan]EU5 Strategy Advisor[/bold cyan]",
                border_style="cyan"
            ))
            console.print()

    except KeyboardInterrupt:
        console.print("\n\n[bold cyan]Goodbye! May your empire prosper![/bold cyan]\n")
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error:[/bold red] {e}\n")
        raise


def run_single_query(agent: EU5Agent, query: str, verbose: bool = False):
    """
    Run a single query and display the response.

    Args:
        agent: The EU5Agent instance
        query: The user's question
        verbose: Show tool calls and intermediate steps
    """
    print_banner()

    console.print(f"[bold yellow]Query:[/bold yellow] {query}\n")

    # Get response
    try:
        with console.status("[bold green]Analyzing your question...", spinner="dots"):
            response = agent.chat(query, verbose=verbose)

        # Display response
        console.print()
        console.print(Panel(
            Markdown(response),
            title="[bold cyan]EU5 Strategy Advisor[/bold cyan]",
            border_style="cyan"
        ))
        console.print()

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}\n")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="EU5 Strategy Advisor - Expert strategic guidance for Europa Universalis 5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python -m eu5_standalone.cli

  # Single query
  python -m eu5_standalone.cli --query "How do estates work?"

  # Verbose mode (show tool calls)
  python -m eu5_standalone.cli --query "England opening" --verbose

Environment Variables:
  OPENAI_API_KEY     Your OpenAI API key (required)
  OPENAI_MODEL       Model to use (default: gpt-5-mini)
  EU5_KNOWLEDGE_PATH Path to knowledge base (default: /home/dimitar/ai/eu5_agent)
        """
    )

    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Single query mode - ask a question and exit"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show tool calls and intermediate steps"
    )

    parser.add_argument(
        "-m", "--model",
        type=str,
        default=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        help="OpenAI model to use (default: gpt-5-mini)"
    )

    args = parser.parse_args()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Error:[/bold red] OPENAI_API_KEY environment variable not set!")
        console.print("\nPlease set your OpenAI API key:")
        console.print("  export OPENAI_API_KEY='your-api-key-here'\n")
        console.print("Or create a .env file with:")
        console.print("  OPENAI_API_KEY=your-api-key-here\n")
        sys.exit(1)

    # Initialize agent
    try:
        agent = EU5Agent(model=args.model)
    except Exception as e:
        console.print(f"[bold red]Failed to initialize agent:[/bold red] {e}")
        sys.exit(1)

    # Run in appropriate mode
    if args.query:
        run_single_query(agent, args.query, verbose=args.verbose)
    else:
        run_interactive(agent)


if __name__ == "__main__":
    main()
