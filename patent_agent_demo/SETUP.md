# Patent Agent Demo - Setup & Usage Guide

This guide will help you set up and run the Patent Agent Demo system, a multi-agent platform for automated patent development using FastMCP and Google A2A.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Google AI API key (required)
- Git

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd patent_agent_demo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or use your preferred editor
```

**Required Configuration:**
- `GOOGLE_API_KEY`: Your Google AI API key from [MakerSuite](https://makersuite.google.com/app/apikey)

### 4. Run the Demo

```bash
# Simple demo
python demo_simple.py

# Interactive mode
python main.py --interactive

# Single workflow
python main.py --topic "Your Patent Topic"
```

## 🔧 Detailed Setup

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
GOOGLE_API_KEY=your_actual_api_key_here

# Optional
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# FastMCP Configuration
FASTMCP_HOST=localhost
FASTMCP_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Google AI API Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

### Dependencies

The system requires several Python packages:

- **FastMCP**: Message passing and coordination framework
- **Google Generative AI**: AI-powered content generation
- **Rich**: Beautiful terminal output
- **Pydantic**: Data validation and settings management
- **AsyncIO**: Asynchronous programming support

## 🎯 Usage Examples

### Basic Usage

```python
from patent_agent_system import PatentAgentSystem

async def main():
    # Initialize system
    system = PatentAgentSystem()
    await system.start()
    
    # Develop a patent
    result = await system.develop_patent(
        topic="AI-powered medical diagnosis",
        description="Machine learning system for automated medical diagnosis"
    )
    
    print(f"Patent development complete: {result}")
    
    # Cleanup
    await system.stop()

# Run
asyncio.run(main())
```

### Interactive Mode

```bash
python main.py --interactive
```

Available commands:
- `help` - Show available commands
- `status` - Display system status
- `workflow` - Run patent development workflow
- `health` - Perform system health check
- `agents` - Show agent details
- `workflows` - Show active workflows
- `quit` - Exit the system

### Command Line Interface

```bash
# Run with specific topic
python main.py --topic "Quantum Computing Algorithm"

# Verbose logging
python main.py --verbose

# Run and wait
python main.py
```

## 🏗️ System Architecture

### Agent Roles

1. **Planner Agent**: Creates patent strategy and roadmap
2. **Searcher Agent**: Conducts prior art research
3. **Discusser Agent**: Facilitates innovation discussions
4. **Writer Agent**: Drafts patent applications
5. **Reviewer Agent**: Reviews quality and compliance
6. **Rewriter Agent**: Implements feedback and improvements
7. **Coordinator Agent**: Orchestrates the entire workflow

### Workflow Stages

```
Planning → Research → Discussion → Writing → Review → Rewrite → Complete
```

### FastMCP Integration

- **Message Broker**: Handles inter-agent communication
- **Task Coordination**: Manages workflow execution
- **Status Tracking**: Monitors agent and workflow states
- **Error Handling**: Provides fault tolerance and recovery

### Google A2A Integration

- **Content Generation**: Creates patent drafts and descriptions
- **Analysis**: Evaluates patent topics and prior art
- **Optimization**: Improves content quality and compliance
- **Technical Writing**: Generates technical documentation

## 🔍 Troubleshooting

### Common Issues

#### 1. API Key Errors
```
Error: Google API key is required
```
**Solution**: Ensure your `GOOGLE_API_KEY` is set in the `.env` file

#### 2. Import Errors
```
ModuleNotFoundError: No module named 'patent_agent_system'
```
**Solution**: Ensure you're in the correct directory and have installed dependencies

#### 3. Permission Errors
```
PermissionError: [Errno 13] Permission denied
```
**Solution**: Check file permissions and ensure you have write access

#### 4. Network Errors
```
ConnectionError: Failed to connect to Google AI API
```
**Solution**: Check your internet connection and API key validity

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python main.py --verbose
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

### Health Checks

Use the built-in health check system:

```bash
# In interactive mode
patent_demo> health

