"""
Invoice OCR Router
Uses GPT-4o Vision for invoice parsing
"""
from fastapi import APIRouter, HTTPException
from app.schemas.invoice import ParseInvoiceRequest, ParseInvoiceResponse
from app.config import settings
import json

router = APIRouter()

@router.post("/parse-invoice", response_model=ParseInvoiceResponse)
async def parse_invoice(request: ParseInvoiceRequest):
    """
    Extract structured data from invoice images using GPT-4o Vision.
    
    Supports JPEG, PNG, and PDF formats.
    """
    try:
        # Check if OpenAI API key is configured
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
            )
        
        # Import OpenAI (lazy import)
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Create prompt for GPT-4o Vision
        prompt = """Extract the following information from this invoice image:
        
1. Vendor name (company that issued the invoice)
2. Invoice date (format: YYYY-MM-DD)
3. Total amount
4. Line items (description, quantity, unit price, total for each item)

Return ONLY valid JSON matching this exact schema:
{
  "vendor_name": "string",
  "invoice_date": "YYYY-MM-DD",
  "total_amount": number,
  "line_items": [
    {
      "description": "string",
      "quantity": number,
      "unit_price": number,
      "total": number
    }
  ]
}

Important:
- Extract all line items you can see
- Use numbers without currency symbols
- Date must be YYYY-MM-DD format
- Return ONLY the JSON, no markdown or explanation
"""
        
        # Call GPT-4o Vision
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": request.image_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=1500,
            temperature=0.1,  # Low temperature for consistent extraction
        )
        
        # Extract response content
        content = response.choices[0].message.content
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        # Parse JSON
        try:
            parsed_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse GPT-4o response as JSON: {str(e)}"
            )
        
        # Validate and return
        return ParseInvoiceResponse(**parsed_data)
        
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="OpenAI library not installed. Please install with: pip install openai"
        )
    except Exception as e:
        # Check for specific OpenAI errors
        error_message = str(e)
        if "api_key" in error_message.lower():
            raise HTTPException(
                status_code=401,
                detail="Invalid OpenAI API key"
            )
        elif "quota" in error_message.lower():
            raise HTTPException(
                status_code=429,
                detail="OpenAI API quota exceeded"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Invoice parsing error: {error_message}"
            )
