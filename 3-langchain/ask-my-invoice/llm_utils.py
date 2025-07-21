from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from config import API_KEY

try:
    embeddings = GoogleGenerativeAIEmbeddings(model ="models/embedding-001", google_api_key= API_KEY)
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash-lite-preview-06-17",google_api_key = API_KEY, temperature = 0)
except Exception as e:
    raise RuntimeError(f"Failed to initialize the google models. Check you API key and network connection. Error: {e}")
