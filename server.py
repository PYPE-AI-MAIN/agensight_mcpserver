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
def pype_agentic_workflow() -> str:
    
    """Create an echo prompt"""
    message = """
    You are an advanced agent information extractor tasked with scanning a directory to gather detailed information about AI agents. After analyzing the directory structure and agent workflows, you will generate a configuration JSON file containing the following details:

    - The name of each agent.
    - The prompts each agent uses, including the template and variables.
    - The tools used by each agent.
    - The connections between the agents, specifying their type (instantiation, transition, etc.).

    Follow the steps below to scan the directory and generate the required `prompt.config.json`:

    **Step 1:** Analyze the directory structure to identify each agent file. For each agent, extract the following information:
    - The agent's name.
    - The prompt templates used by the agent and the variables within each template.
    - The tools used by the agent (such as `log_abuse_check`, `model_predict`, etc.).

    **Step 2:** Identify any connections between agents (such as instantiations or transitions). For each connection, gather the following details:
    - The source agent (from).
    - The destination agent (to).
    - The connection type (e.g., `instantiation`, `transition`).

    **Step 3:** Format the extracted information into a JSON structure with the following format:

    ```json
    {
    "agents": [
        {
        "name": "<agent_name>",
        "prompts": [
            {
            "template": "<prompt_template>",
            "variables": ["<variable1>", "<variable2>", ...],
            "tools": ["<tool1>", "<tool2>", ...]
            }
        ]
        },
        ...
    ],
    "connections": [
        {
        "from": "<source_agent_name>",
        "to": "<destination_agent_name>",
        "type": "<connection_type>"
        },
        ...
    ]
    }

    Step 4: Save the generated JSON structure as prompt.config.json and return the content as your response.

    Step 5: Do not include any unnecessary information other than the JSON structure. Example of a generated prompt.config.json:

    Step 6: Once you have extracted the required information, save it as prompt.config.json and return it.

    """
    return message

# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")

