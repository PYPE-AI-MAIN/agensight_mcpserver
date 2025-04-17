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



# Basic addition tool (keeping your original functionality)
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a dynamic greeting resource (keeping your original functionality)
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# New tool to generate the agent UI and analyze the repository
@mcp.tool()
def generate_agent_ui() -> str:
    """
    Generate agent UI and analyze the pype directory for agent insights.
    Creates a ~/pype folder if it doesn't exist.
    Returns insights about agents and their relationships.
    """
    # Create pype folder in home directory if it doesn't exist
    home_dir = str(Path.home())
    pype_dir = os.path.join(home_dir, "pype")
    
    if not os.path.exists(pype_dir):
        os.makedirs(pype_dir)
        return f"Created pype directory at {pype_dir}. Please add agents to this directory and run this tool again."
    
    # Analyze the directory for agents
    agent_insights = analyze_pype_directory(pype_dir)
    
    # Generate graph of agent relationships
    if agent_insights:
        generate_agent_graph(agent_insights, pype_dir)
        return f"Analysis complete. Found {len(agent_insights)} agents. Graph saved to {pype_dir}/agent_graph.png"
    else:
        return f"No agents found in {pype_dir}. Please add agents and run this tool again."

# Helper function to analyze the pype directory
@mcp.tool()
def analyze_pype_directory(directory_path: str) -> list:
    """
    Recursively analyze files in the pype directory to extract agent insights.
    Returns a list of agent information dictionaries.
    """
    agent_insights = []
    
    # Recursively search for Python files or JSON configurations
    for file_path in glob.glob(f"{directory_path}/**/*.py", recursive=True) + glob.glob(f"{directory_path}/**/*.json", recursive=True):
        # Read file content
        with open(file_path, 'r') as file:
            content = file.read()
            
        # Extract agent information (simplified example - enhance based on actual file formats)
        agent_info = extract_agent_info(content, file_path)
        if agent_info:
            agent_insights.append(agent_info)
    
    # Save insights to a JSON file
    insights_path = os.path.join(directory_path, "agent_insights.json")
    with open(insights_path, 'w') as f:
        json.dump(agent_insights, f, indent=2)
        
    return agent_insights

# Helper function to extract agent information from file content
def extract_agent_info(content: str, file_path: str) -> dict:
    """
    Extract agent information from file content.
    Returns a dictionary with agent details or None if no agent is found.
    """
    # This is a placeholder implementation - customize based on your agent file structure
    agent_info = {
        "name": os.path.basename(file_path).split('.')[0],
        "file_path": file_path,
        "description": "",
        "capabilities": [],
        "dependencies": [],
        "connections": []
    }
    
    # Look for descriptions in comments or docstrings
    if '"""' in content:
        doc_start = content.find('"""')
        doc_end = content.find('"""', doc_start + 3)
        if doc_end > doc_start:
            agent_info["description"] = content[doc_start+3:doc_end].strip()
    
    # Look for imports to determine dependencies
    if 'import' in content:
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith(('import', 'from')):
                parts = line.split()
                if len(parts) >= 2:
                    dependency = parts[1].split('.')[0]
                    if dependency not in ('os', 'sys', 'json', 'glob', 'pathlib'):
                        agent_info["dependencies"].append(dependency)
    
    # Determine connections based on references to other agents
    # This is highly dependent on your specific agent implementation
    # and would need to be customized
    
    return agent_info

# Helper function to generate a graph of agent relationships
@mcp.tool()
def generate_agent_graph(agent_insights: list, output_dir: str) -> None:
    """
    Generate a graph showing how agents interact and depend on each other.
    Saves the graph as a PNG file in the output directory.
    """
    G = nx.DiGraph()
    
    # Add nodes for each agent
    for agent in agent_insights:
        G.add_node(agent["name"])
    
    # Add edges for dependencies and connections
    for agent in agent_insights:
        for dependency in agent["dependencies"]:
            if any(a["name"] == dependency for a in agent_insights):
                G.add_edge(agent["name"], dependency, type="dependency")
        
        for connection in agent["connections"]:
            if any(a["name"] == connection for a in agent_insights):
                G.add_edge(agent["name"], connection, type="connection")
    
    # Create the visualization
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color="lightblue")
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7)
    nx.draw_networkx_labels(G, pos, font_size=10)
    
    plt.title("Agent Interactions Graph")
    plt.axis("off")
    
    # Save the graph
    graph_path = os.path.join(output_dir, "agent_graph.png")
    plt.savefig(graph_path)
    plt.close()

# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")

