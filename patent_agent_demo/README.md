# Patent Agent Demo

A sophisticated multi-agent system built with Message Bus and Google A2A for automated patent planning, research, discussion, writing, and review.

## Features

- **Multi-Agent Architecture**: Coordinated agents for different patent development stages
- **Message Bus Integration**: High-performance message passing and coordination
- **Google A2A Integration**: Advanced AI-powered content generation
- **Comprehensive Workflow**: From planning to final patent draft
- **Quality Assurance**: Built-in review and rewrite cycles
- **Progress Tracking**: Real-time monitoring and incremental file generation

## Architecture

The system consists of specialized agents working together:

- **Planner Agent**: Strategic planning and patent strategy development
- **Searcher Agent**: Prior art research and patent analysis
- **Discusser Agent**: Innovation discussion and idea refinement
- **Writer Agent**: Patent drafting and technical writing
- **Reviewer Agent**: Quality review and compliance checking
- **Rewriter Agent**: Feedback implementation and improvement
- **Coordinator Agent**: Workflow orchestration and agent coordination

## Quick Start

### Prerequisites

- Python 3.8+
- Google A2A API access
- Required dependencies (see requirements.txt)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd patent_agent_demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export ZHIPUAI_API_KEY="your_api_key_here"
export PATENT_TOPIC="Your Patent Topic"
export PATENT_DESC="Your Patent Description"
```

4. Run the system:
```bash
python run_patent_workflow.py
```

## Configuration

### Environment Variables

```bash
# API Configuration
ZHIPUAI_API_KEY=your_api_key_here

# Message Bus Configuration
MESSAGE_BUS_HOST=localhost
MESSAGE_BUS_PORT=8000

# Patent Configuration
PATENT_TOPIC="Your Patent Topic"
PATENT_DESC="Your Patent Description"
```

### System Configuration

The system can be configured through the main configuration file:

```python
# patent_agent_system.py
system = PatentAgentSystem()
await system.start()
```

## Usage

### Basic Usage

```python
from patent_agent_demo.patent_agent_system import PatentAgentSystem

async def main():
    system = PatentAgentSystem()
    await system.start()
    
    # Execute patent workflow
    result = await system.execute_workflow(
        topic="AI-Powered Patent Analysis",
        description="A system for automated patent analysis using AI"
    )
    
    await system.stop()

asyncio.run(main())
```

### Advanced Usage

```python
# Monitor workflow progress
status = await system.get_workflow_status(workflow_id)

# Get system health
health = await system.health_check()

# Get system status
status = await system.get_system_status()
```

## Workflow Stages

1. **Planning & Strategy**: Define patent strategy and approach
2. **Prior Art Search**: Research existing patents and technologies
3. **Innovation Discussion**: Refine ideas and identify unique aspects
4. **Patent Drafting**: Create comprehensive patent application
5. **Quality Review**: Review for quality and compliance
6. **Final Rewrite**: Implement feedback and improvements

## Output

The system generates:

- **Progress Files**: Incremental content in `/workspace/output/progress/`
- **Final Patent**: Complete patent application in Markdown format
- **Logs**: Detailed execution logs in `/workspace/output/logs/`

## Development

### Project Structure

```
patent_agent_demo/
├── agents/                 # Agent implementations
│   ├── base_agent.py      # Base agent class
│   ├── planner_agent.py   # Planning agent
│   ├── searcher_agent.py  # Search agent
│   ├── discusser_agent.py # Discussion agent
│   ├── writer_agent.py    # Writing agent
│   ├── reviewer_agent.py  # Review agent
│   ├── rewriter_agent.py  # Rewrite agent
│   └── coordinator_agent.py # Coordination agent
├── message_bus.py         # Message passing infrastructure
├── patent_agent_system.py # Main system class
├── glm_client.py          # Google A2A client
├── main.py               # CLI interface
└── run_patent_workflow.py # Workflow runner
```

### Adding New Agents

1. Create a new agent class inheriting from `BaseAgent`
2. Implement the `execute_task` method
3. Register the agent in `PatentAgentSystem`
4. Update workflow configuration

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=patent_agent_demo
```

## Performance

The system is optimized for:

- **Concurrent Processing**: Multiple agents work simultaneously
- **Efficient Communication**: Message Bus for fast inter-agent communication
- **Resource Management**: Optimized API usage and memory management
- **Scalability**: Modular design for easy scaling

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure `ZHIPUAI_API_KEY` is set correctly
2. **Network Issues**: Check internet connectivity for API calls
3. **Memory Issues**: Monitor system resources during execution
4. **Timeout Issues**: Adjust timeout settings in configuration

### Logs

Check logs in `/workspace/output/logs/` for detailed error information:

- `system.log`: Main system logs
- `*_agent.log`: Individual agent logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google A2A team for the AI capabilities
- Message Bus team for the messaging framework
- Open source community for various dependencies