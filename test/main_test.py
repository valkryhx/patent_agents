"""
Patent Agent Demo Test Mode - Main CLI Interface
Provides command-line interface for testing the patent agent system
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
from rich.syntax import Syntax

from .patent_agent_system_test import PatentAgentSystemTestMode

app = typer.Typer()
console = Console()

@app.command()
def main(
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Patent topic"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Patent description"),
    simple_test: bool = typer.Option(False, "--simple", "-s", help="Run simple agent test"),
    workflow_test: bool = typer.Option(False, "--workflow", "-w", help="Run workflow test"),
    status: bool = typer.Option(False, "--status", help="Show system status"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Patent Agent Demo Test Mode - Multi-Agent Patent Development System"""
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    if simple_test:
        asyncio.run(run_simple_test(topic, description))
    elif workflow_test:
        asyncio.run(run_workflow_test(topic, description))
    elif status:
        asyncio.run(show_test_system_status())
    else:
        asyncio.run(run_interactive_test_mode(topic, description))

async def run_simple_test(topic: Optional[str], description: Optional[str]):
    """Run simple test of all agents"""
    
    # Get topic and description
    if not topic:
        topic = os.getenv("PATENT_TOPIC") or console.input("[bold blue]Enter patent topic: [/bold blue]")
    if not description:
        description = os.getenv("PATENT_DESC") or console.input("[bold blue]Enter patent description: [/bold blue]")
    
    if not topic or not description:
        console.print("[red]Topic and description are required[/red]")
        sys.exit(1)
    
    console.print(Panel.fit(
        f"[bold green]Patent Agent Test Mode[/bold green]\n\n"
        f"[bold]Topic:[/bold] {topic}\n"
        f"[bold]Description:[/bold] {description}\n\n"
        f"[italic]Running Simple Agent Test[/italic]",
        title="🧪 Simple Test Mode"
    ))
    
    # Initialize test system
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Initializing Test System...", total=None)
        
        system = PatentAgentSystemTestMode()
        await system.start()
        
        progress.update(task, description="Test system initialized!")
    
    # Run simple test
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running simple agent test...", total=None)
        
        try:
            result = await system.run_simple_test(topic, description)
            
            if result["success"]:
                progress.update(task, description="Simple test completed!")
                console.print(f"[green]✅ Simple test completed successfully![/green]")
                
                # Display test results
                display_test_results(result["test_results"])
            else:
                progress.update(task, description="Simple test failed!")
                console.print(f"[red]❌ Simple test failed: {result.get('error', 'Unknown error')}[/red]")
                
        except Exception as e:
            progress.update(task, description="Simple test failed!")
            console.print(f"[red]❌ Error: {e}[/red]")
    
    # Shutdown system
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Shutting down test system...", total=None)
        
        await system.stop()
        
        progress.update(task, description="Test system shutdown complete!")

async def run_workflow_test(topic: Optional[str], description: Optional[str]):
    """Run workflow test"""
    
    # Get topic and description
    if not topic:
        topic = os.getenv("PATENT_TOPIC") or console.input("[bold blue]Enter patent topic: [/bold blue]")
    if not description:
        description = os.getenv("PATENT_DESC") or console.input("[bold blue]Enter patent description: [/bold blue]")
    
    if not topic or not description:
        console.print("[red]Topic and description are required[/red]")
        sys.exit(1)
    
    console.print(Panel.fit(
        f"[bold green]Patent Agent Test Mode[/bold green]\n\n"
        f"[bold]Topic:[/bold] {topic}\n"
        f"[bold]Description:[/bold] {description}\n\n"
        f"[italic]Running Workflow Test[/italic]",
        title="🔄 Workflow Test Mode"
    ))
    
    # Initialize test system
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Initializing Test System...", total=None)
        
        system = PatentAgentSystemTestMode()
        await system.start()
        
        progress.update(task, description="Test system initialized!")
    
    # Execute workflow
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Starting test workflow...", total=None)
        
        try:
            result = await system.execute_workflow(topic, description)
            
            if result["success"]:
                progress.update(task, description="Test workflow started!")
                console.print(f"[green]✅ Test workflow started: {result['workflow_id']}[/green]")
                
                # Monitor workflow for a short time
                workflow_id = result["workflow_id"]
                console.print(f"[yellow]⚠️  Monitoring workflow for 10 seconds...[/yellow]")
                
                for i in range(10):
                    await asyncio.sleep(1)
                    status = await system.get_workflow_status(workflow_id)
                    if status["success"]:
                        console.print(f"[blue]📊 Workflow status at {i+1}s: Active[/blue]")
                    else:
                        console.print(f"[red]❌ Workflow error: {status.get('error')}[/red]")
                        break
                
            else:
                progress.update(task, description="Test workflow failed!")
                console.print(f"[red]❌ Test workflow failed: {result.get('error', 'Unknown error')}[/red]")
                
        except Exception as e:
            progress.update(task, description="Test workflow failed!")
            console.print(f"[red]❌ Error: {e}[/red]")
    
    # Shutdown system
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Shutting down test system...", total=None)
        
        await system.stop()
        
        progress.update(task, description="Test system shutdown complete!")

