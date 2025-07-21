import os
from config import PDF_DIRS, VECTOR_STORE_DIR, COLLECTION_NAME
from llm_utils import embeddings
import chromadb
from langchain_chroma import Chroma
import shutil
import gradio as gr
vector_store_instance = None

#Loading the PDFs
def get_pdf_list():
    """Return a list of pdf available in the PDFs Directory"""
    return[f for f in os.listdir(PDF_DIRS) if f.endswith(".pdf")]


#Get vector store
def get_vector_store_instance():
    global vector_store_instance

    if vector_store_instance is None:
        try:
            client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
            vector_store_instance = Chroma(
                client=client,
                collection_name=COLLECTION_NAME, 
                embedding_function= embeddings)
        except Exception as e:
            print(f"Error in getting the vector store : {e}") 
            return None
        return vector_store_instance


#Adding Vector Store
def add_to_vector_store(files):
    """Adds new, non duplicate pdf to the vector store.
       Checks for existing filenames to prevent duplication 
    """
    global vector_store_instance
    new_pdf_paths = []
    skipped_files = []
    for file in files:
        dest_path = os.path.join(PDF_DIRS, os.path.basename(file.name))
        if os.path.exists(dest_path):
            skipped_files.append(os.path.basename(file.name))
            continue
        shutil.copy(file.name,dest_path)
        new_pdf_paths.append(dest_path)
    
    if not new_pdf_paths:
        status = "Status : all files are already available in the knowledge base"
        if skipped_files:
            status += f" skipped : {",".join(skipped_files)}"
        return status, gr.update(choices=get_pdf_list())

    status = f"uploaded files count: {len(new_pdf_paths)}"
    return status, gr.update(choices=get_pdf_list())

    





#Removing one pdf Vector Store 



#Clear all the Data
