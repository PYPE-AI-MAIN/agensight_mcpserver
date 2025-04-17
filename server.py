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
code_workflow_yaml = """  
    # --- inside ingestion.agents ---
- name: MyAgent                    # look in the code for the variable name of the agent
  module: path.to.MyAgentModule    # Python import path for your class
  description: ""                  # short human‑readable summary
  prompt: |                        # system/user prompt template
    # your prompt here
  tools:                           # list of method names this agent exposes if functions are provided else not required
    - tool_method_1
    - tool_method_2
  model:
    api: ""                        # e.g. OpenAI, Anthropic, etc.
    model: ""                      # refer this in the code - model identifier, e.g. gpt-4o-mini
    parameters:                    # any params
      temperature: 
      max_tokens: 
      # …etc.
  function_code:                   # stub implementations for each tool if tool is provided else not required
    tool_method_1: |
      def tool_method_1(self, ...):
          \"\"\"Describe what this does\"\"\"
          # your code here
          ...
    tool_method_2: |
      def tool_method_2(self, ...):
          \"\"\"Describe what this does\"\"\"
          # your code here
          ...
"""

gradio_app_structure = '''
import gradio as gr
import json
import tempfile
import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont
import io

# Add support for .env files
try:
    from dotenv import load_dotenv
    # Load .env file from project root
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(dotenv_path)
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed. Install with: pip install python-dotenv")
    print("Continuing without .env support...")

# Add parent directory to path if needed so 'src' can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Check if graphviz is installed and import it only if available
GRAPHVIZ_AVAILABLE = False
try:
    subprocess.run(["dot", "-V"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except (subprocess.SubprocessError, FileNotFoundError, ImportError):
    print("⚠️ WARNING: Graphviz not found on your system!")
    print("Please install Graphviz before running this application:")
    print("   - On macOS: brew install graphviz")
    print("   - On Ubuntu/Debian: sudo apt-get install graphviz")
    print("   - On Windows: choco install graphviz or download from https://graphviz.org/download/")
    print("\nFalling back to a simple text-based visualization.")

# Agent configurations with exact prompts from code
AGENT_CONFIGS = {
    "EntityExtractorAgent": {
        "description": "Extracts structured product information from text input",
        "prompt": """Extract the following fields from the product specification and return them in this exact JSON format:
{
    "brand": "extracted brand name or empty string if not found",
    "product": "main product name/type",
    "variant": "variant information like size/color/model or empty string if not found",
    "specification": "all technical specifications as a single string, separated by commas"
}

Guidelines:
- All fields must be strings
- For specification, combine all technical details into a single comma-separated string
- If a field is not found, use an empty string ("")
- Do not use nested objects or arrays""",
        "tools": ["extract_entities", "process_single", "process_batch"],
        "model": {
            "api": "OpenAI",
            "model": "gpt-4",
            "parameters": {
                "temperature": 0.1,
                "max_tokens": 500
            }
        },
        "function_code": {
            "extract_entities": """def extract_entities(self, text: str) -> ProductSpecification:
    \"\"\"Extract product entities from the given text.\"\"\"
    try:
        # Call OpenAI API to extract structured data from text
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": \"\"\"Extract the following fields from the product specification...\"\"\"
                },
                {"role": "user", "content": text}
            ]
        )
        
        # Process response into ProductSpecification object
        # Check for missing fields and validate format
        # Return structured data object
        
        return spec
        
    except Exception as e:
        # Error handling
        raise
""",
            "process_single": """def process_single(self, description: str) -> dict:
    \"\"\"Process a single product description.\"\"\"
    spec = self.extract_entities(description)
    return {
        "brand": spec.brand,
        "product": spec.product,
        "variant": spec.variant,
        "specification": spec.specification,
        "is_incomplete_specs": spec.is_incomplete_specs,
        "incomplete_fields": spec.incomplete_fields
    }
""",
            "process_batch": """def process_batch(self, csv_path: str) -> pd.DataFrame:
    \"\"\"Process a batch of product specifications from a CSV file.\"\"\"
    try:
        # Read CSV file
        # For each row, extract entities
        # Return results as DataFrame
        
        return pd.DataFrame(results)
        
    except Exception as e:
        # Error handling
        raise
"""
        }
    },
    "WebSearchAgent": {
        "description": "Searches the web for product information",
        "prompt": """Generate a concise search keyword (3-4 words) for a product based on its specification.
Focus on the most distinctive and searchable aspects.
Do not include general terms like "buy" or "price".
Return ONLY the search keyword, no other text.""",
        "tools": ["generate_search_keyword", "search_web"],
        "model": {
            "api": "OpenAI + Tavily",
            "model": "gpt-4",
            "parameters": {
                "temperature": 0.2,
                "max_results": 5,
                "search_depth": "basic"
            }
        },
        "function_code": {
            "generate_search_keyword": """def generate_search_keyword(self, spec: ProductSpecification) -> str:
    \"\"\"Generate a search keyword from product specification.\"\"\"
    try:
        # Create prompt with product info
        # Call OpenAI API to generate search keywords
        # Return optimized search term
        
        return search_keyword
        
    except Exception as e:
        # Error handling
        raise
""",
            "search_web": """def search_web(self, spec: ProductSpecification) -> WebSearchResult:
    \"\"\"Perform web search using Tavily.\"\"\"
    try:
        # Generate search keyword
        # Call Tavily API to search web
        # Process and filter results
        # Return structured search results
        
        return WebSearchResult(
            search_keyword=search_keyword,
            search_results=processed_results
        )
        
    except Exception as e:
        # Error handling
        raise
"""
        }
    },
    "SummarizerAgent": {
        "description": "Generates a concise product description",
        "prompt": """Based on the product information and web search results, create a factual product description that:
1. Focuses on technical specifications and features
2. Avoids marketing language 
3. Combines information from specifications and relevant web search results
4. Is EXACTLY 400 characters long (not counting spaces)
5. Uses simple, clear language""",
        "tools": ["generate_description"],
        "model": {
            "api": "OpenAI",
            "model": "gpt-4",
            "parameters": {
                "temperature": 0.2,
                "max_tokens": 500
            }
        },
        "function_code": {
            "generate_description": """def generate_description(self, product: ProductDescription) -> str:
    \"\"\"Generate a concise product description.\"\"\"
    try:
        # Create prompt with product specs and search results
        # Call OpenAI API to generate description
        # Ensure correct length and format
        # Return final description
        
        return description
        
    except Exception as e:
        # Error handling
        raise
"""
        }
    }
}

# Map for agent processes
def process_entity_extractor(input_text, api_key=None):
    """Process input through EntityExtractorAgent."""
    if not input_text.strip():
        return json.dumps({"error": "Please enter product text."})
    
    import os
    import sys
    
    # Make sure src is in the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Use API key from param or env var
    if not api_key or not api_key.strip():
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return json.dumps({"error": "OpenAI API key not found. Please provide it in the UI or set it in a .env file."})
    
    os.environ["OPENAI_API_KEY"] = api_key
    
    try:
        # Try direct import first
        try:
            from src.agents.entity_extractor import EntityExtractorAgent
        except ImportError:
            # If that fails, try importing without 'src' prefix
            from agents.entity_extractor import EntityExtractorAgent
        
        # Use the actual agent
        agent = EntityExtractorAgent()
        try:
            result = agent.extract_entities(input_text)
            
            # Convert to JSON-serializable dict
            output = {
                "brand": result.brand,
                "product": result.product,
                "variant": result.variant,
                "specification": result.specification,
                "is_incomplete_specs": result.is_incomplete_specs,
                "incomplete_fields": result.incomplete_fields
            }
            
            return json.dumps(output, indent=2)
        except Exception as e:
            # Handle specific extraction errors
            return json.dumps({
                "error": "Could not extract product information. Please provide a valid product description.",
                "details": str(e)
            }, indent=2)
            
    except ImportError as e:
        return json.dumps({"error": f"ImportError: {str(e)}. Make sure all dependencies are installed."}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error executing agent: {str(e)}"}, indent=2)

def process_web_search(input_text, api_key=None):
    """Process input through WebSearchAgent."""
    if not input_text.strip():
        return json.dumps({"error": "Please enter product text or JSON."})
    
    import os
    import sys
    
    # Make sure src is in the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Use API key from param or env var
    if not api_key or not api_key.strip():
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return json.dumps({"error": "OpenAI API key not found. Please provide it in the UI or set it in a .env file."})
    
    os.environ["OPENAI_API_KEY"] = api_key
    
    try:
        # Try direct import first
        try:
            from src.agents.entity_extractor import EntityExtractorAgent
            from src.agents.web_search import WebSearchAgent
            from src.models.product import ProductSpecification
        except ImportError:
            # If that fails, try importing without 'src' prefix
            from agents.entity_extractor import EntityExtractorAgent
            from agents.web_search import WebSearchAgent
            from models.product import ProductSpecification
'''


