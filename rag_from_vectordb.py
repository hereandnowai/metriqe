#Step Import libraries
from openai import OpenAI
import gradio as gr
from dotenv import load_dotenv
import PyPDF2
import os
import requests
import numpy as np
import faiss
import re
import pickle

#step 2 Loading the key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
client = OpenAI(api_key= api_key,base_url= base_url)

#step 3 file paths
pdf_path = os.path.join(os.path.dirname(__file__),"profile-of-hereandnowai.pdf")
vector_path = os.path.join(os.path.dirname(__file__),"vector_store.pkl")

#step 4 reading the pdf
def read_pdf(pdf_path):
    text =""
    with open(pdf_path,"rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            if page.extract_text(): text += page.extract_text()        
    return text

#step 5 sentence split into chunks 
def split_text_semanticaly(text,chunk_size = 1000):
    sentences = re.split(r'(?<=[.!?])\s+',text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

#step 5 get the embeddings

def get_embeddings(text):
    response = client.embeddings.create(
        input=text,
        model="embedding-001"  
    )
    embedding = response.data[0].embedding
    return np.array(embedding)

# step 6 loading and creating the vector
def load_or_create_vector_store():
    if os.path.exists(vector_path):
        with open(vector_path,"rb") as f: return pickle.load(f)

    text = read_pdf(pdf_path)
    chunks = split_text_semanticaly(text,1000)

    embeddings = np.array([get_embeddings(chunk) for chunk in chunks]).astype(np.float32)

    embeddings /= np.linalg.norm(embeddings,axis=0,keepdims=True)

    index = faiss.IndexFlatIP(embeddings.shape[1])

    index.add(embeddings)    

    with open(vector_path,"wb") as f : pickle.dump((chunks, index),f)

    return chunks, index
    

def search_similar_chunk(query, chunks, index , top_k=3):
    
    query_embedding = get_embeddings(query).astype("float32")
        
    Distance,Index = index.search(np.expand_dims(query_embedding,axis= 0),top_k)

    return [chunks[i] for i in Index[0]]
    

def get_response(query, history):
    context = "\n\n".join(search_similar_chunk(query,chunks,index,top_k=3 ))
    prompt = f"context: {context}\n\n question:  {query} \n\n Answer based on the context only. If the information is not found in the context. just say it is not there in the context no explanation"
    response = client.chat.completions.create( 
    model="gemini-2.5-flash", 
    messages= [{"role":"user", "content": prompt}])
    return response.choices[0].message.content
    

chunks, index = load_or_create_vector_store()

gr.ChatInterface(
    fn = get_response,
    title= "RAG with Vector",
    type="messages"
).launch()
