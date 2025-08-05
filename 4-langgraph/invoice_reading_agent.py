from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.rate_limiters import InMemoryRateLimiter
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os
import json
from pypdf import PdfReader
from config import MODEL

load_dotenv()
google_api_key = os.getenv("GEMINI_API_KEY")
model = MODEL

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,
    check_every_n_seconds=0.1,
    max_bucket_size=1
)

class GraphState(TypedDict):
    invoice_path: str
    invoice_text: str
    structured_data: Annotated[dict, "Structured invoice data in JSON format"]

class Invoice(BaseModel):
    """Model to hold structured data extracted from the invoice"""
    vendor_name:  str = Field(..., description="The name of the company issuing the invoice")
    customer_name:  str = Field(..., description="The name of the customer on the invoice")
    invoice_number:  str = Field(..., description="The unique id or number of the invoice")
    total_amount: float = Field(..., description="The total amount due on the invoice")
    due_date: str = Field(..., description="The date when the invoice was made")

# let's create nodes #1
def read_invoice_file(state: GraphState) -> GraphState:
    """This function reads the raw text from the invoice file"""    
    print("--- 1. Reading Invoice File ---")
    reader = PdfReader(state["invoice_path"])
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    print("The text is successfully read")
    return {"invoice_text": text}

# let's continue with our node #2
def extract_structured_data(state: GraphState) -> GraphState:
    """This function extracts the data from the scanned pdf using google gemini"""
    print("--- 2. Extracting Structured Data ---")
    llm = ChatGoogleGenerativeAI(model=model,
                                 google_api_key=google_api_key,
                                 temperature=0,
                                 rate_limiter=rate_limiter)
    structured_llm = llm.with_structured_output(Invoice)

    prompt = f"""
    You are expert accountant.
    Analyze the following invoice text and extract the key details into the required JSON format.

    Invoice Text:
    ---
    {state["invoice_text"]}
    ---
    """
    print("The Agent is extracting your invoice...")
    response = structured_llm.invoke(prompt)

    print("The text is successfully extracted")
    return {"structured_data": response.dict()}

workflow = StateGraph(GraphState)
workflow.add_node("read_file", read_invoice_file)
workflow.add_node("extract_data", extract_structured_data)

workflow.set_entry_point("read_file")
workflow.add_edge("read_file", "extract_data")
workflow.add_edge("extract_data", END)

app = workflow.compile()

if __name__ == "__main__":
    print("Starting Invoice Processing Workflow")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    invoice_path = os.path.join(script_dir, "scanned_invoice.pdf")

    initial_state = {"invoice_path": invoice_path}
    final_state = app.invoke(initial_state)

    print("\n Extracted is completed")
    print("Final Structured Data")
    print(json.dumps(final_state["structured_data"], indent=2))