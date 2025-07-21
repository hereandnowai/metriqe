
from metadata_schema import InvocieMetaData
from llm_utils import llm

def extract_metadata_from_document(doc_content:str, llm_model)->dict:
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
        print(f"error:{e}")

    return extracted_data.dict()


print(extract_metadata_from_document("""
Invoice No: INV001         Date: 2025-07-20
 TAX INVOICE
 Supplier: HereandnowAI
 Address: Chennai, Tamil Nadu
 GSTIN: 33HNAI0000X1Z5
 Bill To: TechNova Solutions
 Address: Bangalore, Karnataka
 GSTIN: 29ABCDE1234F1Z5
 Description
 Desktop Computer
 Laptop
 Wireless Mouse
 Keyboard
 Monitor 24 inch
 Total CGST: Rs.12375.00
 Total SGST: Rs.12375.00
 Grand Total: Rs.162250.0
"""  , llm))