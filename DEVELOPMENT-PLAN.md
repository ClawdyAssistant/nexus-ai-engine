# NEXUS AI Engine - Development Plan

**Repository:** nexus-ai-engine  
**Developer:** Clawdy (Solo AI Developer)  
**Stack:** Python 3.11+ + FastAPI + OpenAI API + Scikit-learn  
**Sprint Duration:** 2 weeks  
**Total Timeline:** 2 weeks (1 sprint)

---

## Overview

AI microservice for NEXUS platform providing:
- Demand forecasting (time-series prediction)
- Invoice OCR (GPT-4o Vision)
- Upsell recommendations (collaborative filtering)
- Chatbot support

---

## Architecture

**Service Type:** Stateless Python microservice  
**Framework:** FastAPI  
**Models:** OpenAI GPT-4o, Prophet/ARIMA  
**Deployment:** Docker container

**Integration:**
- Backend (NestJS) acts as proxy
- Backend handles authentication & tenant isolation
- AI service receives validated requests

---

## SPRINT AI-1: AI Service (2 weeks)

### 🎫 TICKET-AI-001: FastAPI Project Setup
**Priority:** 🔴 Critical  
**Time:** 4 hours

**Requirements:**
1. Initialize FastAPI project
2. Install dependencies
3. Configure environment variables
4. Create project structure

**Dependencies:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
openai==1.10.0
prophet==1.1.5
scikit-learn==1.4.0
pandas==2.2.0
pillow==10.2.0
python-dotenv==1.0.0
```

**Project Structure:**
```
nexus-ai-engine/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routers/
│   │   ├── demand.py
│   │   ├── ocr.py
│   │   ├── recommendations.py
│   │   └── chat.py
│   ├── models/
│   │   ├── demand_forecaster.py
│   │   └── recommender.py
│   └── schemas/
│       ├── demand.py
│       ├── invoice.py
│       └── recommendations.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

**Acceptance Criteria:**
- [ ] FastAPI runs on port 8000
- [ ] `/docs` endpoint shows Swagger UI
- [ ] Health check endpoint works
- [ ] Environment variables loaded

---

### 🎫 TICKET-AI-002: Demand Forecasting Endpoint
**Priority:** 🟡 High  
**Time:** 12 hours

**Endpoint:** `POST /predict-demand`

**Input:**
```json
{
  "tenant_id": "uuid",
  "product_id": "uuid",
  "historical_sales": [150, 160, 155, 170, ...],  // Last 12 months
  "dates": ["2025-01-01", "2025-02-01", ...]
}
```

**Output:**
```json
{
  "next_month_forecast": 180,
  "confidence": 0.85,
  "trend": "increasing"
}
```

**Implementation (Prophet Model):**
```python
from fastapi import APIRouter
from prophet import Prophet
import pandas as pd

router = APIRouter()

@router.post("/predict-demand")
async def predict_demand(data: PredictDemandRequest):
    # Convert to DataFrame
    df = pd.DataFrame({
        'ds': data.dates,
        'y': data.historical_sales
    })
    
    # Fit Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )
    model.fit(df)
    
    # Forecast next 30 days
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    
    # Get next month total
    next_month = forecast['yhat'].tail(30).sum()
    
    return {
        "next_month_forecast": int(next_month),
        "confidence": 0.85,
        "trend": "increasing" if next_month > df['y'].mean() else "stable"
    }
```

**Alternative (ARIMA):**
If Prophet is too slow, use ARIMA from statsmodels.

**Acceptance Criteria:**
- [ ] Endpoint accepts historical sales data
- [ ] Returns forecast for next month
- [ ] Response time <5 seconds
- [ ] Handles edge cases (not enough data)

---

### 🎫 TICKET-AI-003: Invoice OCR Endpoint
**Priority:** 🟡 High  
**Time:** 10 hours

**Endpoint:** `POST /parse-invoice`

**Input:**
```json
{
  "image_url": "https://s3.amazonaws.com/..."
}
```

**Output:**
```json
{
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
```

**Implementation (GPT-4o Vision):**
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/parse-invoice")
async def parse_invoice(data: ParseInvoiceRequest):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Extract the following from this invoice image:
                        1. Vendor name
                        2. Invoice date (YYYY-MM-DD format)
                        3. Total amount
                        4. Line items (description, quantity, unit price, total)
                        
                        Return ONLY valid JSON matching this schema:
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
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": data.image_url}
                    }
                ]
            }
        ],
        max_tokens=1000
    )
    
    # Parse JSON from response
    content = response.choices[0].message.content
    parsed = json.loads(content)
    
    return parsed
