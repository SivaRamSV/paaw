"""
PAAW CLI

Main command-line interface for interacting with PAAW.
"""

import asyncio
from datetime import datetime

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from paaw import __version__
from paaw.agent import Agent
from paaw.config import settings
from paaw.models import Channel, UnifiedMessage

app = typer.Typer(
    name="paaw",
    help="🐾 PAAW - Personal AI Assistant that Works",
    no_args_is_help=True,
)
console = Console()


def print_banner():
    """Print the PAAW welcome banner."""
    banner = """
[bold cyan]
    ██████╗  █████╗  █████╗ ██╗    ██╗
    ██╔══██╗██╔══██╗██╔══██╗██║    ██║
    ██████╔╝███████║███████║██║ █╗ ██║
    ██╔═══╝ ██╔══██║██╔══██║██║███╗██║
    ██║     ██║  ██║██║  ██║╚███╔███╔╝
    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝
[/bold cyan]
[dim]Personal AI Assistant that Works 🐾[/dim]
"""
    console.print(banner)


@app.command()
def chat():
    """
    Start an interactive chat session with PAAW.

    Type your messages and press Enter. Use Ctrl+C to exit.
    """
    print_banner()
    console.print(
        Panel(
            "[green]PAAW is ready![/green] Type your message and press Enter.\n"
            "[dim]Commands: /clear (clear history), /quit (exit)[/dim]",
            title="🐾 Chat",
            border_style="cyan",
        )
    )

    # Run async chat loop
    asyncio.run(_chat_loop())


def _configure_cli_logging():
    """Suppress noisy logs in CLI mode - only show warnings and errors."""
    import logging
    import structlog
    
    # Suppress debug/info logs in CLI - they clutter the chat output
    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("paaw").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    
    # Reconfigure structlog to not output to console
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,
    )


async def _chat_loop():
    """Async chat loop."""
    # Suppress logs for cleaner CLI output
    _configure_cli_logging()
    
    agent = Agent()
    
    # Initialize mental model
    try:
        await agent.initialize()
        console.print("[dim]Mental model connected.[/dim]")
    except Exception as e:
        console.print(f"[yellow]Note: Running without mental model ({e})[/yellow]")

    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")

            if not user_input.strip():
                continue

            # Handle commands
            if user_input.strip().lower() in ["/quit", "/exit", "/q"]:
                console.print("\n[dim]Goodbye! 🐾[/dim]")
                break

            if user_input.strip().lower() == "/clear":
                agent.clear_history()
                console.print("[dim]Conversation cleared.[/dim]")
                continue

            if user_input.strip().lower() == "/help":
                console.print(
                    Panel(
                        "/clear - Clear conversation history\n"
                        "/memory - Show mental model\n"
                        "/quit - Exit chat\n"
                        "/help - Show this help",
                        title="Commands",
                        border_style="dim",
                    )
                )
                continue
            
            if user_input.strip().lower() == "/memory":
                if agent.db:
                    stats = await agent.db.get_stats()
                    user = await agent.db.get_user_node("user_default")
                    root_nodes = await agent.db.get_root_nodes("user_default")
                    
                    mem_info = f"[bold]Graph Stats:[/bold]\n"
                    for k, v in stats.items():
                        mem_info += f"  {k}: {v}\n"
                    
                    if user:
                        mem_info += f"\n[bold]User:[/bold] {user.label}\n"
                        mem_info += f"  Context: {user.context[:100] if user.context else 'No context'}...\n"
                    
                    if root_nodes:
                        mem_info += f"\n[bold]Root Nodes ({len(root_nodes)}):[/bold]\n"
                        for node in root_nodes:
                            mem_info += f"  • {node.type.value}: {node.label}\n"
                    
                    console.print(Panel(mem_info, title="🧠 Mental Model", border_style="cyan"))
                else:
                    console.print("[yellow]Mental model not connected[/yellow]")
                continue

            # Create unified message
            message = UnifiedMessage(
                channel=Channel.CLI,
                user_id=settings.default_user_id,
                content=user_input,
                timestamp=datetime.utcnow(),
            )

            # Get response with streaming
            console.print("\n[bold cyan]PAAW[/bold cyan]", end=" ")

            full_response = ""
            async for chunk in agent.process_stream(message):
                console.print(chunk, end="")
                full_response += chunk

            console.print()  # New line after response

        except KeyboardInterrupt:
            console.print("\n\n[dim]Interrupted. Goodbye! 🐾[/dim]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask PAAW"),
):
    """
    Ask PAAW a single question and get a response.

    Example: paaw ask "What is the meaning of life?"
    """
    asyncio.run(_ask_question(question))


async def _ask_question(question: str):
    """Ask a single question."""
    agent = Agent()

    message = UnifiedMessage(
        channel=Channel.CLI,
        user_id=settings.default_user_id,
        content=question,
        timestamp=datetime.utcnow(),
    )

    console.print(f"\n[bold blue]You:[/bold blue] {question}\n")
    console.print("[bold cyan]PAAW:[/bold cyan]", end=" ")

    async for chunk in agent.process_stream(message):
        console.print(chunk, end="")

    console.print("\n")


@app.command()
def status():
    """
    Show PAAW status and health information.
    """
    console.print(
        Panel(
            f"[green]●[/green] Status: Running\n"
            f"[dim]Version:[/dim] {__version__}\n"
            f"[dim]Model:[/dim] {settings.llm.default_model}\n"
            f"[dim]Debug:[/dim] {settings.debug}\n"
            f"[dim]Log Level:[/dim] {settings.log_level}",
            title="🐾 PAAW Status",
            border_style="cyan",
        )
    )


