from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SearchFilters(BaseModel):
    q: Optional[str] = Field(None, description="Search keyword")
    category: Optional[str] = Field(None, description="Filter by category")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    university: Optional[str] = Field(None, description="Filter by university")
    status: Optional[str] = Field("ACTIVE", description="Filter by status")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

class AdvancedSearchFilters(BaseModel):
    keywords: Optional[List[str]] = Field(None, description="Multiple search keywords")
    categories: Optional[List[str]] = Field(None, description="Multiple categories")
    price_ranges: Optional[List[str]] = Field(None, description="Price ranges")
    universities: Optional[List[str]] = Field(None, description="Multiple universities")
    date_from: Optional[str] = Field(None, description="Filter from date")
    date_to: Optional[str] = Field(None, description="Filter to date")
    exclude_sold: bool = Field(True, description="Exclude sold items")

class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    results: List[dict]

class SearchSuggestion(BaseModel):
    suggestions: List[str]

class TrendingCategory(BaseModel):
    category: str
    count: int

class TrendingResponse(BaseModel):
    trending_categories: List[TrendingCategory]
