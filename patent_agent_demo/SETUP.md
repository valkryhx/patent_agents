# Patent Agent Demo Setup Guide

This guide will help you set up and run the Patent Agent Demo system, a multi-agent platform for automated patent development using Message Bus and Google A2A.

## Prerequisites

- Python 3.8 or higher
- Git
- Access to Google A2A API
- Basic understanding of patent development process

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd patent_agent_demo
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# API Configuration
ZHIPUAI_API_KEY=your_zhipuai_api_key_here

# Message Bus Configuration
MESSAGE_BUS_HOST=localhost
MESSAGE_BUS_PORT=8000

# Patent Configuration
PATENT_TOPIC="Your Patent Topic"
PATENT_DESC="Your Patent Description"
```

### 4. Verify Installation

Run the health check to verify everything is set up correctly:

```bash
python -m patent_agent_demo.main --health
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ZHIPUAI_API_KEY` | Your ZhipuAI API key | Yes | - |
| `MESSAGE_BUS_HOST` | Message Bus host | No | localhost |
| `MESSAGE_BUS_PORT` | Message Bus port | No | 8000 |
| `PATENT_TOPIC` | Default patent topic | No | - |
| `PATENT_DESC` | Default patent description | No | - |

### System Configuration

The system can be configured through the main configuration file:

```python
# patent_agent_system.py
system = PatentAgentSystem()
await system.start()
```

## Usage

### Basic Usage

Run a patent development workflow:

```bash
python run_patent_workflow.py
```

### Interactive Mode

Run in interactive mode for step-by-step guidance:

```bash
python -m patent_agent_demo.main --interactive
```

### Command Line Options

```bash
# Run with specific topic and description
python -m patent_agent_demo.main --topic "AI Patent" --description "AI system description"

# Perform health check
python -m patent_agent_demo.main --health

# Show system status
python -m patent_agent_demo.main --status
```

## System Architecture

The Patent Agent Demo system consists of:

- **Message Bus**: Message passing and coordination framework
- **Google A2A**: AI-powered content generation
- **Multi-Agent System**: Specialized agents for different tasks
- **Workflow Engine**: Orchestration and progress tracking

### Agent Roles

1. **Planner Agent**: Strategic planning and patent strategy
2. **Searcher Agent**: Prior art research and analysis
3. **Discusser Agent**: Innovation discussion and refinement
4. **Writer Agent**: Patent drafting and technical writing
5. **Reviewer Agent**: Quality review and compliance checking
6. **Rewriter Agent**: Feedback implementation and improvement
7. **Coordinator Agent**: Workflow orchestration

## Workflow Stages

The patent development workflow consists of 6 main stages:

1. **Planning & Strategy**: Define patent strategy and approach
2. **Prior Art Search**: Research existing patents and technologies
3. **Innovation Discussion**: Refine ideas and identify unique aspects
4. **Patent Drafting**: Create comprehensive patent application
5. **Quality Review**: Review for quality and compliance
6. **Final Rewrite**: Implement feedback and improvements

## Output

The system generates several types of output:

### Progress Files

Incremental content is saved in `/workspace/output/progress/`:

- `00_title_abstract.md`: Patent title and abstract
- `01_outline.md`: Patent structure outline
- `02_background.md`: Background technology
- `03_summary.md`: Invention summary
- `04_claims.md`: Patent claims
- `05_desc_all.md`: Detailed description
- `06_drawings.md`: Technical diagrams
- `progress.md`: Combined progress file

### Final Patent

The complete patent application is exported as a Markdown file in the output directory.

### Logs

Detailed execution logs are saved in `/workspace/output/logs/`:

- `system.log`: Main system logs
- `*_agent.log`: Individual agent logs

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure `ZHIPUAI_API_KEY` is set correctly
   - Verify API key has sufficient credits
   - Check API key permissions

2. **Network Issues**
   - Verify internet connectivity
   - Check firewall settings
   - Ensure API endpoints are accessible

3. **Memory Issues**
   - Monitor system resources during execution
   - Consider reducing concurrent operations
   - Check for memory leaks

4. **Timeout Issues**
   - Adjust timeout settings in configuration
   - Check network latency
   - Consider using faster API endpoints

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `API key not found` | Missing or invalid API key | Set `ZHIPUAI_API_KEY` environment variable |
| `Connection timeout` | Network connectivity issues | Check internet connection and firewall |
| `Memory error` | Insufficient system memory | Close other applications or increase memory |
| `Agent not found` | Agent registration failed | Restart the system |

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
export LOG_LEVEL=DEBUG
python run_patent_workflow.py
```

## Performance Optimization

### System Requirements

- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM recommended
- **Storage**: 1GB+ free space
- **Network**: Stable internet connection

### Optimization Tips

1. **Concurrent Processing**: The system uses concurrent processing for better performance
2. **API Rate Limiting**: Respect API rate limits to avoid throttling
3. **Resource Management**: Monitor system resources during execution
4. **Caching**: Enable caching for repeated operations

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

### Adding New Features

1. **New Agents**: Inherit from `BaseAgent` and implement required methods
2. **New Workflow Stages**: Add stages to the coordinator agent
3. **New Output Formats**: Extend the writer agent
4. **New APIs**: Add new clients in the appropriate module

### Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=patent_agent_demo

# Run specific tests
pytest tests/test_planner_agent.py
```

## API Reference

### Main Classes

- `PatentAgentSystem`: Main system class
- `BaseAgent`: Base class for all agents
- `MessageBusConfig`: Message bus configuration
- `GLMA2AClient`: Google A2A client

### Key Methods

- `execute_workflow()`: Start a patent development workflow
- `get_workflow_status()`: Get workflow progress
- `health_check()`: Perform system health check
- `get_system_status()`: Get system status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:

- **Documentation**: Check the README and this setup guide
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## Acknowledgments

- Google A2A team for the AI capabilities
- Message Bus team for the messaging framework
- Open source community for various dependencies

## Changelog

### Version 1.0.0
- Initial release
- Multi-agent patent development system
- Message Bus integration
- Google A2A integration
- Comprehensive workflow management