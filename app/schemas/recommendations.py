"""
Pydantic schemas for Recommendations
"""
from pydantic import BaseModel, Field
from typing import List

class RecommendUpsellRequest(BaseModel):
    tenant_id: str = Field(..., description="Tenant ID")
    current_cart_items: List[str] = Field(..., description="Product IDs currently in cart")

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "current_cart_items": ["prod-123", "prod-456"]
            }
        }

class UpsellRecommendation(BaseModel):
    product_id: str = Field(..., description="Recommended product ID")
    confidence: float = Field(..., description="Confidence score (0-1)")
    reason: str = Field(..., description="Why this product is recommended")

class RecommendUpsellResponse(BaseModel):
    recommendations: List[UpsellRecommendation] = Field(..., description="List of recommended products")

    class Config:
        json_schema_extra = {
            "example": {
                "recommendations": [
                    {
                        "product_id": "prod-789",
                        "confidence": 0.82,
                        "reason": "Frequently bought together"
                    },
                    {
                        "product_id": "prod-101",
                        "confidence": 0.75,
                        "reason": "Similar customers also bought"
                    }
                ]
            }
        }