```

**Acceptance Criteria:**
- [ ] Accepts image URL (JPEG, PNG, PDF)
- [ ] Extracts vendor, date, items
- [ ] Returns valid JSON
- [ ] Response time <10 seconds
- [ ] Error handling for bad images

---

### 🎫 TICKET-AI-004: Upsell Recommendations Endpoint
**Priority:** 🟢 Medium  
**Time:** 8 hours

**Endpoint:** `POST /recommend-upsell`

**Input:**
```json
{
  "tenant_id": "uuid",
  "current_cart_items": ["product-uuid-1", "product-uuid-2"]
}
```

**Output:**
```json
{
  "recommendations": [
    {
      "product_id": "product-uuid-3",
      "confidence": 0.82,
      "reason": "Frequently bought together"
    },
    {
      "product_id": "product-uuid-4",
      "confidence": 0.75,
      "reason": "Similar customers also bought"
    }
  ]
}
```

**Implementation (Collaborative Filtering):**

**Option 1: Simple Association Rules**
```python
# Pre-trained model loaded from historical sales
@router.post("/recommend-upsell")
async def recommend_upsell(data: RecommendRequest):
    # Simple frequency-based approach
    # In production: Use Apriori algorithm or ALS (Alternating Least Squares)
    
    recommendations = []
    for item in data.current_cart_items:
        # Lookup frequently co-purchased items
        related = frequently_bought_together.get(item, [])
        recommendations.extend(related)
    
    # Sort by confidence and return top 5
    recommendations = sorted(recommendations, key=lambda x: x['confidence'], reverse=True)[:5]
    
    return {"recommendations": recommendations}
```

**Option 2: ML Model (if enough data)**
Use scikit-learn's Apriori or collaborative filtering.

**Acceptance Criteria:**
- [ ] Returns product recommendations
- [ ] Confidence scores provided
- [ ] Response time <2 seconds
- [ ] Handles empty cart

---

### 🎫 TICKET-AI-005: Chatbot Endpoint (Ask Nexus)
**Priority:** 🟢 Medium  
**Time:** 6 hours

**Endpoint:** `POST /chat`

**Input:**
```json
{
  "tenant_id": "uuid",
  "user_message": "What are my top selling products this month?",
  "context": {
    "current_page": "/inventory/products",
    "conversation_history": [...]
  }
}
```

**Output:**
```json
{
  "response": "Based on your sales data, your top 3 products this month are...",
  "suggestions": [
    "View detailed analytics",
    "Check stock levels"
  ]
}
```

**Implementation:**
```python
@router.post("/chat")
async def chat(data: ChatRequest):
    # Build context-aware prompt
    system_prompt = f"""You are Nexus AI, an assistant for a CRM & ERP platform.
    
    Current context:
    - User is on page: {data.context.current_page}
    - Tenant: {data.tenant_id}
    
    Provide helpful, concise answers about their business data.
    If you need data from the backend, say "I'll need to check the database" and suggest using specific features.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Cheaper model for chat
        messages=[
            {"role": "system", "content": system_prompt},
            *data.context.conversation_history,
            {"role": "user", "content": data.user_message}
        ],
        max_tokens=300
    )
    
    return {
        "response": response.choices[0].message.content,
        "suggestions": ["View inventory", "Check sales reports"]
    }
```

**Acceptance Criteria:**
- [ ] Context-aware responses
- [ ] Conversation history supported
- [ ] Response time <3 seconds
- [ ] Helpful suggestions provided

---

### 🎫 TICKET-AI-006: Docker Containerization
**Priority:** 🟡 High  
**Time:** 4 hours

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app ./app

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml (for local testing):**
```yaml
version: '3.8'

services:
  ai-engine:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./app:/app/app
```

**Acceptance Criteria:**
- [ ] Docker image builds successfully
- [ ] Container runs FastAPI
- [ ] Environment variables injected
- [ ] Health check endpoint works

---

### 🎫 TICKET-AI-007: Testing & Documentation
**Priority:** 🟢 Medium  
**Time:** 6 hours

**Tests:**
- Unit tests for each endpoint
- Mock OpenAI API calls
- Test edge cases

**Documentation:**
- API documentation (Swagger auto-generated)
- README with setup instructions
- Example requests/responses

**Acceptance Criteria:**
- [ ] >70% test coverage
- [ ] All endpoints documented
- [ ] README complete

---

## Environment Variables

```env
# .env.example
OPENAI_API_KEY=sk-...
ENVIRONMENT=development
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,https://nexus.app
```

---

## API Documentation

FastAPI auto-generates docs at `/docs` (Swagger UI).

---

## Performance Targets

- Demand forecasting: <5s response time
- Invoice OCR: <10s response time
- Recommendations: <2s response time
- Chatbot: <3s response time

---

## Deployment

**Development:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Production:**
```bash
docker build -t nexus-ai-engine .
docker run -p 8000:8000 --env-file .env nexus-ai-engine
```

---

**Developer:** Clawdy  
**Last Updated:** February 5, 2026  
**Status:** Ready for development
