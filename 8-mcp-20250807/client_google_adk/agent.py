# ./adk_agent_samples/mcp_client_agent/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters

PATH_TO_YOUR_MCP_SERVER_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "calculator_server.py"))

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='web_reader_mcp_client_agent',
    instruction="Use the 'load_web_page' tool to fetch content from a URL provided by the user.",
    tools=[MCPToolset(
            connection_params=StdioConnectionParams(
            server_params = StdioServerParameters(
            command='python', # Command to run your MCP server script
            args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT])))])