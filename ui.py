import gradio as gr
from rag_from_pdf import get_response

gr.ChatInterface(fn=get_response, title="RAG from PDF").launch()