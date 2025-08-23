# Complete Testing Sequence Guide

## Overview
This guide provides a systematic approach to testing your Campus Exchange API, ensuring all components work correctly in the proper sequence.

## Prerequisites
- API server running on `http://localhost:8000`
- PostgreSQL database connected and migrated
- Environment variables properly configured
- Postman installed (optional but recommended)

## Testing Phases

### Phase 1: Infrastructure & Health Checks

#### 1.1 Basic Connectivity
\`\`\`bash
# Test basic server response
curl -X GET http://localhost:8000/

# Expected Response:
# {"message": "Welcome to the campus_exchange API"}
\`\`\`

#### 1.2 Health Endpoints
\`\`\`bash
# Basic health check
curl -X GET http://localhost:8000/healthz

# Expected Response:
# {"status": "ok"}

# Detailed health check
curl -X GET http://localhost:8000/health/detailed

# Expected Response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "environment": "development",
#   "database": "connected",
#   "timestamp": 1642234567.123
# }
\`\`\`

#### 1.3 API Documentation Access
\`\`\`bash
# Check Swagger UI availability
curl -X GET http://localhost:8000/docs

# Should return HTML content for Swagger UI
\`\`\`

**✅ Phase 1 Success Criteria:**
- All endpoints return 200 status
- Database connection confirmed
- Swagger UI accessible

---

### Phase 2: Authentication Flow

#### 2.1 User Registration
\`\`\`bash
# Sign up new user
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@cuiatk.edu.pk",
    "password": "testpassword123"
  }'

# Expected Response:
# {"message": "Registration successful. Please login to get your token."}
\`\`\`

#### 2.2 User Login
\`\`\`bash
# Login and capture token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@cuiatk.edu.pk",
    "password": "testpassword123"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"

# Expected Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }
\`\`\`

#### 2.3 Authentication Verification
\`\`\`bash
# Get current user info
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Expected Response:
# {
#   "id": 1,
#   "email": "test@cuiatk.edu.pk",
#   "is_admin": false,
#   "is_verified": true,
#   "university_name": "COMSATS Attock University"
# }
\`\`\`

#### 2.4 Invalid Authentication Tests
\`\`\`bash
# Test with invalid token
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer invalid_token"

# Expected Response: 401 Unauthorized

# Test with no token
curl -X GET http://localhost:8000/api/v1/auth/me

# Expected Response: 403 Forbidden
\`\`\`

**✅ Phase 2 Success Criteria:**
- User registration successful
- Login returns valid JWT token
- Token authentication works
- Invalid token properly rejected

---

### Phase 3: Listings Management

#### 3.1 Create Listing
\`\`\`bash
# Create a new listing
LISTING_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/listings \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Test Laptop for Sale" \
  -F "description=High-performance laptop in excellent condition" \
  -F "category=Electronics" \
  -F "price=750.00")

echo "$LISTING_RESPONSE"

# Extract listing ID
LISTING_ID=$(echo "$LISTING_RESPONSE" | jq -r '.id')
echo "Created Listing ID: $LISTING_ID"

# Expected Response:
# {
#   "id": 1,
#   "title": "Test Laptop for Sale",
#   "description": "High-performance laptop in excellent condition",
#   "category": "Electronics",
#   "price": 750.0,
#   "images": [],
#   "status": "ACTIVE",
#   "owner_id": 1,
#   "created_at": "2024-01-15T10:30:00Z"
# }
\`\`\`

#### 3.2 Retrieve Listing
\`\`\`bash
# Get specific listing
curl -X GET http://localhost:8000/api/v1/listings/$LISTING_ID

# Expected Response: Same as creation response
\`\`\`

#### 3.3 Update Listing
\`\`\`bash
# Update listing details
curl -X PATCH http://localhost:8000/api/v1/listings/$LISTING_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Laptop for Sale - Price Reduced!",
    "price": 650.00
  }'

# Expected Response: Updated listing object
\`\`\`

#### 3.4 Update Listing Status
\`\`\`bash
# Change listing status
curl -X PATCH http://localhost:8000/api/v1/listings/$LISTING_ID/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "SOLD"}'

# Expected Response: Listing with updated status
\`\`\`

#### 3.5 Authorization Tests
\`\`\`bash
# Try to update without authentication
curl -X PATCH http://localhost:8000/api/v1/listings/$LISTING_ID \
  -H "Content-Type: application/json" \
  -d '{"title": "Unauthorized Update"}'

# Expected Response: 403 Forbidden

# Create another user and try to update first user's listing
# (This requires creating a second user account)
\`\`\`

**✅ Phase 3 Success Criteria:**
- Listing creation successful
- Listing retrieval works
- Updates require authentication
- Status changes work correctly
- Authorization properly enforced

---

### Phase 4: Search & Discovery

#### 4.1 Basic Search
\`\`\`bash
# Search for listings
curl -X GET "http://localhost:8000/api/v1/listings/search?q=laptop&page=1&page_size=5"

# Expected Response:
# {
#   "total": 1,
#   "page": 1,
#   "page_size": 5,
#   "total_pages": 1,
#   "has_next": false,
#   "has_prev": false,
#   "results": [...]
# }
\`\`\`

#### 4.2 Filtered Search
\`\`\`bash
# Search with multiple filters
curl -X GET "http://localhost:8000/api/v1/listings/search?q=laptop&category=Electronics&min_price=500&max_price=1000&status=ACTIVE"

# Test different filter combinations
curl -X GET "http://localhost:8000/api/v1/listings/search?category=Electronics&sort_by=price&sort_order=asc"
\`\`\`

#### 4.3 Advanced Search
\`\`\`bash
# Advanced search with multiple parameters
curl -X GET "http://localhost:8000/api/v1/listings/advanced-search?keywords=laptop,computer&categories=Electronics&exclude_sold=true"
\`\`\`

#### 4.4 Search Suggestions
\`\`\`bash
# Get search suggestions
curl -X GET "http://localhost:8000/api/v1/listings/suggestions?q=lap&limit=5"

# Expected Response:
# {
#   "suggestions": ["laptop", "laptop bag", "laptop stand"]
# }
\`\`\`

#### 4.5 Trending Searches
\`\`\`bash
# Get trending categories
curl -X GET "http://localhost:8000/api/v1/listings/trending?days=7&limit=10"
\`\`\`

**✅ Phase 4 Success Criteria:**
- Basic search returns results
- Filters work correctly
- Pagination functions properly
- Search suggestions generated
- Trending data available

---

### Phase 5: AI Services

#### 5.1 AI Health Check
\`\`\`bash
# Check AI service status
curl -X GET http://localhost:8000/api/v1/ai/health

# Expected Response:
# {
#   "price_suggest_enabled": true,
#   "duplicate_check_enabled": true,
#   "recommend_enabled": true,
#   "ai_service_configured": true,
#   "model": "gpt-4o-mini"
# }
\`\`\`

#### 5.2 Price Suggestion
\`\`\`bash
# Get AI price suggestion
curl -X POST http://localhost:8000/api/v1/ai/price-suggest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "MacBook Pro 2021",
    "description": "13-inch MacBook Pro with M1 chip, 8GB RAM, 256GB SSD",
    "category": "Electronics",
    "condition": "Used - Good"
  }'

# Expected Response:
# {
#   "suggested_price": 1150.0,
#   "confidence": 0.85,
#   "price_range": {"min": 1000.0, "max": 1300.0},
#   "reasoning": "Based on current market prices..."
# }
\`\`\`

#### 5.3 Duplicate Detection
\`\`\`bash
# Check for duplicate listings
curl -X POST http://localhost:8000/api/v1/ai/duplicate-check \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Laptop for Sale",
    "description": "Selling my laptop",
    "category": "Electronics"
  }'
\`\`\`

#### 5.4 Recommendations
\`\`\`bash
# Get personalized recommendations
curl -X POST http://localhost:8000/api/v1/ai/recommend \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_preferences": {
      "categories": ["Electronics", "Books"],
      "price_range": [100, 1000],
      "keywords": ["laptop", "programming"]
    }
  }'
\`\`\`

**✅ Phase 5 Success Criteria:**
- AI services respond correctly
- Price suggestions are reasonable
- Duplicate detection works
- Recommendations are relevant

---

### Phase 6: User Interactions

#### 6.1 Favorites Management
\`\`\`bash
# Add listing to favorites
curl -X POST http://localhost:8000/api/v1/favorites/$LISTING_ID \
  -H "Authorization: Bearer $TOKEN"

# Get user's favorites
curl -X GET http://localhost:8000/api/v1/favorites \
  -H "Authorization: Bearer $TOKEN"

# Remove from favorites
curl -X DELETE http://localhost:8000/api/v1/favorites/$LISTING_ID \
  -H "Authorization: Bearer $TOKEN"
\`\`\`

#### 6.2 Notifications
\`\`\`bash
# Get user notifications
curl -X GET http://localhost:8000/api/v1/notifications \
  -H "Authorization: Bearer $TOKEN"

# Mark notification as read (if notifications exist)
curl -X PATCH http://localhost:8000/api/v1/notifications/1/read \
  -H "Authorization: Bearer $TOKEN"

# Mark all notifications as read
curl -X PATCH http://localhost:8000/api/v1/notifications/mark-all-read \
  -H "Authorization: Bearer $TOKEN"
\`\`\`

**✅ Phase 6 Success Criteria:**
- Favorites can be added/removed
- Notifications are retrievable
- Read status updates work

---

### Phase 7: Admin Operations

#### 7.1 Admin Authentication
\`\`\`bash
# Login as admin (using admin credentials from environment)
ADMIN_TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@cuiatk.edu.pk",
    "password": "admin123"
  }' | jq -r '.access_token')

echo "Admin Token: $ADMIN_TOKEN"
\`\`\`

#### 7.2 Admin User Management
\`\`\`bash
# Get all users (admin only)
curl -X GET "http://localhost:8000/api/v1/admin/users?page=1&page_size=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Get user statistics
curl -X GET http://localhost:8000/api/v1/admin/stats/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"
\`\`\`

#### 7.3 Admin Listing Management
\`\`\`bash
# Get all listings (admin only)
curl -X GET "http://localhost:8000/api/v1/admin/listings?page=1&page_size=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Get listing statistics
curl -X GET http://localhost:8000/api/v1/admin/stats/listings \
  -H "Authorization: Bearer $ADMIN_TOKEN"
\`\`\`

#### 7.4 Admin Authorization Tests
\`\`\`bash
# Try admin endpoint with regular user token
curl -X GET http://localhost:8000/api/v1/admin/users \
  -H "Authorization: Bearer $TOKEN"

# Expected Response: 403 Forbidden
\`\`\`

**✅ Phase 7 Success Criteria:**
- Admin login successful
- Admin endpoints accessible with admin token
- Regular users cannot access admin endpoints
- Statistics and management functions work

---

### Phase 8: Error Handling & Edge Cases

#### 8.1 Invalid Data Tests
\`\`\`bash
# Test with invalid email domain
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@invalid-domain.com",
    "password": "testpass123"
  }'

# Expected Response: 400 Bad Request

# Test with invalid price
curl -X POST http://localhost:8000/api/v1/listings \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Test Item" \
  -F "description=Test description" \
  -F "category=Electronics" \
  -F "price=-100.00"

# Expected Response: 422 Validation Error
\`\`\`

#### 8.2 Non-existent Resource Tests
\`\`\`bash
# Try to get non-existent listing
curl -X GET http://localhost:8000/api/v1/listings/99999

# Expected Response: 404 Not Found

# Try to update non-existent listing
curl -X PATCH http://localhost:8000/api/v1/listings/99999 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# Expected Response: 404 Not Found
\`\`\`

#### 8.3 Rate Limiting Tests
\`\`\`bash
# Test rate limiting (if enabled)
for i in {1..110}; do
  curl -X GET http://localhost:8000/healthz &
done
wait

# Some requests should return 429 Too Many Requests
\`\`\`

**✅ Phase 8 Success Criteria:**
- Invalid data properly rejected
- Non-existent resources return 404
- Rate limiting works (if enabled)
- Error messages are informative

---

## Automated Testing Script

### Complete Test Suite
\`\`\`bash
#!/bin/bash
# complete_api_test.sh

set -e  # Exit on any error

BASE_URL="http://localhost:8000"
TEST_EMAIL="test@cuiatk.edu.pk"
TEST_PASSWORD="testpassword123"

echo "🚀 Starting Campus Exchange API Test Suite"
echo "=========================================="

# Phase 1: Health Checks
echo "📋 Phase 1: Health Checks"
curl -f "$BASE_URL/" > /dev/null && echo "✅ Root endpoint OK" || echo "❌ Root endpoint FAILED"
curl -f "$BASE_URL/healthz" > /dev/null && echo "✅ Health check OK" || echo "❌ Health check FAILED"
curl -f "$BASE_URL/health/detailed" > /dev/null && echo "✅ Detailed health OK" || echo "❌ Detailed health FAILED"

# Phase 2: Authentication
echo -e "\n🔐 Phase 2: Authentication"
# Signup
SIGNUP_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

if echo "$SIGNUP_RESPONSE" | grep -q "Registration successful"; then
  echo "✅ Signup OK"
else
  echo "✅ User already exists (OK)"
fi

# Login
TOKEN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" \
  | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
  echo "✅ Login OK - Token received"
else
  echo "❌ Login FAILED - No token received"
  exit 1
fi

# Verify token
USER_INFO=$(curl -s -X GET "$BASE_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN")

if echo "$USER_INFO" | grep -q "email"; then
  echo "✅ Token verification OK"
else
  echo "❌ Token verification FAILED"
  exit 1
fi

# Phase 3: Listings
echo -e "\n📝 Phase 3: Listings Management"
# Create listing
LISTING_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/listings" \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Test Laptop" \
  -F "description=Test description" \
  -F "category=Electronics" \
  -F "price=500.00")

LISTING_ID=$(echo "$LISTING_RESPONSE" | jq -r '.id')

if [ "$LISTING_ID" != "null" ] && [ -n "$LISTING_ID" ]; then
  echo "✅ Listing creation OK - ID: $LISTING_ID"
else
  echo "❌ Listing creation FAILED"
  exit 1
fi

# Get listing
curl -s -f "$BASE_URL/api/v1/listings/$LISTING_ID" > /dev/null && echo "✅ Listing retrieval OK" || echo "❌ Listing retrieval FAILED"

# Phase 4: Search
echo -e "\n🔍 Phase 4: Search & Discovery"
SEARCH_RESPONSE=$(curl -s "$BASE_URL/api/v1/listings/search?q=laptop")
if echo "$SEARCH_RESPONSE" | grep -q "results"; then
  echo "✅ Search OK"
else
  echo "❌ Search FAILED"
fi

# Phase 5: AI Services
echo -e "\n🤖 Phase 5: AI Services"
AI_HEALTH=$(curl -s "$BASE_URL/api/v1/ai/health")
if echo "$AI_HEALTH" | grep -q "price_suggest_enabled"; then
  echo "✅ AI Health check OK"
else
  echo "❌ AI Health check FAILED"
fi

# Test price suggestion
PRICE_SUGGEST=$(curl -s -X POST "$BASE_URL/api/v1/ai/price-suggest" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Laptop","description":"Good laptop","category":"Electronics","condition":"Used"}')

if echo "$PRICE_SUGGEST" | grep -q "suggested_price"; then
  echo "✅ Price suggestion OK"
else
  echo "⚠️  Price suggestion may not be working (check AI_API_KEY)"
fi

echo -e "\n🎉 Test Suite Completed!"
echo "Check individual test results above for any failures."
\`\`\`

### Running the Test Suite
\`\`\`bash
# Make script executable
chmod +x complete_api_test.sh

# Run the test suite
./complete_api_test.sh
\`\`\`

This comprehensive testing guide ensures your Campus Exchange API is thoroughly validated across all functionality areas. Follow the phases sequentially to identify and resolve any issues systematically.
