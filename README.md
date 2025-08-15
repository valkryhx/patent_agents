# Patent Agent Demo

A sophisticated multi-agent system for automated patent development, featuring intelligent planning, research, discussion, writing, and review capabilities with OpenAI GPT-5 and GLM-4.5 fallback support.

## 🚀 Features

- **Multi-Agent Architecture**: Coordinated agents for different patent development stages
- **Message Bus Integration**: High-performance message passing and coordination
- **OpenAI GPT-5 Integration**: Advanced AI-powered content generation with GLM-4.5 fallback
- **Comprehensive Workflow**: From planning to final patent draft
- **Quality Assurance**: Built-in review and rewrite cycles
- **Progress Tracking**: Real-time monitoring and incremental file generation
- **Smart Fallback**: Automatic fallback to GLM-4.5 when OpenAI quota is exceeded
- **Cross-Platform Support**: Works on Linux, Windows, and macOS

## 🏗️ System Architecture

The system consists of specialized agents working together:

- **Planner Agent**: Strategic planning and patent strategy development
- **Searcher Agent**: Prior art research and patent analysis with web search capabilities
- **Discusser Agent**: Innovation discussion and idea refinement
- **Writer Agent**: Patent drafting and technical writing
- **Reviewer Agent**: Quality review and compliance checking
- **Rewriter Agent**: Feedback implementation and improvement
- **Coordinator Agent**: Workflow orchestration and agent coordination

## 🛠️ Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API access (GPT-5) or GLM-4.5 API access
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

3. Set up API keys:

#### Option 1: OpenAI GPT-5 (Recommended)
```bash
# Linux/macOS
export OPENAI_API_KEY="your_openai_api_key_here"

# Windows (PowerShell)
$env:OPENAI_API_KEY="your_openai_api_key_here"

# Windows (CMD)
set OPENAI_API_KEY=your_openai_api_key_here
```

#### Option 2: GLM-4.5-flash (Fallback)
```bash
# Linux/macOS
export ZHIPUAI_API_KEY="your_glm_api_key_here"

# Windows (PowerShell)
$env:ZHIPUAI_API_KEY="your_glm_api_key_here"

# Windows (CMD)
set ZHIPUAI_API_KEY=your_glm_api_key_here
```

#### Option 3: Private Key Files (More Secure)
```bash
# Create private key files in the patent_agent_demo directory
echo "your_openai_api_key_here" > patent_agent_demo/private_openai_key
echo "your_glm_api_key_here" > patent_agent_demo/glm_api_key
```

4. Set patent topic and description:
```bash
# Linux/macOS
export PATENT_TOPIC="Your Patent Topic"
export PATENT_DESC="Your Patent Description"

# Windows (PowerShell)
$env:PATENT_TOPIC="Your Patent Topic"
$env:PATENT_DESC="Your Patent Description"

# Windows (CMD)
set PATENT_TOPIC=Your Patent Topic
set PATENT_DESC=Your Patent Description
```

5. Run the system:

#### Method 1: Direct CLI (Recommended)
```bash
python -m patent_agent_demo.main --topic "Your Patent Topic" --description "Your Patent Description"
```

#### Method 2: Interactive Mode
```bash
python -m patent_agent_demo.main --interactive
```

#### Method 3: Environment Variables
```bash
python -m patent_agent_demo.main
```

#### Method 4: Python Script
```bash
python run_patent_workflow.py
```

## 🔑 API Key Configuration

### OpenAI API Key Setup

1. **Get API Key**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Set Environment Variable**:
   ```bash
   # Linux/macOS
   export OPENAI_API_KEY="sk-..."
   
   # Windows PowerShell
   $env:OPENAI_API_KEY="sk-..."
   
   # Windows CMD
   set OPENAI_API_KEY=sk-...
   ```
3. **Or Use Private File**:
   ```bash
   echo "sk-..." > patent_agent_demo/private_openai_key
   ```

### GLM-4.5 API Key Setup

