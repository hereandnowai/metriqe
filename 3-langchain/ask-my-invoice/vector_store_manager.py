import os
from config import PDF_DIRS, VECTOR_STORE_DIR, COLLECTION_NAME
from llm_utils import embeddings
import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from metadata_extractor import extract_metadata_from_document
from langchain.text_splitter import RecursiveCharacterTextSplitter
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

    document = []
    failed_files = []

    for pdf_path in new_pdf_paths:
        try:
            loader = PyPDFLoader(pdf_path)
            doc_pages = loader.load()
            metadata = extract_metadata_from_document(doc_pages[0].page_content)
            
            for page in doc_pages:
                page.metadata.update(metadata)
                page.metadata['source'] = pdf_path

            document.extend(doc_pages)
            
        except Exception as e:
            print("error",e)
            failed_files.extend(os.path.basename(pdf_path))

        texts = RecursiveCharacterTextSplitter(chunk_size= 1000,chunk_overlap = 200).split_documents(documents=document)

        if vector_store_instance is None:
            client = chromadb.PersistentClient(VECTOR_STORE_DIR)
            vector_store_instance = Chroma(client = client,
                                           collection_name= COLLECTION_NAME, 
                                           embedding_function=embeddings)
            if vector_store_instance._collection.count() == 0:
                vector_store_instance = Chroma.from_documents(client =client,
                                                              collection_name = COLLECTION_NAME,
                                                              embedding= embeddings,
                                                              documents= texts,
                                                              persist_directory= VECTOR_STORE_DIR
                                                              )
            else:
                vector_store_instance.add_documents(documents=texts)

        else:
            vector_store_instance.add_documents(documents=texts)
        

    total_docs_in_chromadb = vector_store_instance._collection.count()
    status = f"Added {len(new_pdf_paths) - len(failed_files)}  new files, we have {total_docs_in_chromadb} are there in chromadb " 
    status += f"{len(failed_files)} are failed ."
    status += f"failed to process {", ".join(failed_files)}."
    
    return status, gr.update(choices=get_pdf_list())

    





#Removing one pdf Vector Store 



#Clear all the Data


def clear_all_data():
    """Clears the vector store collection and all PDFs."""
    global vector_store_instance
    vector_store_instance = None
    
    try:
        client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
        client.delete_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(f"Could not clear collection (it might not exist): {e}")

    if os.path.exists(PDF_DIRS):
        shutil.rmtree(PDF_DIRS)
    os.makedirs(PDF_DIRS)
    
    return "Status: All documents and knowledge base have been cleared.", gr.update(choices=[], value=None)


