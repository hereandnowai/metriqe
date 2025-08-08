import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run():
    # Connect to FastMCP server via SSE
    async with sse_client("http://127.0.0.1:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
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
