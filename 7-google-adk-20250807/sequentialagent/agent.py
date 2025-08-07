from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.agents import SequentialAgent

search_agent = Agent(
    model='gemini-2.0-flash-001',
    name='search_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions using the google search tool',
    tools=[google_search]
)

summarizing_agent = Agent(
     model='gemini-2.5-flash-lite',
     name = "summarizing_agent",
     description="An agent that summarizes the given data",
     instruction="summarize the data given to you for easy understanding by a 10 year old"
)

root_agent= SequentialAgent(
    name ="sequential_agent",
    description="you are a sequenetial agent",
    sub_agents=[search_agent,
                summarizing_agent]
)