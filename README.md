# NEXUS AI Engine

AI microservice for NEXUS CRM & ERP platform.

## Features

- **Demand Forecasting** - Time-series prediction using Prophet/ARIMA
- **Invoice OCR** - Extract data from invoices using GPT-4o Vision
- **Upsell Recommendations** - Collaborative filtering for product suggestions
- **AI Chatbot** - Context-aware assistant for users

## Tech Stack

- Python 3.11+
- FastAPI
- OpenAI API (GPT-4o)
- Prophet (time-series forecasting)
- Scikit-learn

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once running, visit: http://localhost:8000/docs

## Development

See [DEVELOPMENT-PLAN.md](DEVELOPMENT-PLAN.md) for detailed sprint plan.

---

**Developer:** Clawdy  
**Repository:** https://github.com/ClawdyAssistant/nexus-ai-engine
