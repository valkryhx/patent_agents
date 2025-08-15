#!/usr/bin/env python3
"""
Patent Agent Demo - Main Entry Point
Multi-agent system for patent planning, research, discussion, writing, and review
"""

import asyncio
import argparse
import logging
import sys
import os
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text

from patent_agent_system import PatentAgentSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()

class PatentAgentDemo:
    """Main demo class for the Patent Agent System"""
    
    def __init__(self):
        self.patent_system = None
        self.is_running = False
        
    async def start(self):
        """Start the patent agent demo"""
        try:
            console.print(Panel.fit(
                "[bold blue]Patent Agent Demo System[/bold blue]\n"
                "Multi-Agent Patent Planning & Development Platform\n"
                "Powered by FastMCP and Google A2A",
                border_style="blue"
            ))
            
            # Initialize the system
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Initializing Patent Agent System...", total=None)
                
                self.patent_system = PatentAgentSystem()
                await self.patent_system.start()
                
                progress.update(task, description="System initialized successfully!")
                
            self.is_running = True
            console.print("[green]✓ Patent Agent System started successfully![/green]")
            
            # Show system status
            await self.show_system_status()
            
        except Exception as e:
            console.print(f"[red]✗ Failed to start Patent Agent System: {e}[/red]")
            logger.error(f"Startup error: {e}")
            raise
            
    async def stop(self):
        """Stop the patent agent demo"""
        try:
            if self.patent_system and self.is_running:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Shutting down Patent Agent System...", total=None)
                    
                    await self.patent_system.stop()
                    
                    progress.update(task, description="System shutdown complete!")
                    
                self.is_running = False
                console.print("[green]✓ Patent Agent System stopped successfully![/green]")
                
        except Exception as e:
            console.print(f"[red]✗ Error during shutdown: {e}[/red]")
            logger.error(f"Shutdown error: {e}")
            
    async def show_system_status(self):
        """Display system status"""
        try:
            if not self.patent_system:
                return
                
            status = await self.patent_system.get_system_status()
            
            # Create status table
            table = Table(title="System Status")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Agents", str(status.total_agents))
            table.add_row("Active Agents", str(status.active_agents))
            table.add_row("Active Workflows", str(status.active_workflows))
            table.add_row("System Health", status.system_health)
            table.add_row("Uptime", f"{status.uptime:.1f} seconds")
            
            console.print(table)
            
            # Show agent details
            await self.show_agent_details()
            
        except Exception as e:
            console.print(f"[red]Error getting system status: {e}[/red]")
            
    async def show_agent_details(self):
        """Display detailed agent information"""
        try:
            if not self.patent_system:
                return
                
            console.print("\n[bold cyan]Agent Details:[/bold cyan]")
            
            agents = ["planner_agent", "searcher_agent", "discusser_agent", 
                     "writer_agent", "reviewer_agent", "rewriter_agent", "coordinator_agent"]
            
            for agent_name in agents:
                agent_status = await self.patent_system.get_agent_status(agent_name)
                if agent_status:
                    status_icon = "🟢" if agent_status.get("status") == "idle" else "🟡"
                    console.print(f"{status_icon} {agent_name}: {agent_status.get('status', 'unknown')}")
                    
        except Exception as e:
            console.print(f"[red]Error getting agent details: {e}[/red]")
            
    async def run_demo_workflow(self):
        """Run a complete patent development workflow"""
        try:
            if not self.patent_system or not self.is_running:
                console.print("[red]System not running. Please start the system first.[/red]")
                return
                
            console.print("\n[bold blue]Patent Development Workflow Demo[/bold blue]")
            
            # Get patent topic from user
            topic = Prompt.ask("Enter patent topic", default="AI-powered medical diagnosis system")
            description = Prompt.ask("Enter patent description", 
                                   default="A machine learning system for automated medical diagnosis using image analysis")
            
            # Confirm workflow start
            if not Confirm.ask(f"Start patent development for: {topic}?"):
                console.print("[yellow]Workflow cancelled by user.[/yellow]")
                return
                
            # Start the workflow
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Starting patent development workflow...", total=None)
                
                try:
                    result = await self.patent_system.develop_patent(topic, description)
                    
                    progress.update(task, description="Workflow completed successfully!")
                    
                    # Display results
                    await self.display_workflow_results(result)
                    
                except Exception as e:
                    progress.update(task, description="Workflow failed!")
                    console.print(f"[red]Workflow error: {e}[/red]")
                    
        except Exception as e:
            console.print(f"[red]Error running demo workflow: {e}[/red]")
            
    async def display_workflow_results(self, result: Dict[str, Any]):
        """Display workflow results"""
        try:
            console.print("\n[bold green]🎯 Patent Development Complete![/bold green]")
            
            # Create results table
            table = Table(title="Workflow Results")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            
            if "workflow_id" in result:
                table.add_row("Workflow ID", result["workflow_id"])
            if "status" in result:
                table.add_row("Status", result["status"])
            if "completion_time" in result:
                table.add_row("Completion Time", str(result["completion_time"]))
            if "message" in result:
                table.add_row("Message", result["message"])
                
            console.print(table)
            
            # Show patent summary if available
            if "patent_summary" in result:
                summary = result["patent_summary"]
                console.print("\n[bold cyan]Patent Summary:[/bold cyan]")
                
                summary_table = Table()
                summary_table.add_column("Field", style="cyan")
                summary_table.add_column("Value", style="green")
                
                if "title" in summary:
                    summary_table.add_row("Title", summary["title"])
                if "status" in summary:
                    summary_table.add_row("Status", summary["status"])
                if "confidence_score" in summary:
                    summary_table.add_row("Confidence Score", f"{summary['confidence_score']:.1%}")
                    
                console.print(summary_table)
                
        except Exception as e:
            console.print(f"[red]Error displaying results: {e}[/red]")
            
    async def interactive_mode(self):
        """Run interactive mode"""
        try:
            console.print("\n[bold blue]Interactive Mode[/bold blue]")
            console.print("Type 'help' for available commands, 'quit' to exit.")
            
            while self.is_running:
                try:
                    command = Prompt.ask("\n[bold green]patent_demo>[/bold green]")
                    
                    if command.lower() in ['quit', 'exit', 'q']:
                        break
                    elif command.lower() == 'help':
                        await self.show_help()
                    elif command.lower() == 'status':
                        await self.show_system_status()
                    elif command.lower() == 'workflow':
                        await self.run_demo_workflow()
                    elif command.lower() == 'health':
                        await self.show_health_check()
                    elif command.lower() == 'agents':
                        await self.show_agent_details()
                    elif command.lower() == 'workflows':
                        await self.show_active_workflows()
                    else:
                        console.print(f"[yellow]Unknown command: {command}[/yellow]")
                        console.print("Type 'help' for available commands.")
                        
                except KeyboardInterrupt:
                    console.print("\n[yellow]Use 'quit' to exit.[/yellow]")
                except Exception as e:
                    console.print(f"[red]Command error: {e}[/red]")
                    
        except Exception as e:
            console.print(f"[red]Interactive mode error: {e}[/red]")
            
    async def show_help(self):
        """Show help information"""
        help_text = """
[bold cyan]Available Commands:[/bold cyan]

[bold]help[/bold]     - Show this help message
[bold]status[/bold]   - Show system status
[bold]workflow[/bold] - Run patent development workflow
[bold]health[/bold]   - Perform health check
[bold]agents[/bold]   - Show agent details
[bold]workflows[/bold] - Show active workflows
[bold]quit[/bold]     - Exit the system

[bold cyan]Patent Development Workflow:[/bold cyan]
1. Planning & Strategy (Planner Agent)
2. Prior Art Search (Searcher Agent)
3. Innovation Discussion (Discusser Agent)
4. Patent Drafting (Writer Agent)
5. Quality Review (Reviewer Agent)
6. Final Rewrite (Rewriter Agent)

[bold cyan]System Features:[/bold cyan]
- FastMCP message passing and coordination
- Google A2A AI-powered content generation
- Multi-agent collaboration and workflow management
- Automated quality assessment and improvement
- Comprehensive patent compliance checking
        """
        
        console.print(Panel(help_text, title="Help", border_style="blue"))
        
    async def show_health_check(self):
        """Perform and display health check"""
        try:
            if not self.patent_system:
                return
                
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Performing health check...", total=None)
                
                health_status = await self.patent_system.health_check()
                
                progress.update(task, description="Health check completed!")
                
            # Display health status
            console.print("\n[bold cyan]System Health Check:[/bold cyan]")
            
            health_table = Table()
            health_table.add_column("Component", style="cyan")
            health_table.add_column("Status", style="green")
            
            for component, status in health_status.items():
                if isinstance(status, dict):
                    continue
                    
                status_color = "green" if status == "healthy" else "yellow" if status == "degraded" else "red"
                health_table.add_row(component, f"[{status_color}]{status}[/{status_color}]")
                
            console.print(health_table)
            
        except Exception as e:
            console.print(f"[red]Error performing health check: {e}[/red]")
            
    async def show_active_workflows(self):
        """Show active workflows"""
        try:
            if not self.patent_system:
                return
                
            workflows = await self.patent_system.monitor_workflows()
            
            if not workflows:
                console.print("[yellow]No active workflows.[/yellow]")
                return
                
            console.print(f"\n[bold cyan]Active Workflows ({len(workflows)}):[/bold cyan]")
            
            workflow_table = Table()
            workflow_table.add_column("Workflow ID", style="cyan")
            workflow_table.add_column("Topic", style="green")
            workflow_table.add_column("Status", style="yellow")
            workflow_table.add_column("Progress", style="blue")
            
            for workflow in workflows:
                workflow_table.add_row(
                    workflow.get("workflow_id", "N/A")[:8] + "...",
                    workflow.get("topic", "N/A"),
                    workflow.get("status", "N/A"),
                    workflow.get("progress", "N/A")
                )
                
            console.print(workflow_table)
            
        except Exception as e:
            console.print(f"[red]Error getting active workflows: {e}[/red]")
            
    async def run(self, args):
        """Main run method"""
        try:
            # Start the system
            await self.start()
            
            if args.interactive:
                # Run interactive mode
                await self.interactive_mode()
            elif args.topic:
                # Run single workflow
                await self.run_demo_workflow()
            else:
                # Show status and wait
                console.print("\n[yellow]System running. Press Ctrl+C to stop.[/yellow]")
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    pass
                    
        except Exception as e:
            console.print(f"[red]Fatal error: {e}[/red]")
            logger.error(f"Fatal error: {e}")
        finally:
            # Cleanup
            await self.stop()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Patent Agent Demo - Multi-Agent Patent Development System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --interactive          # Run interactive mode
  python main.py --topic "AI system"    # Run single workflow
  python main.py                        # Run system and wait
        """
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--topic",
        type=str,
        help="Patent topic for demo workflow"
    )
    
    parser.add_argument(
        "--description",
        type=str,
        help="Patent description for demo workflow"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Create and run demo
    demo = PatentAgentDemo()
    
    try:
        asyncio.run(demo.run(args))
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()