async def run_interactive_test_mode(topic: Optional[str], description: Optional[str]):
    """Run interactive test mode"""
    
    # Get topic and description
    if not topic:
        topic = os.getenv("PATENT_TOPIC") or console.input("[bold blue]Enter patent topic: [/bold blue]")
    if not description:
        description = os.getenv("PATENT_DESC") or console.input("[bold blue]Enter patent description: [/bold blue]")
    
    if not topic or not description:
        console.print("[red]Topic and description are required[/red]")
        sys.exit(1)
    
    console.print(Panel.fit(
        f"[bold green]Patent Agent Test Mode[/bold green]\n\n"
        f"[bold]Topic:[/bold] {topic}\n"
        f"[bold]Description:[/bold] {description}\n\n"
        f"[italic]Interactive Test Mode[/italic]",
        title="🎮 Interactive Test Mode"
    ))
    
    # Initialize test system
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Initializing Test System...", total=None)
        
        system = PatentAgentSystemTestMode()
        await system.start()
        
        progress.update(task, description="Test system initialized!")
    
    console.print("[green]✅ Test system ready![/green]")
    console.print("\n[bold]Available commands:[/bold]")
    console.print("1. [blue]simple[/blue] - Run simple agent test")
    console.print("2. [blue]workflow[/blue] - Run workflow test")
    console.print("3. [blue]status[/blue] - Show system status")
    console.print("4. [blue]quit[/blue] - Exit")
    
    while True:
        try:
            command = console.input("\n[bold yellow]Enter command: [/bold yellow]").strip().lower()
            
            if command == "simple":
                console.print("[blue]Running simple test...[/blue]")
                result = await system.run_simple_test(topic, description)
                if result["success"]:
                    display_test_results(result["test_results"])
                else:
                    console.print(f"[red]Simple test failed: {result.get('error')}[/red]")
                    
            elif command == "workflow":
                console.print("[blue]Running workflow test...[/blue]")
                result = await system.execute_workflow(topic, description)
                if result["success"]:
                    console.print(f"[green]Workflow started: {result['workflow_id']}[/green]")
                else:
                    console.print(f"[red]Workflow failed: {result.get('error')}[/red]")
                    
            elif command == "status":
                console.print("[blue]Getting system status...[/blue]")
                # Get status of all agents
                for name, agent in system.agents.items():
                    status = await agent.get_status()
                    console.print(f"[cyan]{name}:[/cyan] {status['status']}")
                    
            elif command == "quit":
                console.print("[yellow]Shutting down...[/yellow]")
                break
                
            else:
                console.print("[red]Unknown command. Use: simple, workflow, status, or quit[/red]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    # Shutdown system
    await system.stop()
    console.print("[green]Test system shutdown complete![/green]")

async def show_test_system_status():
    """Show test system status"""
    console.print(Panel.fit(
        "[bold green]Patent Agent Test Mode Status[/bold green]\n\n"
        "[bold]Features:[/bold]\n"
        "✅ All agents in test mode\n"
        "✅ No external API calls\n"
        "✅ Fast response times\n"
        "✅ Detailed test output\n"
        "✅ Easy debugging\n\n"
        "[bold]Available Agents:[/bold]\n"
        "• Planner Agent\n"
        "• Writer Agent\n"
        "• Searcher Agent\n"
        "• Reviewer Agent\n"
        "• Rewriter Agent\n"
        "• Discusser Agent\n"
        "• Coordinator Agent\n\n"
        "[italic]Use --simple or --workflow to run tests[/italic]",
        title="📊 Test System Status"
    ))

def display_test_results(test_results: dict):
    """Display test results in a table"""
    console.print("\n[bold green]Test Results:[/bold green]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Execution Time", style="yellow")
    table.add_column("Has Content", style="blue")
    
    for agent_name, result in test_results.items():
        status = "✅ Success" if result["success"] else "❌ Failed"
        execution_time = f"{result['execution_time']:.2f}s"
        has_content = "✅ Yes" if result["has_content"] else "❌ No"
        
        table.add_row(
            agent_name,
            status,
            execution_time,
            has_content
        )
    
    console.print(table)
    
    # Summary
    total_agents = len(test_results)
    successful_agents = sum(1 for r in test_results.values() if r["success"])
    total_time = sum(r["execution_time"] for r in test_results.values())
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"• Total agents tested: {total_agents}")
    console.print(f"• Successful: {successful_agents}/{total_agents}")
    console.print(f"• Total execution time: {total_time:.2f}s")
    console.print(f"• Average time per agent: {total_time/total_agents:.2f}s")

if __name__ == "__main__":
    app()