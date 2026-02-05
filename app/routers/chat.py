"""
Chatbot Router
"Ask Nexus" - Context-aware AI assistant
"""
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.config import settings

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask Nexus - Context-aware AI assistant for the NEXUS platform.
    
    Provides help and answers questions based on:
    - Current page the user is viewing
    - Conversation history
    - User's role and permissions (future)
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
        
        # Build context-aware system prompt
        current_page = request.context.current_page or "unknown"
        
        system_prompt = f"""You are Nexus AI, a helpful assistant for the NEXUS CRM & ERP platform.

Current Context:
- User is viewing: {current_page}
- Tenant: {request.tenant_id}

Your capabilities:
- Answer questions about the NEXUS platform features
- Provide guidance on how to use different modules (CRM, Inventory, Sales, Purchasing)
- Suggest actions users can take
- Explain business metrics and reports

Guidelines:
- Be concise and helpful
- If the user asks about data (sales, inventory levels, etc.), remind them that you can't access live data, but suggest where they can find it
- Suggest specific actions they can take (e.g., "Check the Low Stock Alerts page")
- Keep responses under 100 words when possible
- Be professional but friendly

If you don't know something, admit it and suggest how they might find the answer."""

        # Build messages array
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history if present
        if request.context.conversation_history:
            for msg in request.context.conversation_history[-5:]:  # Last 5 messages only
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": request.user_message
        })
        
        # Call GPT-4o-mini (cheaper for chat)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.7,  # Balanced creativity/consistency
        )
        
        # Extract response
        ai_response = response.choices[0].message.content
        
        # Generate context-based suggestions
        suggestions = generate_suggestions(current_page, request.user_message)
        
        return ChatResponse(
            response=ai_response,
            suggestions=suggestions
        )
        
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="OpenAI library not installed"
        )
    except Exception as e:
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
                detail=f"Chat error: {error_message}"
            )


def generate_suggestions(current_page: str, user_message: str) -> list[str]:
    """
    Generate contextual action suggestions based on current page and user query.
    """
    suggestions_map = {
        "/inventory": [
            "View low stock alerts",
            "Check product details",
            "Create purchase order"
        ],
        "/crm/leads": [
            "Create new lead",
            "View pipeline",
            "Export leads to CSV"
        ],
        "/crm/deals": [
            "View deal pipeline",
            "Move deal to next stage",
            "Generate sales report"
        ],
        "/sales": [
            "Create new order",
            "View recent orders",
            "Generate invoice"
        ],
        "/purchasing": [
            "Create purchase order",
            "Receive goods",
            "View vendor list"
        ],
        "default": [
            "View dashboard",
            "Check notifications",
            "Browse help docs"
        ]
    }
    
    # Find matching suggestions
    for page_path, suggestions in suggestions_map.items():
        if page_path in current_page:
            return suggestions
    
    return suggestions_map["default"]
