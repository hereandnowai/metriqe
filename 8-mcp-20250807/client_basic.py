from mcp import ClientSession , StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

server_params = StdioServerParameters(
            command= "python",
            args=["8-mcp-20250807/calculator_server.py"]
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read,write) as session:
            await session.initialize()

            tools = await session.list_tools()
            for tool in tools:
                print(f"- {tool}")
            expression = input("enter a math expression eg 4 * 5: ")

            result = await session.call_tool(
                "evaluate_expression",
                arguments={"expression":expression}
            )
            print(result.content[0].text)

if __name__ == "__main__":
    asyncio.run(run())