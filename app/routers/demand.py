"""
Demand Forecasting Router
Uses Prophet for time-series forecasting
"""
from fastapi import APIRouter, HTTPException
from app.schemas.demand import PredictDemandRequest, PredictDemandResponse
import pandas as pd

router = APIRouter()

@router.post("/predict-demand", response_model=PredictDemandResponse)
async def predict_demand(request: PredictDemandRequest):
    """
    Predict product demand for the next month using time-series forecasting.
    
    Uses Facebook Prophet model for forecasting based on historical sales data.
    """
    try:
        # Validate input
        if len(request.historical_sales) < 3:
            raise HTTPException(
                status_code=400,
                detail="Need at least 3 months of historical data for forecasting"
            )
        
        if len(request.historical_sales) != len(request.dates):
            raise HTTPException(
                status_code=400,
                detail="Number of sales values must match number of dates"
            )
        
        # Import Prophet (lazy import to avoid loading if not needed)
        from prophet import Prophet
        
        # Create DataFrame for Prophet
        df = pd.DataFrame({
            'ds': pd.to_datetime(request.dates),
            'y': request.historical_sales
        })
        
        # Initialize and fit Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,  # Flexibility in trend
        )
        
        # Suppress Prophet's verbose output
        import logging
        logging.getLogger('prophet').setLevel(logging.WARNING)
        
        model.fit(df)
        
        # Create future dataframe for next 30 days
        future = model.make_future_dataframe(periods=30, freq='D')
        forecast = model.predict(future)
        
        # Get forecast for next month (sum of next 30 days)
        next_month_forecast = int(forecast['yhat'].tail(30).sum())
        
        # Ensure non-negative forecast
        next_month_forecast = max(0, next_month_forecast)
        
        # Calculate trend
        recent_avg = df['y'].tail(3).mean()
        trend = "increasing" if next_month_forecast > recent_avg else \
                "decreasing" if next_month_forecast < recent_avg * 0.9 else \
                "stable"
        
        # Calculate confidence (based on uncertainty interval width)
        # Narrower interval = higher confidence
        uncertainty = forecast['yhat_upper'].tail(30).mean() - forecast['yhat_lower'].tail(30).mean()
        confidence = max(0.5, min(0.95, 1 - (uncertainty / max(1, next_month_forecast))))
        
        return PredictDemandResponse(
            next_month_forecast=next_month_forecast,
            confidence=round(confidence, 2),
            trend=trend
        )
        
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Prophet library not installed. Please install with: pip install prophet"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Forecasting error: {str(e)}"
        )
