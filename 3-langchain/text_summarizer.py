from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()
google_api_key = os.getenv("GEMINI_API_KEY")

def text_summarizer():
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key)
    prompt_template = "Summarize the give text: \n\n {text}\n\n Summary: "
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()

    with open("profile-of-hereandnowai.txt", "r") as f:
        long_text = f.read()

    summary = chain.invoke({"text": long_text})
    print(summary)

if __name__ == "__main__":
    text_summarizer()
