"""
Patent Agent Demo - Main CLI Interface
Provides command-line interface for the patent agent system
"""

import asyncio
import os
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from .patent_agent_system import PatentAgentSystem

app = typer.Typer()
console = Console()

@app.command()
def main(
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Patent topic"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Patent description"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
    health_check: bool = typer.Option(False, "--health", help="Perform health check"),
    status: bool = typer.Option(False, "--status", help="Show system status")
):
    """Patent Agent Demo - Multi-Agent Patent Development System"""
    
    if health_check:
        asyncio.run(perform_health_check())
    elif status:
        asyncio.run(show_system_status())
    elif interactive:
        asyncio.run(interactive_mode())
    else:
        asyncio.run(run_patent_workflow(topic, description))

async def run_patent_workflow(topic: Optional[str], description: Optional[str]):
    """Run the patent development workflow"""
    
    # Get topic and description
    if not topic:
        topic = os.getenv("PATENT_TOPIC") or console.input("[bold blue]Enter patent topic: [/bold blue]")
    if not description:
        description = os.getenv("PATENT_DESC") or console.input("[bold blue]Enter patent description: [/bold blue]")
    
    if not topic or not description:
        console.print("[red]Topic and description are required[/red]")
        sys.exit(1)
    
    console.print(Panel.fit(
        f"[bold green]Patent Agent Demo[/bold green]\n\n"
        f"[bold]Topic:[/bold] {topic}\n"
        f"[bold]Description:[/bold] {description}\n\n"
        f"[italic]Powered by Message Bus and Google A2A[/italic]",
        title="🚀 Starting Patent Development"
    ))
    
    # Initialize system
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Initializing Patent Agent System...", total=None)
        
        system = PatentAgentSystem()
        await system.start()
        
        progress.update(task, description="System initialized successfully!")
    
    # Execute workflow
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Starting patent development workflow...", total=None)
        
        try:
            result = await system.execute_workflow(topic, description)
            
            if result["success"]:
                progress.update(task, description="Workflow started successfully!")
                console.print(f"[green]✅ Workflow started: {result['workflow_id']}[/green]")
                console.print(f"[yellow]⚠️  Workflow is running asynchronously. Check logs for progress.[/yellow]")
            else:
                progress.update(task, description="Workflow failed to start!")
                console.print(f"[red]❌ Workflow failed: {result.get('error', 'Unknown error')}[/red]")
                
        except Exception as e:
            progress.update(task, description="Workflow failed!")
            console.print(f"[red]❌ Error: {e}[/red]")
    
    # Shutdown system
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Shutting down Patent Agent System...", total=None)
        
        await system.stop()
        
        progress.update(task, description="System shutdown complete!")

async def perform_health_check():
    """Perform a comprehensive health check"""
    console.print(Panel.fit(
        "[bold green]Patent Agent Demo[/bold green]\n\n"
        "[italic]Performing comprehensive health check...[/italic]",
        title="🏥 Health Check"
    ))
    
    system = PatentAgentSystem()
    
    try:
        await system.start()
        health = await system.health_check()
        
        # Display health status
        table = Table(title="System Health Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")
        
        for component, status in health.items():
            if component == "agents":
                continue
            color = "green" if status == "healthy" else "red" if status == "error" else "yellow"
            table.add_row(component, f"[{color}]{status}[/{color}]", "")
        
        # Add agent status
        if "agents" in health:
            for agent_name, agent_status in health["agents"].items():
                status = agent_status.get("status", "unknown")
                color = "green" if status == "healthy" else "red" if status == "error" else "yellow"
                table.add_row(f"Agent: {agent_name}", f"[{color}]{status}[/{color}]", "")
        
        console.print(table)
        
        # Overall status
        overall_status = health.get("system", "unknown")
        if overall_status == "healthy":
            console.print("[green]✅ System is healthy![/green]")
        else:
            console.print(f"[red]❌ System has issues: {overall_status}[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Health check failed: {e}[/red]")
    finally:
        await system.stop()

async def show_system_status():
    """Show detailed system status"""
    console.print(Panel.fit(
        "[bold green]Patent Agent Demo[/bold green]\n\n"
        "[italic]Retrieving system status...[/italic]",
        title="📊 System Status"
    ))
    
    system = PatentAgentSystem()
    
    try:
        await system.start()
        status = await system.get_system_status()
        
        # Display status
        table = Table(title="System Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Agents", str(status.total_agents))
        table.add_row("Active Agents", str(status.active_agents))
        table.add_row("Message Queue Size", str(status.message_queue_size))
        table.add_row("System Health", status.system_health)
        table.add_row("Uptime", f"{status.uptime:.2f} seconds")
        
        console.print(table)
        
        # Performance metrics
        if status.performance_metrics:
            console.print("\n[bold]Performance Metrics:[/bold]")
            for metric, value in status.performance_metrics.items():
                console.print(f"  {metric}: {value}")
                
    except Exception as e:
        console.print(f"[red]❌ Failed to get system status: {e}[/red]")
    finally:
        await system.stop()

async def interactive_mode():
    """Interactive mode for patent development"""
    console.print(Panel.fit(
        "[bold green]Patent Agent Demo[/bold green]\n\n"
        "[italic]Interactive Mode[/italic]\n\n"
        "This mode allows you to interact with the patent agent system step by step.",
        title="🎮 Interactive Mode"
    ))
    
    # Get patent information
    topic = console.input("[bold blue]Enter patent topic: [/bold blue]")
    description = console.input("[bold blue]Enter patent description: [/bold blue]")
    
    if not topic or not description:
        console.print("[red]Topic and description are required[/red]")
        return
    
    # Initialize system
    console.print("[yellow]Initializing system...[/yellow]")
    system = PatentAgentSystem()
    await system.start()
    
    try:
        # Start workflow
        console.print("[yellow]Starting workflow...[/yellow]")
        result = await system.execute_workflow(topic, description)
        
        if result["success"]:
            workflow_id = result["workflow_id"]
            console.print(f"[green]✅ Workflow started: {workflow_id}[/green]")
            
            # Monitor progress
            console.print("[yellow]Monitoring progress...[/yellow]")
            while True:
                status = await system.get_workflow_status(workflow_id)
                
                if status.get("status") == "completed":
                    console.print("[green]✅ Workflow completed![/green]")
                    break
                elif status.get("status") == "failed":
                    console.print(f"[red]❌ Workflow failed: {status.get('error', 'Unknown error')}[/red]")
                    break
                
                console.print(f"[blue]Status: {status.get('status', 'unknown')}[/blue]")
                await asyncio.sleep(5)
        else:
            console.print(f"[red]❌ Failed to start workflow: {result.get('error', 'Unknown error')}[/red]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
    finally:
        await system.stop()

if __name__ == "__main__":
    app()