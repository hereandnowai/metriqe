from langchain_community.document_loaders import TextLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests
from dotenv import load_dotenv
import os

url = "https://raw.githubusercontent.com/hereandnowai/vac/refs/heads/master/prospectus-context.txt"
response = requests.get(url)
text_file = "profile-of-hereandnowai.txt"
with open(text_file, "wb") as f:
    f.write(response.content)

load_dotenv()
google_api_key = os.getenv("GEMINI_API_KEY")

def rag_text():
    loader = TextLoader("profile-of-hereandnowai.txt")
    documents = loader.load()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key)

    template = "Answer only based on the context: \n\n{context}\n\nQuestion {question}"
    prompt = ChatPromptTemplate.from_template(template)
    chain = ({
        "context": lambda x: "\n\n".join(doc.page_content for doc in x["input_documents"]),
        "question": lambda x: x["question"]
    }
    | prompt
    | llm
    | StrOutputParser()
    )

    question = "What are the products of the company?"
    response = chain.invoke({"input_documents": documents, "question": question})

    print(f"Question: {question}\n Answer: {response}")

if __name__ == "__main__":
    rag_text()