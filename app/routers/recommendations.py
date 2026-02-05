"""
Recommendations Router
Provides upsell/cross-sell recommendations based on collaborative filtering
"""
from fastapi import APIRouter, HTTPException
from app.schemas.recommendations import (
    RecommendUpsellRequest,
    RecommendUpsellResponse,
    UpsellRecommendation
)
from typing import Dict, List
import random

router = APIRouter()

# Mock frequently bought together data
# In production, this would come from a trained ML model or database
FREQUENTLY_BOUGHT_TOGETHER: Dict[str, List[Dict]] = {
    # Example: If product X is in cart, recommend these
    "default": [
        {"product_id": "recommended-1", "confidence": 0.75, "reason": "Popular combination"},
        {"product_id": "recommended-2", "confidence": 0.70, "reason": "Frequently bought together"},
        {"product_id": "recommended-3", "confidence": 0.65, "reason": "Similar customers bought"},
    ]
}

@router.post("/recommend-upsell", response_model=RecommendUpsellResponse)
async def recommend_upsell(request: RecommendUpsellRequest):
    """
    Generate product recommendations based on current cart items.
    
    Uses collaborative filtering to suggest products that are frequently
    purchased together with items currently in the cart.
    
    Note: This is a simplified implementation. In production, you would:
    1. Train a collaborative filtering model (ALS, matrix factorization)
    2. Use association rule mining (Apriori algorithm)
    3. Store pre-computed recommendations in cache/database
    """
    try:
        if not request.current_cart_items:
            # Empty cart - return popular products
            return RecommendUpsellResponse(
                recommendations=[
                    UpsellRecommendation(
                        product_id=f"popular-{i}",
                        confidence=0.8 - (i * 0.1),
                        reason="Trending product"
                    )
                    for i in range(min(3, 5))
                ]
            )
        
        # Simple algorithm: Look up frequently bought together items
        # In production: Query trained ML model or pre-computed associations
        
        recommendations = []
        seen_products = set(request.current_cart_items)
        
        # For each item in cart, find associated products
        for item_id in request.current_cart_items:
            # Get associated products (simplified - using default for now)
            associated = FREQUENTLY_BOUGHT_TOGETHER.get(
                item_id,
                FREQUENTLY_BOUGHT_TOGETHER["default"]
            )
            
            for assoc in associated:
                product_id = assoc["product_id"]
                
                # Don't recommend items already in cart
                if product_id not in seen_products:
                    recommendations.append(
                        UpsellRecommendation(
                            product_id=product_id,
                            confidence=round(assoc["confidence"] + random.uniform(-0.05, 0.05), 2),
                            reason=assoc["reason"]
                        )
                    )
                    seen_products.add(product_id)
        
        # Sort by confidence and return top 5
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        recommendations = recommendations[:5]
        
        # If no recommendations found, return empty list
        if not recommendations:
            recommendations = [
                UpsellRecommendation(
                    product_id="complementary-product",
                    confidence=0.60,
                    reason="Complementary product"
                )
            ]
        
        return RecommendUpsellResponse(recommendations=recommendations)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation error: {str(e)}"
        )


# TODO: In production, add these endpoints:
# - POST /train-model - Train collaborative filtering model on historical sales
# - POST /update-associations - Update frequently bought together associations
# - GET /model-metrics - Return model accuracy metrics
