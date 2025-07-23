from langchain.chat_models import init_chat_model
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain.tools import tool
from langchain_core.rate_limiters import InMemoryRateLimiter
import pytesseract 
from pdf2image import convert_from_path
import os
from dotenv import load_dotenv
from config import MODEL
import warnings
import sys

warnings.filterwarnings("ignore", message="API key must be provided when using hosted LangSmith API")

load_dotenv()
google_api_key = os.getenv("GEMINI_API_KEY")

model = MODEL

@tool(description="Extract text from the given scanned pdf using tesseract ocr. Provide the full file path")
def extract_text_from_scanned_pdf(pdf_path: str) -> str:
    """"This function extracts all the visible text from the scanned invoice pdf using tesseract ocr."""
    if not os.path.exists(pdf_path):
        return f"Error: file is found at {pdf_path}"
    try:
        text = ""
        for image in convert_from_path(pdf_path):
            text += pytesseract.image_to_string(image) + "\n"
        return text
    except Exception as e:
        return f"An error occurred: {e}"

def run_invoice_processing_agent():
    try:
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract not installed on your machine")
        sys.exit(1)

    rate_limiter = InMemoryRateLimiter(
        requests_per_second=0.1,
        check_every_n_seconds=0.1,
        max_bucket_size=1
    )

    llm = init_chat_model(
        model=model,
        model_provider="google-genai",
        google_api_key=google_api_key,
        rate_limiter=rate_limiter
    )

    tools = [extract_text_from_scanned_pdf]
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    invoice_pdf_path = os.path.join(BASE_DIR, "scanned_invoice.pdf")

    if not os.path.exists(invoice_pdf_path):
        print(f"{invoice_pdf_path} not found. Please give the right path for your pdf")

    print(f"\n Processing invoice: {invoice_pdf_path}")
    response = agent_executor.invoke(
        {"input": f"Please extract the total amount due from the invoice located at '{invoice_pdf_path}.'"})

    print("\n Agent's Final Answer")
    print(response['output'])

if __name__ == "__main__":
    run_invoice_processing_agent()
