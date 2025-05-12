# Pype Agentic MCP Server

A Machine Conversation Protocol (MCP) server that analyzes codebases to extract agent information and generate structured workflows.

## Installation

```bash
# Clone the repository
git clone git@github.com:PYPE-AI-MAIN/agensight_mcp_server.git
cd agensight_mcp_server

# Create a virtual environment (optional but recommended)
python -m venv mcp-env
source mcp-env/bin/activate  # On Windows: mcp-env\Scripts\activate

# Install dependencies
pip install mcp-server
```

## Setting up with Cursor

1. Create or edit your Cursor MCP configuration file:
```bash
mkdir -p ~/.cursor
touch ~/.cursor/mcp.json
```

2. Add this configuration to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "sqlite-server": {
      "command": "/path/to/your/python",
      "args": [
        "/path/to/agensight_mcp_server/server.py"
      ],
      "description": "tool to generate agensight config"
    }
  }
}
```

3. Replace the paths with your actual paths:
   - `/path/to/your/python`: Path to your Python executable (use the virtual env path if created)
   - `/path/to/agensight_mcp_server/server.py`: Full path to the server.py file

4. Restart Cursor to load the new configuration

## Usage in Cursor

Once configured, you can use the tool directly in Cursor by asking:

"Please analyze this codebase using the pype_agentic_workflow MCP tool"

The tool will:
- Scan your codebase to identify AI agents
- Extract prompt templates
- Identify tools used by agents
- Map connections between agents
- Generate an `agensight.config.json` file with all extracted information

## Features

- **Agent Discovery**: Automatically identifies AI agents in your codebase
- **Prompt Extraction**: Locates and extracts the full text of prompt templates
- **Tool Identification**: Maps all tools used by each agent
- **Connection Mapping**: Visualizes how agents interact with each other
- **JSON Output**: Generates a structured configuration file for easy integration

## How It Works

The server uses the Machine Conversation Protocol to provide a tool that analyzes your codebase. When invoked, it:

1. Recursively scans all files in your project
2. Identifies classes and functions that interact with LLMs
3. Extracts complete prompt templates by following variable references
4. Maps the connections between agents
5. Outputs a structured JSON configuration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
