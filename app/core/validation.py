import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, validator
from fastapi import HTTPException

class InputValidator:
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format and length"""
        if not email or len(email) > 255:
            raise HTTPException(status_code=400, detail="Invalid email length")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        return email.lower().strip()
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength"""
        if not password or len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        if len(password) > 128:
            raise HTTPException(status_code=400, detail="Password too long")
        
        # Check for at least one uppercase, lowercase, digit
        if not re.search(r'[A-Z]', password):
            raise HTTPException(status_code=400, detail="Password must contain uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise HTTPException(status_code=400, detail="Password must contain lowercase letter")
        
        if not re.search(r'\d', password):
            raise HTTPException(status_code=400, detail="Password must contain digit")
        
        return password
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not text:
            return ""
        
        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Trim whitespace
        text = text.strip()
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def validate_listing_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate listing creation data"""
        validated = {}
        
        # Title validation
        title = data.get('title', '').strip()
        if not title or len(title) < 3:
            raise HTTPException(status_code=400, detail="Title must be at least 3 characters")
        if len(title) > 200:
            raise HTTPException(status_code=400, detail="Title too long")
        validated['title'] = InputValidator.sanitize_string(title, 200)
        
        # Description validation
        description = data.get('description', '').strip()
        if len(description) > 2000:
            raise HTTPException(status_code=400, detail="Description too long")
        validated['description'] = InputValidator.sanitize_string(description, 2000)
        
        # Price validation
        price = data.get('price')
        if price is not None:
            if not isinstance(price, (int, float)) or price < 0:
                raise HTTPException(status_code=400, detail="Invalid price")
            if price > 999999:
                raise HTTPException(status_code=400, detail="Price too high")
            validated['price'] = float(price)
        
        # Category validation
        category = data.get('category', '').strip()
        allowed_categories = ['electronics', 'books', 'furniture', 'clothing', 'sports', 'other']
        if category and category not in allowed_categories:
            raise HTTPException(status_code=400, detail="Invalid category")
        validated['category'] = category
        
        return validated

class SecureBaseModel(BaseModel):
    """Base model with security validations"""
    
    @validator('*', pre=True)
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            return InputValidator.sanitize_string(v)
        return v
