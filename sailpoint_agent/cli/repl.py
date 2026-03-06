"""Interactive REPL session manager using Claude Agent SDK."""

from rich.console import Console
from rich.prompt import Prompt

from sailpoint_agent.models.config import AppConfig

console = Console()


async def run_repl(config: AppConfig, verbose: bool = False):
    """Run interactive REPL session using ClaudeSDKClient for multi-turn conversation."""
    from sailpoint_agent.main import build_sdk_options
    from claude_agent_sdk import ClaudeSDKClient

    options = build_sdk_options(config)

    console.print("[bold blue]SailPoint Query AI Agent[/bold blue]")
    console.print("Type your questions about SailPoint IIQ, IDN, or ISC.")
    console.print(
        "Commands: [bold]/quit[/bold] to exit, [bold]/clear[/bold] to reset, "
        "[bold]/model <name>[/bold] to switch model\n"
    )

    async with ClaudeSDKClient(options=options) as client:
        while True:
            try:
                user_input = Prompt.ask("[bold green]You[/bold green]")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Goodbye![/yellow]")
                break

            if not user_input.strip():
                continue

            # Handle REPL commands
            if user_input.strip().startswith("/"):
                should_continue = _handle_command(user_input.strip(), config)
                if not should_continue:
                    break
                continue

            try:
                console.print()
                await client.query(user_input)
                async for message in client.receive_response():
                    if message.type == "assistant":
                        for block in message.content:
                            if hasattr(block, "text"):
                                console.print(block.text, end="")
                console.print()
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")


def _handle_command(cmd: str, config: AppConfig) -> bool:
    """Handle REPL commands. Returns True to continue, False to exit."""
    if cmd in ("/quit", "/exit", "/q"):
        console.print("[yellow]Goodbye![/yellow]")
        return False
    elif cmd == "/clear":
        console.print("[yellow]Conversation cleared. Start a new session.[/yellow]")
    elif cmd.startswith("/model "):
        new_model = cmd.split(" ", 1)[1].strip()
        config.llm.model = new_model
        console.print(f"[yellow]Switched to model: {new_model}[/yellow]")
    elif cmd == "/help":
        console.print("[bold]Commands:[/bold]")
        console.print("  /quit    - Exit the session")
        console.print("  /clear   - Clear conversation history")
        console.print("  /model   - Switch LLM model")
        console.print("  /help    - Show this help")
    else:
        console.print(f"[red]Unknown command: {cmd}[/red]")
    return True
