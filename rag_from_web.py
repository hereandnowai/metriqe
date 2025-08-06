# step 1 - importing libs
from openai import OpenAI
import gradio as gr
import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# step 2 - loading secrets
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
# base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
base_url = "http://localhost:11434/v1/"
client = OpenAI(api_key="ollama", base_url=base_url)

# step 3 - getting info from web: https://hereandnowai.github.io/vac/
url = "https://hereandnowai.github.io/vac/"

response = requests.get(url,
                        headers={"User-Agent": "Mozilla/5.0"},
                        timeout=10)

soup = BeautifulSoup(response.content, "html.parser")
website_context = soup.body.get_text(separator="\n",
                                     strip=True) if soup.body else "no info found"

# step 4 - fn
def get_response(HumanMessage, history):
    messages = f"Context from {url}:\n{website_context}\n\n Question: {HumanMessage}\n Answer only based on context"
    response = client.chat.completions.create(model="llama3.2:latest",
                                              messages=[{"role":"user", "content":messages}])
    return response.choices[0].message.content

print(get_response("Who is the cto of here and now ai?", []))

if __name__ == "__main__":
    gr.ChatInterface(fn=get_response, title="RAG from web from HERE AND NOW AI").launch()