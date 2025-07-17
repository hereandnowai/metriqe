from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
google_api_key = os.getenv("GEMINI_API_KEY")

def simple_chatbot():
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key)
    print("Caramel AI - Your friendly ai chatbot")
    print("You can ask anything your want or type quit to exit")
    while True:
        user_input = input("You: ")
        if user_input == "quit":
            break
        response = llm.invoke(user_input)
        print(f"Bot: {response.content}")

if __name__ == "__main__":
    simple_chatbot()