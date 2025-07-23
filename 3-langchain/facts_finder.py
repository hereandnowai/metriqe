# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain.tools import tool
from langchain_core.rate_limiters import InMemoryRateLimiter
from dotenv import load_dotenv
import os
import sys
# import time
from config import MODEL
import warnings

warnings.filterwarnings("ignore", message="API key must be provided when using hosted LangSmith API")

load_dotenv()
# google_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENROUTER")
model = MODEL

FACTS = {
    "capital of france": "Paris",
    "largest ocean": "Pacific Ocean",
    "inventor of telephone": "Alexander Graham Bell",
    "population of india": "Approximately 1.5 billion"
}

@tool
def get_fact(query: str) -> str:
     """
    Retrieves a fact from a predefined list. The query must be an exact match
    to one of the available facts.

    Available facts are:
    - 'capital of france'
    - 'largest ocean'
    - 'inventor of telephone'
    - 'population of india'
    """
     return FACTS.get(query.lower(), "Fact is not found")

def run_data_retrieval_agent():
    """
    Creates an agent that can use the get_fact tool.
    """
    
    # wait_time = 30
    # print(f"Jarvis is suiting up... He will be ready after {wait_time} seconds")
    # for i in range(wait_time, 0, -1):
    #     sys.stdout.write(f"\rPlease wait for {i} seconds...")
    #     sys.stdout.flush()
    #     time.sleep(1)
    # sys.stdout.write("\rJarvis is ready & running...             \n")

    rate_limiter = InMemoryRateLimiter(
        requests_per_second=0.1,
        check_every_n_seconds=0.1,
        max_bucket_size=1
    )

    # llm = ChatGoogleGenerativeAI(model=model, google_api_key=google_api_key, rate_limiter=rate_limiter).with_retry()
    llm = ChatOpenAI(model=model, openai_api_key=openai_api_key, base_url="https://openrouter.ai/api/v1/") 
    tools = [get_fact]
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                                   handle_parsing_errors=True)

    responses = []
    print("\n Question 1: Capital of France")
    responses.append(agent_executor.invoke({"input": "What is the capital of France?"}))

    print("\n Question 2: Largest Ocean")
    responses.append(agent_executor.invoke({"input": "What is the largest ocean in the world?"}))

    print("\n Final Answers")
    for i, response in enumerate(responses, 1):
        print(f"Response {i}: {response['output']}")

if __name__ == "__main__":
    run_data_retrieval_agent()