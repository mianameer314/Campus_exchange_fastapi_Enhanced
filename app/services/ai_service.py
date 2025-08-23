import asyncio
import json
import logging
from typing import Dict, List, Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class AIService:
    def __init__(self):
        self.base_url = settings.AI_SERVICE_URL
        self.timeout = settings.AI_TIMEOUT_SECONDS
        self.max_retries = settings.AI_MAX_RETRIES
        self.retry_delay = settings.AI_RETRY_DELAY

    async def _make_ml_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to ML service"""
        headers = {"Content-Type": "application/json"}

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    return response.json()

            except httpx.TimeoutException:
                logger.warning(f"ML service timeout on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    raise AIServiceError("ML service timeout after all retries")

            except httpx.HTTPStatusError as e:
                logger.error(f"ML service HTTP error: {e.response.status_code}")
                if e.response.status_code == 429:  # Rate limit
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                        continue
                raise AIServiceError(f"ML service error: {e.response.status_code}")

            except Exception as e:
                logger.error(f"Unexpected ML service error: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise AIServiceError(f"ML service error: {str(e)}")

            await asyncio.sleep(self.retry_delay)

    async def suggest_price(
        self,
        title: str,
        description: str,
        category: str,
        condition: str,
        market_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Suggest price using ML model with DB context"""
        if not settings.AI_PRICE_SUGGEST_ENABLED:
            return {"suggested_price": None, "confidence": 0, "reasoning": "AI price suggestion disabled"}

        payload = {
            "title": title,
            "description": description,
            "category": category,
            "condition": condition,
            "market_stats": market_stats  # <-- new, DB-powered
        }

        try:
            result = await self._make_ml_request("/predict-price", payload)
            return {
                "suggested_price": result.get("predicted_price"),
                "confidence": result.get("confidence", 0),
                "reasoning": result.get("explanation", "ML model prediction"),
                "price_range": result.get("price_range")
            }
        except Exception as e:
            logger.error(f"Price suggestion error: {e}")
            return {"suggested_price": None, "confidence": 0, "reasoning": f"Service error: {str(e)}"}

    async def check_duplicate(self, title: str, description: str, existing_listings: List[Dict]) -> Dict[str, Any]:
        """Check duplicates using ML model with DB context"""
        if not settings.AI_DUPLICATE_CHECK_ENABLED:
            return {"is_duplicate": False, "confidence": 0, "similar_listings": []}

        payload = {
            "title": title,
            "description": description,
            "existing_listings": existing_listings[:10]  # Pass sample from DB
        }

        try:
            result = await self._make_ml_request("/check-duplicate", payload)
            return {
                "is_duplicate": result.get("is_duplicate", False),
                "confidence": result.get("confidence", 0),
                "similar_listings": result.get("similar_listing_ids", []),
                "reasoning": result.get("explanation", "ML duplicate detection")
            }
        except Exception as e:
            logger.error(f"Duplicate check error: {e}")
            return {"is_duplicate": False, "confidence": 0, "similar_listings": []}

    async def recommend_listings(self, user_preferences: Dict, available_listings: List[Dict]) -> Dict[str, Any]:
        """Get recommendations using ML model with DB context"""
        if not settings.AI_RECOMMEND_ENABLED:
            return {"recommendations": [], "reasoning": "AI recommendations disabled"}

        payload = {
            "user_id": user_preferences.get("user_id"),
            "user_preferences": user_preferences,
            "available_listings": available_listings[:20]  # Pass real DB listings
        }

        try:
            result = await self._make_ml_request("/recommend", payload)
            return {
                "recommendations": result.get("recommendations", []),
                "reasoning": result.get("explanation", "ML-based recommendations")
            }
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            return {"recommendations": [], "reasoning": f"Service error: {str(e)}"}


# Singleton instance
ai_service = AIService()
