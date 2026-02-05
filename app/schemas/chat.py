"""
Pydantic schemas for Chatbot
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatContext(BaseModel):
    current_page: Optional[str] = Field(None, description="Current page user is on (e.g., '/inventory/products')")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Previous messages in conversation")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context metadata")

class ChatRequest(BaseModel):
    tenant_id: str = Field(..., description="Tenant ID")
    user_message: str = Field(..., description="User's message")
    context: Optional[ChatContext] = Field(default_factory=ChatContext, description="Conversation context")

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_message": "What are my low stock products?",
                "context": {
                    "current_page": "/inventory/products",
                    "conversation_history": []
                }
            }
        }

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI assistant's response")
    suggestions: Optional[List[str]] = Field(None, description="Suggested follow-up actions")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "I can help you check low stock products. You can view them by clicking the 'Low Stock Alerts' button on your inventory page.",
                "suggestions": [
                    "View low stock alerts",
                    "Check recent sales",
                    "Generate purchase order"
                ]
            }
        }
