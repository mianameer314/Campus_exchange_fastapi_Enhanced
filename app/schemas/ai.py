from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PriceSuggestRequest(BaseModel):
    title: str
    description: str
    category: str
    condition: str

class PriceSuggestResponse(BaseModel):
    suggested_price: Optional[float]
    confidence: int
    reasoning: str
    price_range: Optional[Dict[str, float]] = None

class DuplicateCheckRequest(BaseModel):
    title: str
    description: str
    category: str

class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    confidence: int
    similar_listings: List[int]
    reasoning: str

class RecommendRequest(BaseModel):
    user_preferences: Dict[str, Any]

class RecommendResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    reasoning: str
