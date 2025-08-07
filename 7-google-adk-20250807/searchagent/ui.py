from agent import search_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
import google.genai as genai

import warnings
import gradio as gr

warnings.filterwarnings("ignore")

session_service = InMemorySessionService()
APP_NAME = "search_agent_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

async def run_conversation(query):
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    runner = Runner(
        agent=search_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    content = genai.types.Content(role='user', parts=[genai.types.Part(text=query)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.content and event.content.parts:
            yield event.content.parts[0].text
        if event.is_final_response():
            break


async def gradio_stream(query, history):
    result = ""
    async for response in run_conversation(query):
        if response is not None:
            result += str(response)
    return result


with gr.ChatInterface(gradio_stream, title="Chat with a Google Agent and see its thoughts") as demo:
    pass

if __name__ == "__main__":
    demo.launch()

    