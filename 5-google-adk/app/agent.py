from google.adk.agents import Agent
import yfinance as yf
from google.adk.tools.tool_context import ToolContext

def get_stock_price(ticker: str, tool_context: ToolContext):
    stock = yf.Ticker(ticker)
    price = stock.info.get("currentPrice","price not available")

    if "recent_searches" not in tool_context.state:
        tool_context.state["recent_searches"] = []

    recent_searches = tool_context.state["recent_searches"]
    if ticker not in recent_searches:
        recent_searches.append(ticker)
        tool_context.state["recent_searches"] = recent_searches

    return {"price": price,"ticker":ticker }




tool_agent = Agent(
    model='gemini-2.0-flash-001',
    name='tool_agent',
    description='A helpful assistant in fetching the stock price',
    instruction="""you are an expert in stock exchange, always use the get_stock_price tool
    Include the ticker in your response
    """,
    tools=[get_stock_price]
)

root_agent = tool_agent
