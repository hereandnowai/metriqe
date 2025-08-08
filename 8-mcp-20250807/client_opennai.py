import os
import json
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
from mcp.types import TextContent

# ————————————————————————————————
# Initialization
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
model = "gemini-2.5-flash-lite"

# MCP tool server configuration
server_params = StdioServerParameters(
    command="python",
    args=["/workspaces/metriqe/8-mcp-20250807/calculator_server.py"],
    env=None
)

# Helper to extract serializable result from CallToolResult
def extract_tool_payload(result) -> object:
    if getattr(result, "structured_content", None) is not None:
        return result.structured_content
    texts = []
    for block in result.content:
        if isinstance(block, TextContent):
            texts.append(block.text)
        else:
            texts.append(f"<{block.__class__.__name__}>")
    return "\n".join(texts) if len(texts) > 1 else (texts[0] if texts else None)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_list = await session.list_tools()
            tools = [{
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema
                }
            } for tool in tools_list.tools]

            user_query = input("Ask me anything (e.g., 'What’s 5 × 7?'): ")

            client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": user_query}],
                tools=tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            if message.tool_calls:
                for call in message.tool_calls:
                    name = call.function.name
                    args = json.loads(call.function.arguments)
                    result = await session.call_tool(name, args)

                    payload = extract_tool_payload(result)
                    followup = await client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "user", "content": user_query},
                            {"role": "assistant", "content": message.content},
                            {"role": "user", "content": json.dumps({"tool_result": payload})}
                        ]
                    )
                    print("→", followup.choices[0].message.content)
            else:
                print("→", message.content)

if __name__ == "__main__":
    asyncio.run(run())