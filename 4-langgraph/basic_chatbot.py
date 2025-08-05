from typing import Annotated
from typing_extensions import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os
from config import MODEL

load_dotenv()
google_api_key = os.getenv("GEMINI_API_KEY")
model = MODEL

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    llm = ChatGoogleGenerativeAI(model=model, google_api_key=google_api_key)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Graph Creation
graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.set_entry_point("chatbot")
graph.set_finish_point("chatbot")

app = graph.compile()

print("Chatbot - Type 'quit' to exit")
while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    response = app.invoke({"messages": [("human", user_input)]})
    print("Jarvis:", response["messages"][-1].content)