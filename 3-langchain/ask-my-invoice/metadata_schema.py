from pydantic import BaseModel, Field
from langchain.chains.query_constructor.base import AttributeInfo
from typing import ClassVar, List

class InvocieMetaData(BaseModel):
    invoice_date: str = Field(description="The date invoice was issued, in format DD-MM-YYYY")
    invoice_number: str = Field(description= "The unique identifier of the invoice")
    total_value: float = Field(description= "The total amount of the invoice")
    customer_name: str = Field(description= "The name of the company that we have invoiced")

metadata_field_info = [
    AttributeInfo(
        name = "invoice_date",
        description = "The date invoice was issued, in format DD-MM-YYYY",
        type = "string",
    ),
    AttributeInfo(
        name = "invoice_number",
        description = "The unique identifier of the invoice",
        type = "string",
    ),
    AttributeInfo(
        name = "total_value",
        description = "The total amount of the invoice",
        type = "float",
    ),
    AttributeInfo(
        name = "customer_name",
        description = "The name of the company that we have invoiced",
        type = "string",
    ),
]

DOCUMENT_DESCRIPTION = "Scanned Invoices and Billing statements"