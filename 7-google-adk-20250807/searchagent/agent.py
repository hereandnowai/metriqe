from google.adk.agents import Agent
from google.adk.tools import google_search
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

search_agent = Agent(
    model='gemini-2.0-flash-001',
    name='search_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions using the google search tool',
    tools=[google_search]
)

root_agent= search_agent