@app.command()
def version():
    """Show PAAW version."""
    console.print(f"PAAW version {__version__} 🐾")


@app.command()
def viz(
    port: int = typer.Option(8080, "--port", "-p", help="Port to run the server on"),
):
    """
    Launch the mental model visualization in your browser.
    
    Opens a web UI showing the graph of PAAW's mental model.
    """
    import webbrowser
    import uvicorn
    from paaw.api.server import create_app
    
    console.print(
        Panel(
            f"[green]Starting visualization server...[/green]\n"
            f"[dim]URL:[/dim] http://localhost:{port}/viz\n\n"
            f"[dim]Press Ctrl+C to stop[/dim]",
            title="🐾 PAAW Mental Model Visualization",
            border_style="cyan",
        )
    )
    
    # Open browser after a short delay
    import threading
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{port}/viz")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run server
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


@app.command()
def serve(
    port: int = typer.Option(8080, "--port", "-p", help="Port to run server on"),
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
):
    """
    Start the PAAW API server.
    
    This runs PAAW as a background service:
    - API endpoints at http://localhost:8080
    - WebSocket chat at /ws/chat
    - Dashboard at /dashboard
    - Graph visualization at /viz
    """
    import uvicorn
    from paaw.api.server import create_app
    
    console.print(
        Panel(
            f"[bold green]Starting PAAW Server V3[/bold green]\n\n"
            f"API: http://{host}:{port}\n"
            f"Dashboard: http://{host}:{port}/dashboard\n"
            f"Graph: http://{host}:{port}/viz\n\n"
            f"[dim]Press Ctrl+C to stop[/dim]",
            title="🐾 PAAW Server",
            border_style="cyan",
        )
    )
    
    app = create_app()
    uvicorn.run(app, host=host, port=port, log_level="info")


@app.command()
def jobs(
    action: str = typer.Argument("list", help="Action: list, run <job_id>, or status"),
    job_id: str = typer.Argument(None, help="Job ID for run/status actions"),
):
    """
    Manage scheduled jobs.
    
    Examples:
        paaw jobs              # List all jobs
        paaw jobs list         # List all jobs
        paaw jobs run morning_news  # Run a job now
    """
    from pathlib import Path
    from paaw.scheduler.parser import load_all_jobs
    
    jobs_dir = Path(__file__).parent.parent.parent / "jobs"
    all_jobs = load_all_jobs(jobs_dir)
    
    if action == "list":
        console.print(
            Panel(
                "[bold]Scheduled Jobs[/bold]\n",
                title="🗓️ Jobs",
                border_style="cyan",
            )
        )
        
        for job in all_jobs:
            status_color = "green" if job.status == "active" else "yellow"
            console.print(f"  [{status_color}]●[/{status_color}] [bold]{job.id}[/bold]")
            console.print(f"    {job.name}")
            console.print(f"    [dim]Cron: {job.cron} ({job.timezone})[/dim]")
            console.print(f"    [dim]Channel: {job.alert_channel}[/dim]")
            console.print()
    
    elif action == "run":
        if not job_id:
            console.print("[red]Please specify a job ID to run[/red]")
            return
        
        asyncio.run(_run_job(job_id))
    
    else:
        console.print(f"[yellow]Unknown action: {action}[/yellow]")


async def _run_job(job_id: str):
    """Run a specific job."""
    from pathlib import Path
    from paaw.scheduler.runner import SchedulerRunner
    
    console.print(f"[cyan]Running job: {job_id}...[/cyan]\n")
    
    scheduler = SchedulerRunner()
    await scheduler.initialize()
    
    result = await scheduler.run_job_now(job_id)
    
    if "error" in result:
        console.print(f"[red]Error: {result['error']}[/red]")
    else:
        status_color = "green" if result["status"] == "completed" else "red"
        console.print(f"[{status_color}]Status: {result['status']}[/{status_color}]")
        console.print(f"[dim]Duration: {result['duration']:.2f}s[/dim]")
        console.print(f"[dim]Alert sent: {result['alert_sent']}[/dim]")
        console.print(f"\n[bold]Summary:[/bold]\n{result['summary']}")
    
    await scheduler.stop()


@app.command()
def scheduler(
    action: str = typer.Argument("start", help="Action: start or stop"),
):
    """
    Run the job scheduler.
    
    Examples:
        paaw scheduler start   # Start the scheduler daemon
    """
    if action == "start":
        console.print(
            Panel(
                "[bold green]Starting Scheduler[/bold green]\n\n"
                "Scheduler will check jobs every minute.\n"
                "[dim]Press Ctrl+C to stop[/dim]",
                title="🗓️ PAAW Scheduler",
                border_style="cyan",
            )
        )
        
        asyncio.run(_run_scheduler())
    else:
        console.print(f"[yellow]Unknown action: {action}[/yellow]")


async def _run_scheduler():
    """Run the scheduler."""
    from paaw.scheduler.runner import SchedulerRunner
    
    scheduler = SchedulerRunner()
    await scheduler.start()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[dim]Stopping scheduler...[/dim]")
        await scheduler.stop()


@app.callback()
def main():
    """
    🐾 PAAW - Personal AI Assistant that Works

    A goal-oriented AI assistant with memory that lives on your machine.
    """
    pass


if __name__ == "__main__":
    app()
