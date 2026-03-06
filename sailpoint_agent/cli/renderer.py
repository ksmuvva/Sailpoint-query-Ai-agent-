"""Rich console markdown renderer for agent responses."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

from sailpoint_agent.models.response import AgentResponse


def render_response(
    console: Console,
    response: AgentResponse,
    show_traces: bool = False,
) -> None:
    """Render an agent response to the terminal with rich formatting."""

    # Show reasoning traces if requested
    if show_traces and response.reasoning_trace:
        console.print("\n[dim]--- Reasoning Trace ---[/dim]")
        for step in response.reasoning_trace:
            console.print(f"[dim]  Step {step.step_number}:[/dim]")
            console.print(f"[dim]    Think: {step.thought[:200]}[/dim]")
            if step.action:
                console.print(f"[dim]    Act: {step.action}[/dim]")
            if step.observation:
                console.print(f"[dim]    Observe: {step.observation[:200]}[/dim]")
        console.print("[dim]----------------------[/dim]\n")

    # Main answer
    console.print(Markdown(response.answer))

    # Code blocks with syntax highlighting
    for block in response.code_blocks:
        console.print()
        if block.description:
            console.print(f"[bold]{block.description}[/bold]")
        syntax = Syntax(block.code, block.language, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=block.filename or block.language))

    # Citations
    if response.citations:
        console.print("\n[bold]Sources:[/bold]")
        for i, cite in enumerate(response.citations, 1):
            console.print(f"  [{i}] {cite.title} -- {cite.url}")

    # Metadata
    if response.model_used or response.tokens_used:
        console.print(
            f"\n[dim]Model: {response.model_used} | "
            f"Tokens: {response.tokens_used} | "
            f"Time: {response.response_time_ms}ms[/dim]"
        )
