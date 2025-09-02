# Medium MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to seamlessly fetch Medium articles and user data. Built with the official MCP Python SDK and the `medium-api` library for robust integration with Claude, ChatGPT, and other MCP-compatible AI tools.

> ⚠️ **WARNING**: This is an experimental MCP server for educational purposes. Use responsibly and respect Medium's Terms of Service and rate limits. Not recommended for production use.

> 🚫 **RATE LIMITING NOTICE**: This server does **NOT** implement automatic rate limiting, throttling, or retry mechanisms. It only detects rate limit errors and reports them. Users must manually manage API usage to avoid exceeding RapidAPI quotas.

## Features

- 🔍 **User Information**: Get detailed user profiles, follower counts, and bio information
- 📰 **Article Access**: Fetch articles with full content in text, HTML, or Markdown formats
- 🔥 **Trending Content**: Get top feeds and trending articles by tags
- 🔎 **Search Functionality**: Search articles by keywords
- 🛡️ **Error Handling**: Comprehensive error handling with meaningful messages
- ⚡ **Error Detection**: Rate limit error detection and user-friendly messages
- 🔐 **Secure Configuration**: Environment-based API key management
- 🚀 **MCP CLI Support**: Easy deployment with the official MCP command-line interface

## Quick Start

### Prerequisites

- Python 3.10+
- RapidAPI account with Medium API subscription

### Installation

```bash
# Clone the repository
git clone https://github.com/marcus912/medium-mcp.git
cd medium-mcp

# Install the package
pip install -e .
```

### Configuration

1. **Get your RapidAPI Key:**
   - Sign up at [RapidAPI](https://rapidapi.com/)
   - Subscribe to [Unofficial Medium API](https://rapidapi.com/nishujain199719-vgIfuFHZxVZ/api/medium2)
   - Copy your API key from the dashboard

2. **Set environment variable:**
   ```bash
   export RAPIDAPI_KEY="your_rapidapi_key_here"
   ```

3. **Install dependencies and run the server:**
   
   **Option 1: Using uv (Recommended):**
   ```bash
   # Install dependencies and create virtual environment
   uv sync
   
   # Run with inspector for development
   uv run mcp dev main.py
   
   # Or run without inspector
   uv run mcp run main.py
   ```
   
   **Option 2: Using pip:**
   ```bash
   # Install with CLI support
   pip install -e ".[cli]"
   
   # Run with inspector for development
   mcp dev main.py
   
   # Or run without inspector
   mcp run main.py
   ```

## MCP Server Configuration

To use this server with Claude Desktop or other MCP clients, add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "medium-mcp": {
      "command": "/Library/Frameworks/Python.framework/Versions/3.10/bin/uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with",
        "pydantic",
        "--with",
        "medium-api",
        "mcp",
        "run",
        "/path/to/medium-mcp/main.py"
      ],
      "env": {
        "RAPIDAPI_KEY": "your_rapidapi_key_here",
        "MAX_ARTICLES_PER_REQUEST": "3"
      }
    }
  }
}
```

**Configuration Notes:**
- Replace `/path/to/medium-mcp/main.py` with your actual project path
- Replace `"your_rapidapi_key_here"` with your actual RapidAPI key
- Adjust `/Library/Frameworks/Python.framework/Versions/3.10/bin/uv` to match your uv installation path
- Restart Claude Desktop after updating the configuration

## Usage Examples

### Get Article Content
```python
# Tool: get_article_content
{
  "article_id": "abc123def456",
  "format": "markdown"
}
```

### Get Trending Articles
```python
# Tool: get_top_feeds
{
  "tag": "ai",
  "mode": "hot",
  "count": 3
}
```

### Get User Information
```python
# Tool: get_user_info
{
  "username": "tim_cook"
}
```

### Fetch User Articles
> ⚠️ **API Usage Warning**: This function will consume API requests proportional to the number of articles published by the user. The cost increases significantly for prolific authors with hundreds or thousands of published articles.

```python
# Tool: get_user_articles  
{
  "username": "username_here",
  "count": 3
}
```

### Search Articles
```python
# Tool: search_articles
{
  "query": "artificial intelligence",
  "count": 3
}
```

## Example Prompts for AI Assistants

Here are some practical prompts you can use with Claude or other AI assistants when this MCP server is configured:

### Research and Analysis
```
"Find the latest trending articles about machine learning on Medium and summarize the key insights from the top 3 articles."
```

```
"Get information about the Medium user @andrewng including his profile details, follower count, and bio information."
```

### Content Discovery
```
"I'm interested in learning about GPT models. Search Medium for recent articles about GPT and give me the full content of the most promising one in markdown format."
```

```
"Show me what's trending in the 'programming' tag this week and help me identify the most practical tutorial among them."
```

### Member-Only Content Access
```
"I found this Medium article but it's behind a paywall: https://medium.com/coding-nexus/no-more-guesswork-how-autorag-finds-the-best-rag-setup-for-you-6cda0e7c6dca 
Can you get the full content for me and provide a detailed summary?"
```

### Topic Deep Dive
```
"Search for articles about 'transformer architecture' and get the full content of the 3 most comprehensive ones. Then create a learning roadmap based on the combined insights."
```


## Configuration Options

Set these environment variables to customize behavior:

```bash
RAPIDAPI_KEY=your_key_here           # Required: Your RapidAPI key
MAX_ARTICLES_PER_REQUEST=3           # Optional: Max articles per request (1-100)
```

## Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/yourusername/medium-mcp.git
cd medium-mcp
pip install -e ".[dev,cli]"

# Run tests
pytest

# Format code
black src/
isort src/

# Type checking
mypy src/

# Test with MCP CLI and Inspector
mcp dev main.py
```

### Project Structure

```
medium-mcp/
├── main.py                 # Standalone MCP server entry point
├── src/medium_mcp/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # CLI entry point
│   ├── server.py            # Main MCP server implementation
│   ├── client.py            # Medium API client wrapper
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic data models and types
│   ├── formatting.py        # String formatting utilities
│   └── utils.py             # General utility functions
├── tests/
│   ├── __init__.py          # Test package initialization
│   ├── test_server.py       # Server function tests
│   ├── test_client.py       # Client wrapper tests
│   ├── test_config.py       # Configuration tests
│   ├── test_types.py        # Data model tests
│   ├── test_formatting.py   # Formatting utility tests
│   └── test_utils.py        # General utility tests
├── .env.example            # Environment variables template
├── Makefile               # Development shortcuts
├── pyproject.toml         # Project configuration and dependencies
├── pytest.ini            # Test configuration
├── uv.lock               # Dependency lock file
└── README.md             # This file
```

## Error Handling

The server provides comprehensive error handling for common scenarios:

- **Invalid API Key**: Clear message with setup instructions
- **Rate Limiting**: Rate limit error detection with user-friendly messages (no automatic retries or throttling)  
- **Network Issues**: Timeout and connectivity error handling
- **Not Found**: Graceful handling of missing users/articles
- **Validation Errors**: Input parameter validation with helpful messages

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Format code: `black src/ && isort src/`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with the official [MCP Python SDK v1.13.1](https://github.com/modelcontextprotocol/python-sdk)
- Built on the excellent [medium-api](https://github.com/weeping-angel/medium-api) library
- Powered by [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Inspired by the need for seamless AI-powered content research

## Support

- 📝 [Documentation](https://github.com/marcus912/medium-mcp)
- 🐛 [Issues](https://github.com/marcus912/medium-mcp/issues)
- 💬 [Discussions](https://github.com/marcus912/medium-mcp/discussions)
