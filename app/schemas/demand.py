"""
Pydantic schemas for Demand Forecasting
"""
from pydantic import BaseModel, Field
from typing import List

class PredictDemandRequest(BaseModel):
    tenant_id: str = Field(..., description="Tenant ID")
    product_id: str = Field(..., description="Product ID")
    historical_sales: List[int] = Field(..., description="Last 12 months sales data")
    dates: List[str] = Field(..., description="Dates corresponding to sales (YYYY-MM-DD)")

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "product_id": "prod-uuid-123",
                "historical_sales": [150, 160, 155, 170, 165, 180, 175, 190, 185, 200, 195, 210],
                "dates": ["2025-01-01", "2025-02-01", "2025-03-01", "2025-04-01", 
                         "2025-05-01", "2025-06-01", "2025-07-01", "2025-08-01",
                         "2025-09-01", "2025-10-01", "2025-11-01", "2025-12-01"]
            }
        }

class PredictDemandResponse(BaseModel):
    next_month_forecast: int = Field(..., description="Forecasted sales for next month")
    confidence: float = Field(..., description="Confidence score (0-1)")
    trend: str = Field(..., description="Trend direction: increasing, stable, or decreasing")

    class Config:
        json_schema_extra = {
            "example": {
                "next_month_forecast": 220,
                "confidence": 0.85,
                "trend": "increasing"
            }
        }