# New tool to generate the agent UI and analyze the repository
@mcp.tool()
def pype_agentic_workflow() -> str:
    
    """Create an echo prompt"""
    message = """
      You are a gradio app designer who designs brilliant dynamic AI agent experimenting platform.
      Follow the instructions below to create a agent experimentation platform gradio app.

      
      Step 1: Given a bolierplate code for workflow.yaml: `{code_workflow_yaml}`, analyze the code and understand what you will need to fill this bolierplate code to make it work.
      Step 2: Go through the user's code-base to undersatnd the AI agent. Understand the agent's purpose, tools (function calling), and capabilities it uses.

      Step 3: Follow the terminology to help you understand LangGraph concepts and how they apply to agent workflows:
        - StateGraph: The core component defining the structure of an agent as a state machine
        - State: A TypedDict defining the schema and reducers for handling state updates
        - Nodes: Functions that process state and perform units of work
        - Edges: Define transitions between nodes in the graph
        - START/END: Special markers for entry and exit points
        - Reducers: Functions that determine how state updates are processed (e.g., add_messages)
        - Checkpointing: Feature allowing time-travel and exploring alternative paths
        - Compilation: Process of creating a runnable graph from the builder

      Step 4: Adjust the bolierplate code for workflow.yaml to the user's code-base based on your understanding from step 2 and 3.
      
      Step 5: An example structure of the gradio app is as follows. An image is also attached as an example to help you understand how the app should look like. gradio app structure: `{gradio_app_structure}`. Follow this structure, the app should look exactly like this but adjusted to the user's agent workflow as you defined in step 4 in workflow.yaml.

      Step 6: Create only a file gradio_app.py that implements the gradio app structure.
      Step 7: add following features to the gradio app:
        - make the graphviz elements clickable
        - when clicked, it should show the description, prompt, tool, model parameters all having separate editable blocks
        - the agents should be runnable, call the functions in the gradio app so these agents can be tested directly from here.
        - give an option to run the python file gradio_app.py
      Step 8: Do not change anything in any other files than gradio_app.py. No Readme.md file should be created.
      Step 9: Just return the gradio_app.py file content as a response and install all the dependencies needed to run the gradio app.
    """
    return message

# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")

