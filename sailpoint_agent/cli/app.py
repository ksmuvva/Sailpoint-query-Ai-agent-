"""CLI interface using Claude Agent SDK for the agentic loop.

Uses SDK's query() for single questions and ClaudeSDKClient for interactive chat.
The SDK handles ReAct reasoning, tool execution, subagent delegation, and Skill
invocation automatically.
"""

import asyncio

import click
from rich.console import Console

from sailpoint_agent.config.settings import load_config
from sailpoint_agent.main import run_single_query
from sailpoint_agent.cli.repl import run_repl

console = Console()


@click.group()
@click.option("--model", default=None, help="LLM model to use (e.g., claude-sonnet-4-20250514, gpt-4)")
@click.option("--verbose", is_flag=True, help="Show ReAct reasoning traces")
@click.option("--config", "config_path", default="config.yaml", help="Path to config file")
@click.pass_context
def cli(ctx, model, verbose, config_path):
    """SailPoint Query AI Agent - Your intelligent SailPoint assistant."""
    ctx.ensure_object(dict)
    app_config = load_config(config_path)
    if model:
        app_config.llm.model = model
    ctx.obj["config"] = app_config
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("question")
@click.option("--output", "-o", default=None, help="Save response to file")
@click.pass_context
def query(ctx, question, output):
    """Ask a single question about SailPoint.

    Uses SDK's stateless query() — the SDK manages the full ReAct loop,
    tool usage, Skill invocation, and subagent delegation automatically.
    """
    app_config = ctx.obj["config"]

    async def _run():
        with console.status("[bold blue]Thinking...[/bold blue]"):
            result = await run_single_query(question, app_config)
        console.print()
        console.print(result)
        if output:
            with open(output, "w") as f:
                f.write(result)
            console.print(f"\n[green]Response saved to {output}[/green]")

    asyncio.run(_run())


@cli.command()
@click.pass_context
def chat(ctx):
    """Start an interactive chat session.

    Uses SDK's ClaudeSDKClient for stateful multi-turn conversations.
    """
    app_config = ctx.obj["config"]
    verbose = ctx.obj["verbose"]
    asyncio.run(run_repl(app_config, verbose=verbose))


if __name__ == "__main__":
    cli()
