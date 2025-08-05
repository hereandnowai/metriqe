
from metadata_schema import InvocieMetaData
from llm_utils import llm

def extract_metadata_from_document(doc_content:str)->dict:
    """use metadata to extract data form the documents""" 
    try:
        parser_llm = llm.with_structured_output(InvocieMetaData)
        
        prompt = f"""
        Extract the following invoice details from the document content provided below
        Ensure the 'invoice_date' is in format 'DD-MM-YYYY', 'invoice_number and 'custumer_name'
        are in string and 'total_value' is in float

        Document content: {doc_content}
        
        Extracted invoice details:
        """
        extracted_data = parser_llm.invoke(prompt)
    except Exception as e:
       return None

    return extracted_data.dict()