1. **Get API Key**: Visit [ZhipuAI Platform](https://open.bigmodel.cn/)
2. **Set Environment Variable**:
   ```bash
   # Linux/macOS
   export ZHIPUAI_API_KEY="your_glm_key_here"
   
   # Windows PowerShell
   $env:ZHIPUAI_API_KEY="your_glm_key_here"
   
   # Windows CMD
   set ZHIPUAI_API_KEY=your_glm_key_here
   ```
3. **Or Use Private File**:
   ```bash
   echo "your_glm_key_here" > patent_agent_demo/glm_api_key
   ```

### Fallback Mechanism

The system automatically falls back to GLM-4.5 when:
- OpenAI API quota is exceeded
- OpenAI API returns errors
- OpenAI is not available

When using GLM fallback, the searcher agent uses DuckDuckGo for free web search instead of OpenAI's web search tool.

## 📋 Workflow Stages

1. **Planning & Strategy**: Define patent strategy and approach
2. **Prior Art Search**: Research existing patents and technologies
3. **Innovation Discussion**: Refine ideas and identify unique aspects
4. **Patent Drafting**: Create comprehensive patent application
5. **Quality Review**: Review for quality and compliance
6. **Final Rewrite**: Implement feedback and improvements

## 📁 Output

The system generates:

- **Progress Files**: Incremental content in `/workspace/output/progress/`
- **Final Patent**: Complete patent application in Markdown format
- **Logs**: Detailed execution logs in `/workspace/output/logs/`

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI Configuration (Primary)
OPENAI_API_KEY=your_openai_api_key_here

# GLM Configuration (Fallback)
ZHIPUAI_API_KEY=your_glm_api_key_here

# Message Bus Configuration
MESSAGE_BUS_HOST=localhost
MESSAGE_BUS_PORT=8000

# Patent Configuration
PATENT_TOPIC="Your Patent Topic"
PATENT_DESC="Your Patent Description"
```

### Configuration Priority

1. **Environment Variables** (highest priority)
2. **Private Key Files** (fallback)
3. **Default Configuration** (lowest priority)

## 📊 Usage Examples

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

### Command Line Interface

```bash
# Run with specific topic and description
python -m patent_agent_demo.main --topic "AI Patent" --description "AI system description"

# Interactive mode
python -m patent_agent_demo.main --interactive

# Health check
python -m patent_agent_demo.main --health

# System status
python -m patent_agent_demo.main --status
```

### Advanced Usage

```bash
# Run with custom output directory
export OUTPUT_DIR="/custom/output/path"
python -m patent_agent_demo.main --topic "Patent Topic" --description "Description"

# Run with specific model preference
export PREFER_OPENAI=true  # Force OpenAI usage
export PREFER_GLM=true     # Force GLM usage
python -m patent_agent_demo.main --topic "Patent Topic" --description "Description"
```

## 🧪 Testing

### Test OpenAI Integration
```bash
python test_openai_key.py
```

### Test Fallback Mechanism
```bash
python test_fallback.py
```

### Test DuckDuckGo Search
```bash
python test_duckduckgo.py
```

### Run All Tests
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=patent_agent_demo
```

## 📈 Performance

The system is optimized for:

- **Concurrent Processing**: Multiple agents work simultaneously
- **Efficient Communication**: Message Bus for fast inter-agent communication
- **Resource Management**: Optimized API usage and memory management
- **Scalability**: Modular design for easy scaling
- **Smart Fallback**: Automatic API switching for optimal performance

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Quota Exceeded**: System automatically falls back to GLM-4.5
2. **API Key Issues**: Ensure API keys are set correctly in environment or private files
3. **Network Issues**: Check internet connectivity for API calls
4. **Memory Issues**: Monitor system resources during execution
5. **Timeout Issues**: Adjust timeout settings in configuration

### API Key Troubleshooting

```bash
# Check if OpenAI key is working
python test_openai_key.py

# Check if GLM key is working
export ZHIPUAI_API_KEY="your_key"
python -c "from patent_agent_demo.glm_client import GLMA2AClient; print('GLM key works')"

# Test fallback mechanism
python test_fallback.py
```

### Logs

Check logs in `/workspace/output/logs/` for detailed error information:

- `system.log`: Main system logs
- `*_agent.log`: Individual agent logs
- `openai_client.log`: OpenAI client logs
- `glm_client.log`: GLM client logs

## 🚀 Quick Examples

### Example 1: Basic Patent Generation
```bash
export OPENAI_API_KEY="sk-..."
export PATENT_TOPIC="证据图增强的检索增强RAG系统"
export PATENT_DESC="构建证据图以提升RAG可验证性与准确性"

python -m patent_agent_demo.main --topic "$PATENT_TOPIC" --description "$PATENT_DESC"
```

### Example 2: Windows PowerShell
```powershell
$env:OPENAI_API_KEY="sk-..."
$env:PATENT_TOPIC="AI Patent System"
$env:PATENT_DESC="Advanced AI system for patent analysis"

python -m patent_agent_demo.main --topic $env:PATENT_TOPIC --description $env:PATENT_DESC
```

### Example 3: Using Private Key Files
```bash
# Create key files
echo "sk-..." > patent_agent_demo/private_openai_key
echo "glm_key_here" > patent_agent_demo/glm_api_key

# Run without environment variables
python -m patent_agent_demo.main --topic "Patent Topic" --description "Description"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI team for GPT-5 capabilities
- ZhipuAI team for GLM-4.5 support
- Message Bus team for the messaging framework
- Open source community for various dependencies

## 📞 Support

For questions and support, please open an issue on GitHub.

---

**Happy Patent Development! 🚀📚**