# Or programmatically
health_status = await system.health_check()
print(health_status)
```

## 📊 Monitoring & Metrics

### System Status

```python
status = await system.get_system_status()
print(f"System Health: {status.system_health}")
print(f"Active Agents: {status.active_agents}")
print(f"Uptime: {status.uptime:.1f} seconds")
```

### Agent Performance

```python
agent_status = await system.get_agent_status("planner_agent")
metrics = agent_status.get("performance_metrics", {})
print(f"Tasks Completed: {metrics.get('tasks_completed', 0)}")
print(f"Average Execution Time: {metrics.get('average_execution_time', 0):.2f}s")
```

### Workflow Monitoring

```python
workflows = await system.monitor_workflows()
for workflow in workflows:
    print(f"Workflow {workflow['workflow_id']}: {workflow['status']}")
```

## 🚀 Advanced Usage

### Custom Agent Configuration

```python
from agents import PlannerAgent

# Create custom planner agent
planner = PlannerAgent()
await planner.start()

# Execute custom task
result = await planner.execute_task({
    "type": "patent_planning",
    "topic": "Custom Topic",
    "description": "Custom Description"
})
```

### Workflow Customization

```python
# Custom workflow parameters
result = await system.develop_patent(
    topic="Custom Topic",
    description="Custom Description",
    workflow_type="fast_track"  # or "comprehensive"
)
```

### Integration with External Systems

```python
# Send messages to specific agents
await system.send_agent_message(
    "writer_agent",
    MessageType.COORDINATION,
    {"custom_task": "data"}
)

# Broadcast system messages
await system.broadcast_system_message(
    MessageType.STATUS,
    {"system_update": "information"}
)
```

## 🔒 Security Considerations

### API Key Management

- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Monitor API usage and costs

### Data Privacy

- Patent data is processed locally
- No data is sent to external services except Google AI API
- Consider data retention policies
- Implement access controls for sensitive information

### Network Security

- Use HTTPS for external API calls
- Implement rate limiting
- Monitor for suspicious activity
- Keep dependencies updated

## 📈 Performance Optimization

### System Tuning

```python
# Adjust workflow timeout
system.workflow_timeout = 600  # 10 minutes

# Set maximum concurrent workflows
system.max_workflows = 5

# Configure agent pool size
system.agent_pool_size = 10
```

### Resource Management

- Monitor memory usage during large workflows
- Implement connection pooling for external APIs
- Use async operations for I/O-bound tasks
- Implement caching for repeated operations

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_planner_agent.py

# Run with coverage
pytest --cov=patent_agents tests/
```

### Integration Tests

```bash
# Test complete workflow
python -m pytest tests/test_integration.py

# Test agent communication
python -m pytest tests/test_agent_communication.py
```

### Load Testing

```bash
# Test multiple concurrent workflows
python tests/load_test.py --workflows 10 --duration 300
```

## 📚 Additional Resources

### Documentation

- [FastMCP Documentation](https://fastmcp.dev/)
- [Google AI Documentation](https://ai.google.dev/)
- [Python AsyncIO Guide](https://docs.python.org/3/library/asyncio.html)

### Community

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share ideas
- Contributing: Guidelines for contributing to the project

### Support

For technical support:
1. Check the troubleshooting section
2. Review GitHub issues
3. Create a new issue with detailed information
4. Include logs and error messages

## 🎉 Getting Help

If you need assistance:

1. **Check the documentation** - This guide covers most common scenarios
2. **Review examples** - Look at the demo scripts and test files
3. **Search issues** - Check if your problem has been reported
4. **Create an issue** - Provide detailed information about your problem

### Issue Template

When creating an issue, include:

- **Description**: What you're trying to do
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, dependencies
- **Steps to reproduce**: Detailed steps to recreate the issue
- **Logs**: Relevant error messages and logs

---

**Happy Patent Development! 🚀📚**