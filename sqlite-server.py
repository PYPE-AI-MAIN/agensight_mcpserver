# server.py
import os
import glob
import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from mcp.server.fastmcp import FastMCP


# Create an MCP server
mcp = FastMCP("AgentAnalyzer")

# New tool to generate the agent UI and analyze the repository
@mcp.tool()
def echo_prompt() -> str:
    """Create an echo prompt"""
    message = """
    
    """
    return message

# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")

