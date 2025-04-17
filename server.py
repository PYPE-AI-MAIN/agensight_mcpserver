# mcp-server/server.py

from mcp.server.fastmcp import FastMCP
import os
import json
import ast
from typing import Dict, List, Any

# Create an MCP server
mcp = FastMCP("Demo")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Agent Analyzer
class AgentAnalyzer:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.agents: List[Dict[str, Any]] = []

    def analyze_repository(self):
        """Analyze the repository for agent definitions and their prompts."""
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    self._analyze_file(os.path.join(root, file))

    def _analyze_file(self, file_path: str):
        """Analyze a Python file for agent definitions."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Look for agent class definitions
                        if 'Agent' in node.name or 'agent' in node.name.lower():
                            agent_info = self._extract_agent_info(node, file_path)
                            if agent_info:
                                self.agents.append(agent_info)
        except Exception as e:
            print(f"Error analyzing file {file_path}: {str(e)}")

    def _extract_agent_info(self, node: ast.ClassDef, file_path: str) -> Dict[str, Any]:
        """Extract information about an agent from its class definition."""
        agent_info = {
            "name": node.name,
            "file": file_path,
            "methods": [],
            "prompts": [],
            "tools": []
        }

        # Extract methods and docstrings
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    "name": item.name,
                    "docstring": ast.get_docstring(item) or "",
                    "parameters": [arg.arg for arg in item.args.args]
                }
                agent_info["methods"].append(method_info)

        return agent_info

    def save_to_pype(self):
        """Save agent information to the pype directory."""
        pype_dir = os.path.join(self.root_dir, 'pype')
        os.makedirs(pype_dir, exist_ok=True)

        # Save agent information
        with open(os.path.join(pype_dir, 'agents.json'), 'w') as f:
            json.dump(self.agents, f, indent=2)

# Add a tool to generate the agent UI
@mcp.tool()
def generate_agent_ui():
    """Analyze the repository and generate the agent UI."""
    analyzer = AgentAnalyzer(os.getcwd())
    analyzer.analyze_repository()
    analyzer.save_to_pype()
    return "Agent UI generated successfully"
