from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
import os 

from llm_utils import llm
from metadata_schema import DOCUMENT_DESCRIPTION, metadata_field_info
from vector_store_manager import get_vector_store_instance

def get_qa_chain():
    """Build and returns a SelfQueryRetriever"""
    vector_store_instance = get_vector_store_instance()
    if vector_store_instance == None:
        return None
    
    return SelfQueryRetriever.from_llm(
            llm=llm,
            vectorstore= vector_store_instance,
            document_contents=DOCUMENT_DESCRIPTION,
            metadata_field_info= metadata_field_info,
            verbose = True,
            search_kwargs={"k":5}
        )

def get_answer(question):
    if not question:
        return "Please Enter the Question to answer"
    
    retriever = get_qa_chain()
    if retriever == None:
        return " There is no knowledgebase to answer. please upload the pdfs"

    retrive_docs = retriever.invoke(question)

    if any(word in question.lower() for word in ["total", "sum", "count", "average"] ):
        total = 0
        invoicecount = 0
        seen_invoices = set()

        for doc in retrive_docs:
            invoice_id  = (doc.metadata.get("invoice_number"),doc.metadata.get("source"))
            if invoice_id not in seen_invoices:
                total += doc.metadata.get("total_value",0)
                invoicecount += 1
                seen_invoices.add(invoice_id)
        
        answer = f"found {invoicecount} invoices: The total value is {total}"
        #sources = "\n".join([ f"-{os.path.basename(doc.metadata.get("source","unknown"))}" for doc in retrive_docs]) 
        sources = "\n".join([ f"-{os.path.basename(doc.metadata.get('source', 'Unknown'))}" for doc in retrive_docs])
        return answer, sources
    else:
        prompt_template = """
        Use the given context from the uploaded documents give answer to the questions at the end;
        if you don't know the answer based on the given context just say so, don't make up any answer
        on your own. keep the answer precise and helpful
        context:
        {context}

        question:
        {question}

        Helpful answer:
        """

        QA_PROMPT = PromptTemplate.from_template(prompt_template)

        rag_chain = (
            {"context": retriever , "question": RunnablePassthrough()}
            |QA_PROMPT
            |llm
            |StrOutputParser()
        )

        answer = rag_chain.invoke(question)
        sources = "\n".join([ f"-{os.path.basename(doc.metadata.get("source","unknown"))}" for doc in retrive_docs])
        return answer, sources










