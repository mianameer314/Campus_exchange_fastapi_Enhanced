from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, text, and_, or_
from typing import Optional, List
from datetime import datetime, timedelta

from app.api.deps import get_db
from app.models.listing import Listing
from app.models.user import User

router = APIRouter(tags=["Search"])

@router.get("/listings/search")
def search_listings(
    q: Optional[str] = Query(None, description="Search keyword"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    university: Optional[str] = Query(None, description="Filter by university"),
    status: Optional[str] = Query("ACTIVE", description="Filter by status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    query = db.query(Listing).options(joinedload(Listing.owner))
    
    if status:
        query = query.filter(Listing.status == status)
    else:
        query = query.filter(Listing.status == "ACTIVE")

    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Listing.title.ilike(search_term),
                Listing.description.ilike(search_term),
                Listing.category.ilike(search_term)
            )
        )

    # Enhanced filters
    if category:
        query = query.filter(Listing.category.ilike(f"%{category}%"))
    if university:
        query = query.join(User).filter(User.university_name.ilike(f"%{university}%"))
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)

    valid_sort_fields = ['created_at', 'updated_at', 'price', 'title']
    if sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Valid options: {valid_sort_fields}")

    sort_column = getattr(Listing, sort_by)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination with performance optimization
    total = query.count()
    listings = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "has_next": page * page_size < total,
        "has_prev": page > 1,
        "results": [listing.to_dict() for listing in listings]
    }

@router.get("/listings/advanced-search")
def advanced_search_listings(
    keywords: Optional[List[str]] = Query(None, description="Multiple search keywords"),
    categories: Optional[List[str]] = Query(None, description="Multiple categories"),
    price_ranges: Optional[List[str]] = Query(None, description="Price ranges (e.g., '0-50', '50-100')"),
    universities: Optional[List[str]] = Query(None, description="Multiple universities"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    exclude_sold: bool = Query(True, description="Exclude sold items"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Listing).options(joinedload(Listing.owner))
    
    # Status filter
    if exclude_sold:
        query = query.filter(Listing.status.in_(["ACTIVE"]))
    
    # Multiple keyword search
    if keywords:
        keyword_conditions = []
        for keyword in keywords:
            search_term = f"%{keyword}%"
            keyword_conditions.append(
                or_(
                    Listing.title.ilike(search_term),
                    Listing.description.ilike(search_term),
                    Listing.category.ilike(search_term)
                )
            )
        query = query.filter(or_(*keyword_conditions))
    
    # Multiple category filter
    if categories:
        query = query.filter(Listing.category.in_(categories))
    
    # Multiple university filter
    if universities:
        query = query.join(User).filter(User.university_name.in_(universities))
    
    # Price range filters
    if price_ranges:
        price_conditions = []
        for price_range in price_ranges:
            try:
                min_p, max_p = map(float, price_range.split('-'))
                price_conditions.append(and_(Listing.price >= min_p, Listing.price <= max_p))
            except ValueError:
                continue
        if price_conditions:
            query = query.filter(or_(*price_conditions))
    
    # Date range filters
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Listing.created_at >= from_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format. Use YYYY-MM-DD")
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Listing.created_at < to_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format. Use YYYY-MM-DD")
    
    # Default sorting by relevance/date
    query = query.order_by(Listing.created_at.desc())
    
    total = query.count()
    listings = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "results": [listing.to_dict() for listing in listings]
    }

@router.get("/listings/suggestions")
def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Search query for suggestions"),
    limit: int = Query(10, ge=1, le=20, description="Number of suggestions"),
    db: Session = Depends(get_db)
):
    # Get title suggestions
    title_suggestions = db.query(Listing.title).filter(
        and_(
            Listing.title.ilike(f"%{q}%"),
            Listing.status == "ACTIVE"
        )
    ).distinct().limit(limit//2).all()
    
    # Get category suggestions
    category_suggestions = db.query(Listing.category).filter(
        and_(
            Listing.category.ilike(f"%{q}%"),
            Listing.status == "ACTIVE"
        )
    ).distinct().limit(limit//2).all()
    
    suggestions = []
    suggestions.extend([title[0] for title in title_suggestions])
    suggestions.extend([cat[0] for cat in category_suggestions])
    
    return {
        "suggestions": list(set(suggestions))[:limit]
    }

@router.get("/listings/trending")
def get_trending_searches(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    # Get most popular categories in the last N days
    cutoff_date = datetime.now() - timedelta(days=days)
    
    popular_categories = db.query(
        Listing.category,
        func.count(Listing.id).label('count')
    ).filter(
        and_(
            Listing.created_at >= cutoff_date,
            Listing.status == "ACTIVE"
        )
    ).group_by(Listing.category).order_by(text('count DESC')).limit(limit).all()
    
    return {
        "trending_categories": [
            {"category": cat[0], "count": cat[1]} 
            for cat in popular_categories
        ]
    }
