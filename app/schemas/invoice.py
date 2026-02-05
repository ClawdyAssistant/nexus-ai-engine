"""
Pydantic schemas for Invoice OCR
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List

class ParseInvoiceRequest(BaseModel):
    image_url: str = Field(..., description="URL of the invoice image (JPEG, PNG, or PDF)")

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://s3.amazonaws.com/bucket/invoice.jpg"
            }
        }

class InvoiceLineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float

class ParseInvoiceResponse(BaseModel):
    vendor_name: str = Field(..., description="Vendor/supplier name")
    invoice_date: str = Field(..., description="Invoice date (YYYY-MM-DD)")
    total_amount: float = Field(..., description="Total invoice amount")
    line_items: List[InvoiceLineItem] = Field(..., description="List of line items")

    class Config:
        json_schema_extra = {
            "example": {
                "vendor_name": "Acme Supplies Inc.",
                "invoice_date": "2026-01-15",
                "total_amount": 1250.00,
                "line_items": [
                    {
                        "description": "Widget A",
                        "quantity": 10,
                        "unit_price": 50.00,
                        "total": 500.00
                    },
                    {
                        "description": "Widget B",
                        "quantity": 25,
                        "unit_price": 30.00,
                        "total": 750.00
                    }
                ]
            }
        }
