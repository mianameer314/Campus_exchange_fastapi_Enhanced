# Campus Exchange API

A production-grade FastAPI backend for a university-only marketplace enabling verified students to buy and sell items, chat, and manage listings with admin oversight.

## Features

- Student authentication with email OTP verification and ID upload
- Admin verification workflow and user management
- Create, update, search, and report listings
- Favorites and notifications
- Real-time style chat endpoints for buyer-seller communication
- AI endpoints for content assistance or moderation (config-dependent)
- Role-based access and permission dependencies
- PostgreSQL with SQLAlchemy ORM and Alembic migrations
- First-class DX: auto docs with Swagger, Docker, Postman collection

## Tech Stack

- **Language** Python 3.11
- **Framework** FastAPI
- **Database** PostgreSQL
- **ORM** SQLAlchemy
- **Migrations** Alembic
- **Auth** JWT-based
- **Container** Docker, docker-compose
- **Deployment** Procfile support
- **Docs** Swagger UI, Postman collection

## Repository Structure (top level)

```
.env
.vscode
Dockerfile
Procfile
README.md
alembic
alembic.ini
app
docker-compose.yml
postman_collection.json
requirements.txt
scripts
test_guide
uploads
```
## Getting Started

### 1. Prerequisites

- Python 3.11
- Docker and docker-compose (optional but recommended)
- PostgreSQL 14+ (if running locally without Docker)
- Make sure you can create and migrate a database

### 2. Clone and configure

```bash
cp .env .env.local  # or create a fresh .env from the variables below
```
### 3. Environment Variables

Define the following keys in your `.env`:

```
DATABASE_URL=<set me>
JWT_SECRET=<set me>
JWT_ALGORITHM=<set me>
JWT_EXPIRE_MINUTES=<set me>
CORS_ORIGINS=<set me>
ENV=<set me>
ADMIN_EMAIL=<set me>
ADMIN_PASSWORD=<set me>
STORAGE_BACKEND=<set me>
MAIL_USERNAME=<set me>
MAIL_PASSWORD=<set me>
MAIL_FROM=<set me>
MAIL_SERVER=<set me>
MAIL_PORT=<set me>
MAIL_FROM_NAME=<set me>
MAIL_STARTTLS=<set me>
MAIL_SSL_TLS=<set me>
ALLOWED_EMAIL_DOMAINS=<set me>
UPLOAD_DIR=<set me>
S3_BUCKET=<set me>
S3_REGION=<set me>
S3_ACCESS_KEY=<set me>
S3_SECRET_KEY=<set me>
S3_PUBLIC_BASE_URL=<set me>
AI_SERVICE_URL=<set me>
AI_API_KEY=<set me>
AI_PRICE_SUGGEST_ENABLED=<set me>
AI_DUPLICATE_CHECK_ENABLED=<set me>
AI_RECOMMEND_ENABLED=<set me>
MAX_FILE_SIZE=<set me>
```
### 4. Install dependencies

```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
### 5. Database setup

Initialize and run migrations:

```bash
alembic upgrade head
```
### 6. Run the app (local)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open docs at http://localhost:8000/docs

### 7. Run with Docker

```bash
docker-compose up --build
```
## API Documentation

Interactive docs at `/docs` and Redoc at `/redoc`. A Postman collection is included: `postman_collection.json`.

Below is a section-by-section breakdown of the API routers detected in `app/api/v1`.

### `admin.py`
- **DELETE /listings/{listing_id}**  
  function `delete_listing`  
  status default  
  response_model —  
  summary —
- **PATCH /listings/{listing_id}/moderate**  
  function `moderate_listing`  
  status default  
  response_model —  
  summary —
- **PATCH /reports/{report_id}/resolve**  
  function `resolve_report`  
  status default  
  response_model —  
  summary —
- **GET /stats**  
  function `get_admin_stats`  
  status default  
  response_model AdminStatsOut  
  summary —
- **GET /system/health**  
  function `get_system_health`  
  status default  
  response_model SystemHealthOut  
  summary —
- **POST /system/maintenance**  
  function `toggle_maintenance_mode`  
  status default  
  response_model —  
  summary —
- **DELETE /users/{user_id}**  
  function `delete_user`  
  status default  
  response_model —  
  summary —
- **PATCH /users/{user_id}**  
  function `update_user`  
  status default  
  response_model —  
  summary —
- **PATCH /verifications/{verification_id}/review**  
  function `review_verification`  
  status default  
  response_model —  
  summary —

### `ai.py`
- **POST /duplicate-check**  
  function `check_duplicate`  
  status default  
  response_model DuplicateCheckResponse  
  summary —
- **GET /health**  
  function `ai_health_check`  
  status default  
  response_model —  
  summary —
- **POST /price-suggest**  
  function `suggest_price`  
  status default  
  response_model PriceSuggestResponse  
  summary —
- **POST /recommend**  
  function `recommend_listings`  
  status default  
  response_model RecommendResponse  
  summary —

### `auth.py`
- **POST /login**  
  function `login`  
  status default  
  response_model Token  
  summary —
- **GET /me**  
  function `me`  
  status default  
  response_model —  
  summary —
- **POST /signup**  
  function `signup`  
  status default  
  response_model SignupResponse  
  summary —

### `chat.py`
- **DELETE /block/{user_id}**  
  function `unblock_user`  
  status default  
  response_model —  
  summary —
- **POST /block/{user_id}**  
  function `block_user`  
  status default  
  response_model —  
  summary —
- **GET /blocked**  
  function `get_blocked_users`  
  status default  
  response_model —  
  summary —
- **POST /messages/{message_id}/reactions**  
  function `add_reaction`  
  status default  
  response_model —  
  summary —
- **GET /rooms**  
  function `get_user_chat_rooms`  
  status default  
  response_model List[ChatRoomOut]  
  summary —
- **GET /rooms/{room_id}/messages**  
  function `get_chat_messages`  
  status default  
  response_model —  
  summary —
- **POST /rooms/{room_id}/messages/file**  
  function `upload_file_message`  
  status default  
  response_model —  
  summary —

### `favorites.py`
- **GET /**  
  function `list_favorites`  
  status default  
  response_model List[FavoriteResponse]  
  summary —
- **DELETE /{listing_id}**  
  function `remove_favorite`  
  status default  
  response_model —  
  summary —
- **POST /{listing_id}**  
  function `add_favorite`  
  status default  
  response_model —  
  summary —

### `listings.py`
- **POST **  
  function `create_listing`  
  status default  
  response_model ListingOut  
  summary —
- **DELETE /{listing_id}**  
  function `delete_listing`  
  status 204  
  response_model —  
  summary —
- **GET /{listing_id}**  
  function `get_listing`  
  status default  
  response_model ListingOut  
  summary —
- **PATCH /{listing_id}**  
  function `update_listing`  
  status default  
  response_model ListingOut  
  summary —
- **PATCH /{listing_id}/status**  
  function `patch_status`  
  status default  
  response_model ListingOut  
  summary —

### `notifications.py`
- **GET **  
  function `list_notifications`  
  status default  
  response_model List[NotificationResponse]  
  summary —
- **POST /mark-all-read**  
  function `mark_all_read`  
  status default  
  response_model —  
  summary —
- **GET /unread-count**  
  function `get_unread_count`  
  status default  
  response_model —  
  summary —
- **PATCH /{notification_id}**  
  function `update_notification`  
  status default  
  response_model NotificationResponse  
  summary —

### `reports.py`
- **POST /**  
  function `create_report`  
  status default  
  response_model ReportOut  
  summary —

### `search.py`
- **GET /listings/advanced-search**  
  function `advanced_search_listings`  
  status default  
  response_model —  
  summary —
- **GET /listings/search**  
  function `search_listings`  
  status default  
  response_model —  
  summary —
- **GET /listings/suggestions**  
  function `get_search_suggestions`  
  status default  
  response_model —  
  summary —
- **GET /listings/trending**  
  function `get_trending_searches`  
  status default  
  response_model —  
  summary —

### `verification.py`
- **POST /approve/{user_id}**  
  function `approve`  
  status default  
  response_model —  
  summary —
- **GET /pending**  
  function `pending`  
  status default  
  response_model —  
  summary —
- **POST /reject/{user_id}**  
  function `reject`  
  status default  
  response_model —  
  summary —
- **POST /request**  
  function `request_verification`  
  status default  
  response_model —  
  summary —
- **GET /status**  
  function `status`  
  status default  
  response_model —  
  summary —
- **POST /upload-id**  
  function `upload_id`  
  status default  
  response_model —  
  summary —
- **POST /verify-otp**  
  function `verify_otp`  
  status default  
  response_model —  
  summary —

## Data Models (Schemas)

Parsed from `app/schemas`.

### `admin.py`
- **AdminUserOut**
  - id: str
  - email: str
  - is_admin: bool
  - is_verified: bool
  - is_active: bool
  - university: Optional[str]
  - created_at: Optional[datetime]
- **AdminListingOut**
  - id: int
  - title: str
  - description: str
  - category: str
  - price: float
  - status: str
  - owner_id: str
  - created_at: datetime
  - updated_at: datetime
  - owner: Optional[AdminUserOut]
- **AdminReportOut**
  - id: int
  - report_type: str
  - reason: str
  - status: str
  - created_at: datetime
  - resolved_at: Optional[datetime]
  - reporter_id: str
  - reported_user_id: Optional[str]
  - listing_id: Optional[int]
  - admin_notes: Optional[str]
- **AdminVerificationOut**
  - id: int
  - user_id: str
  - status: str
  - created_at: datetime
  - reviewed_at: Optional[datetime]
  - admin_notes: Optional[str]
- **PaginatedUsersResponse**
  - users: List[AdminUserOut]
  - total: int
  - page: int
  - page_size: int
  - total_pages: int
- **PaginatedListingsResponse**
  - listings: List[AdminListingOut]
  - total: int
  - page: int
  - page_size: int
  - total_pages: int
- **PaginatedReportsResponse**
  - reports: List[AdminReportOut]
  - total: int
  - page: int
  - page_size: int
  - total_pages: int
- **PaginatedVerificationsResponse**
  - verifications: List[AdminVerificationOut]
  - total: int
  - page: int
  - page_size: int
  - total_pages: int
- **AdminStatsOut**
  - total_users: int
  - verified_users: int
  - new_users: int
  - total_listings: int
  - active_listings: int
  - sold_listings: int
  - new_listings: int
  - total_messages: int
  - active_chats: int
  - recent_messages: int
  - pending_reports: int
  - pending_verifications: int
  - blocked_users_count: int
  - category_stats: List[Dict[str, Any]]
  - period_days: int
- **UserUpdateRequest**
  - is_verified: Optional[bool]
  - is_active: Optional[bool]
  - is_admin: Optional[bool]
  - university: Optional[str]
- **ListingModerationRequest**
  - status: str
  - admin_notes: Optional[str]
- **SystemHealthOut**
  - database_status: str
  - total_users: int
  - total_listings: int
  - total_messages: int
  - recent_activity: Dict[str, int]
  - timestamp: datetime

### `ai.py`
- **PriceSuggestRequest**
  - title: str
  - description: str
  - category: str
  - condition: str
- **PriceSuggestResponse**
  - suggested_price: Optional[float]
  - confidence: int
  - reasoning: str
  - price_range: Optional[Dict[str, float]]
- **DuplicateCheckRequest**
  - title: str
  - description: str
  - category: str
- **DuplicateCheckResponse**
  - is_duplicate: bool
  - confidence: int
  - similar_listings: List[int]
  - reasoning: str
- **RecommendRequest**
  - user_preferences: Dict[str, Any]
- **RecommendResponse**
  - recommendations: List[Dict[str, Any]]
  - reasoning: str

### `auth.py`
- **UserCreate**
  - email: EmailStr
  - password: str
- **Token**
  - access_token: str
  - token_type: str
- **UserOut**
  - id: str
  - email: EmailStr
  - is_admin: bool
  - is_verified: bool
- **SignUpIn**
  - email: EmailStr
  - password: str

### `chat.py`
- **ChatMessageBase**
  - content: str
- **ChatRoomOut**
  - id: int
  - listing_id: int
  - participant1_id: str
  - participant2_id: str
  - created_at: datetime
  - last_message_at: Optional[datetime]
- **MessageReactionOut**
  - id: int
  - message_id: int
  - user_id: str
  - reaction: str
  - created_at: datetime
- **ChatMessageEdit**
  - message_id: int
  - new_content: str
- **ChatMessageDelete**
  - message_id: int

### `common.py`
- **Message**
  - message: str

### `favorite.py`
- **FavoriteBase**
  - listing_id: int

### `listing.py`
- **ListingCreate**
  - title: str
  - description: str
  - category: str
  - price: Decimal
  - images: Optional[List[str]]
- **ListingUpdate**
  - title: Optional[str]
  - description: Optional[str]
  - category: Optional[str]
  - price: Optional[Decimal]
  - images: Optional[List[str]]
- **ListingStatusPatch**
  - status: str
- **ListingOut**
  - id: int
  - title: str
  - description: str
  - category: str
  - price: Decimal
  - images: Optional[List[str]]
  - status: str
  - owner_id: str

### `notification.py`
- **NotificationBase**
  - title: str
  - message: str
  - type: str
  - related_id: Optional[int]
- **NotificationUpdate**
  - is_read: bool

### `report.py`
- **ReportCreate**
  - reported_listing_id: Optional[int]
  - reported_user_id: Optional[str]
  - reason: str
- **ReportOut**
  - id: int
  - reporter_id: str
  - reported_listing_id: Optional[int]
  - reported_user_id: Optional[str]
  - reason: str
  - status: str
  - created_at: datetime
  - reviewed_by: Optional[str]
  - reviewed_at: Optional[datetime]
  - audit_log: Optional[str]

### `search.py`
- **SearchFilters**
  - q: Optional[str]
  - category: Optional[str]
  - min_price: Optional[float]
  - max_price: Optional[float]
  - university: Optional[str]
  - status: Optional[str]
  - sort_by: str
  - sort_order: str
- **AdvancedSearchFilters**
  - keywords: Optional[List[str]]
  - categories: Optional[List[str]]
  - price_ranges: Optional[List[str]]
  - universities: Optional[List[str]]
  - date_from: Optional[str]
  - date_to: Optional[str]
  - exclude_sold: bool
- **SearchResponse**
  - total: int
  - page: int
  - page_size: int
  - total_pages: int
  - has_next: bool
  - has_prev: bool
  - results: List[dict]
- **SearchSuggestion**
  - suggestions: List[str]
- **TrendingCategory**
  - category: str
  - count: int
- **TrendingResponse**
  - trending_categories: List[TrendingCategory]

### `verification.py`
- **VerificationRequest**
  - university_email: EmailStr
  - student_id: str
- **OTPVerify**
  - otp_code: str
- **AdminReviewAction**
  - admin_notes: str

## Migrations

Use Alembic. Common commands:

```bash
alembic revision -m "describe change"
alembic upgrade head
alembic downgrade -1
```
## Testing

- Use the Postman collection to validate endpoints
- Add pytest as needed, structure under `tests/`

## Deployment

- Dockerfile and docker-compose are provided
- Procfile included for PaaS that use it (e.g., Render/Heroku-like processes)
- Set env vars in your deployment environment
- Run migrations before first boot: `alembic upgrade head`

## Security Notes

- Keep `SECRET_KEY` out of VCS
- Rotate tokens and credentials periodically
- Validate file uploads and sanitize user inputs
- Enforce admin-only actions via dependency checks

## Contributing

1. Create a feature branch
2. Add or update tests
3. Open a PR with a clear description

## License

Add your license of choice (MIT recommended).


---

## Detailed Endpoints

### `admin.py`
**Router prefix**: `/admin`
- **GET /admin/stats**
  - Function: `get_admin_stats`
  - Response model: `AdminStatsOut`
  - Response fields (from `AdminStatsOut`):
    - total_users: int
    - verified_users: int
    - new_users: int
    - total_listings: int
    - active_listings: int
    - sold_listings: int
    - new_listings: int
    - total_messages: int
    - active_chats: int
    - recent_messages: int
    - pending_reports: int
    - pending_verifications: int
    - blocked_users_count: int
    - category_stats: List[Dict[str, Any]]
    - period_days: int
  - Parameters: `days: int = Query(30, ge=1, le=365, description="Number of days for stats"),     db: Session = Depends(get_db),     admin: User = Depends(get_current_admin)`
- **PATCH /admin/users/{user_id}**
  - Function: `update_user`
  - Parameters: `user_id: str,  # Changed user_id from int to str     update_data: UserUpdateRequest,     db: Session = Depends(get_db),     admin: User = Depends(get_current_admin)`
- **DELETE /admin/users/{user_id}**
  - Function: `delete_user`
  - Parameters: `user_id: str,  # Changed user_id from int to str     db: Session = Depends(get_db),     admin: User = Depends(get_current_admin)`
- **PATCH /admin/listings/{listing_id}/moderate**
  - Function: `moderate_listing`
  - Parameters: `listing_id: int,     moderation_data: ListingModerationRequest,     db: Session = Depends(get_db),     admin: User = Depends(get_current_admin)`
- **DELETE /admin/listings/{listing_id}**
  - Function: `delete_listing`
  - Parameters: `listing_id: int,     reason: Optional[str] = Query(None, description="Reason for deletion"),     db: Session = Depends(get_db),     admin: User = Depends(get_current_admin)`
- **PATCH /admin/reports/{report_id}/resolve**
  - Function: `resolve_report`
  - Parameters: `report_id: int,     resolution: str = Query(..., description="Resolution action taken"),     notes: Optional[str] = Query(None, description="Admin notes"),     db: Session = Depends(get_db),     admin: User = Depends(get...`
- **PATCH /admin/verifications/{verification_id}/review**
  - Function: `review_verification`
  - Parameters: `verification_id: int,     approved: bool = Query(..., description="Whether to approve or reject"),     notes: Optional[str] = Query(None, description="Admin notes"),     db: Session = Depends(get_db),     admin: User = D...`
- **GET /admin/system/health**
  - Function: `get_system_health`
  - Response model: `SystemHealthOut`
  - Response fields (from `SystemHealthOut`):
    - database_status: str
    - total_users: int
    - total_listings: int
    - total_messages: int
    - recent_activity: Dict[str, int]
    - timestamp: datetime
  - Parameters: `db: Session = Depends(get_db),     admin: User = Depends(get_current_admin)`
- **POST /admin/system/maintenance**
  - Function: `toggle_maintenance_mode`
  - Parameters: `enabled: bool = Query(..., description="Enable or disable maintenance mode"),     message: Optional[str] = Query(None, description="Maintenance message"),     db: Session = Depends(get_db),     admin: User = Depends(get_...`

### `ai.py`
**Router prefix**: `/ai`
- **POST /ai/price-suggest**
  - Function: `suggest_price`
  - Response model: `PriceSuggestResponse`
  - Response fields (from `PriceSuggestResponse`):
    - suggested_price: Optional[float]
    - confidence: int
    - reasoning: str
    - price_range: Optional[Dict[str, float]]
  - Parameters: `request: PriceSuggestRequest,     db: Session = Depends(get_db),     user=Depends(get_current_user)`
- **POST /ai/duplicate-check**
  - Function: `check_duplicate`
  - Response model: `DuplicateCheckResponse`
  - Response fields (from `DuplicateCheckResponse`):
    - is_duplicate: bool
    - confidence: int
    - similar_listings: List[int]
    - reasoning: str
  - Parameters: `request: DuplicateCheckRequest,     db: Session = Depends(get_db),     user=Depends(get_current_user)`
- **POST /ai/recommend**
  - Function: `recommend_listings`
  - Response model: `RecommendResponse`
  - Response fields (from `RecommendResponse`):
    - recommendations: List[Dict[str, Any]]
    - reasoning: str
  - Parameters: `request: RecommendRequest,     db: Session = Depends(get_db),     user=Depends(get_current_user)`
- **GET /ai/health**
  - Function: `ai_health_check`

### `auth.py`
**Router prefix**: `/auth`
- **POST /auth/signup**
  - Function: `signup`
  - Response model: `SignupResponse`
  - Parameters: `payload: SignUpIn, db: Session = Depends(get_db)`
- **POST /auth/login**
  - Function: `login`
  - Response model: `Token`
  - Response fields (from `Token`):
    - access_token: str
    - token_type: str
  - Parameters: `payload: SignUpIn, db: Session = Depends(get_db)`
- **GET /auth/me**
  - Function: `me`
  - Parameters: `user: User = Depends(get_current_user)`

### `chat.py`
**Router prefix**: `/chat`
- **GET /chat/rooms**
  - Function: `get_user_chat_rooms`
  - Response model: `List[ChatRoomOut]`
  - Response fields (from `ChatRoomOut`):
    - id: int
    - listing_id: int
    - participant1_id: str
    - participant2_id: str
    - created_at: datetime
    - last_message_at: Optional[datetime]
  - Parameters: `db: Session = Depends(get_db),     current_user: User = Depends(get_current_user)`
- **GET /chat/rooms/{room_id}/messages**
  - Function: `get_chat_messages`
  - Parameters: `room_id: int,     page: int = 1,     page_size: int = 50,     db: Session = Depends(get_db),     current_user: User = Depends(get_current_user)`
- **POST /chat/rooms/{room_id}/messages/file**
  - Function: `upload_file_message`
  - Parameters: `room_id: int,     file: UploadFile = File(...),     caption: Optional[str] = Form(None),     db: Session = Depends(get_db),     current_user: User = Depends(get_current_user)`
- **POST /chat/messages/{message_id}/reactions**
  - Function: `add_reaction`
  - Parameters: `message_id: int,     reaction: str,     db: Session = Depends(get_db),     current_user: User = Depends(get_current_user)`
- **POST /chat/block/{user_id}**
  - Function: `block_user`
  - Parameters: `user_id: str,     reason: Optional[str] = None,     db: Session = Depends(get_db),     current_user: User = Depends(get_current_user)`
- **DELETE /chat/block/{user_id}**
  - Function: `unblock_user`
  - Parameters: `user_id: str,     db: Session = Depends(get_db),     current_user: User = Depends(get_current_user)`
- **GET /chat/blocked**
  - Function: `get_blocked_users`
  - Parameters: `db: Session = Depends(get_db),     current_user: User = Depends(get_current_user)`

### `favorites.py`
**Router prefix**: `/favorites`
- **POST /favorites/{listing_id}**
  - Function: `add_favorite`
  - Parameters: `listing_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)`
- **DELETE /favorites/{listing_id}**
  - Function: `remove_favorite`
  - Parameters: `listing_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)`
- **GET /favorites/**
  - Function: `list_favorites`
  - Response model: `List[FavoriteResponse]`
  - Parameters: `db: Session = Depends(get_db), user=Depends(get_current_user)`

### `listings.py`
**Router prefix**: `/listings`
- **POST /listings**
  - Function: `create_listing`
  - Response model: `ListingOut`
  - Response fields (from `ListingOut`):
    - id: int
    - title: str
    - description: str
    - category: str
    - price: Decimal
    - images: Optional[List[str]]
    - status: str
    - owner_id: str
  - Parameters: `title: str = Form(...),     description: str = Form(...),     category: str = Form(...),     price: Decimal = Form(...),     images: Optional[List[UploadFile]] = File(None),     db: Session = Depends(deps.get_db),     us...`
- **GET /listings/{listing_id}**
  - Function: `get_listing`
  - Response model: `ListingOut`
  - Response fields (from `ListingOut`):
    - id: int
    - title: str
    - description: str
    - category: str
    - price: Decimal
    - images: Optional[List[str]]
    - status: str
    - owner_id: str
  - Parameters: `listing_id: int, db: Session = Depends(deps.get_db)`
- **PATCH /listings/{listing_id}**
  - Function: `update_listing`
  - Response model: `ListingOut`
  - Response fields (from `ListingOut`):
    - id: int
    - title: str
    - description: str
    - category: str
    - price: Decimal
    - images: Optional[List[str]]
    - status: str
    - owner_id: str
  - Parameters: `listing_id: int,     payload: ListingUpdate,     db: Session = Depends(deps.get_db),     user: User = Depends(deps.get_current_user),`
- **PATCH /listings/{listing_id}/status**
  - Function: `patch_status`
  - Response model: `ListingOut`
  - Response fields (from `ListingOut`):
    - id: int
    - title: str
    - description: str
    - category: str
    - price: Decimal
    - images: Optional[List[str]]
    - status: str
    - owner_id: str
  - Parameters: `listing_id: int,     payload: ListingStatusPatch,     db: Session = Depends(deps.get_db),     user: User = Depends(deps.get_current_user),`
- **DELETE /listings/{listing_id}**
  - Status: 204
  - Function: `delete_listing`
  - Parameters: `listing_id: int,     db: Session = Depends(deps.get_db),     user: User = Depends(deps.get_current_user),`

### `notifications.py`
**Router prefix**: `/notifications`
- **GET /notifications**
  - Function: `list_notifications`
  - Response model: `List[NotificationResponse]`
  - Parameters: `skip: int = 0,      limit: int = 50,      unread_only: bool = False,     db: Session = Depends(get_db),      user=Depends(get_current_user)`
- **PATCH /notifications/{notification_id}**
  - Function: `update_notification`
  - Response model: `NotificationResponse`
  - Parameters: `notification_id: int,     update_data: NotificationUpdate,     db: Session = Depends(get_db),     user=Depends(get_current_user)`
- **POST /notifications/mark-all-read**
  - Function: `mark_all_read`
  - Parameters: `db: Session = Depends(get_db), user=Depends(get_current_user)`
- **GET /notifications/unread-count**
  - Function: `get_unread_count`
  - Parameters: `db: Session = Depends(get_db), user=Depends(get_current_user)`

### `reports.py`
**Router prefix**: `/reports`
- **POST /reports/**
  - Function: `create_report`
  - Response model: `ReportOut`
  - Response fields (from `ReportOut`):
    - id: int
    - reporter_id: str
    - reported_listing_id: Optional[int]
    - reported_user_id: Optional[str]
    - reason: str
    - status: str
    - created_at: datetime
    - reviewed_by: Optional[str]
    - reviewed_at: Optional[datetime]
    - audit_log: Optional[str]
  - Parameters: `payload: ReportCreate,     db: Session = Depends(get_db),     current_user=Depends(get_current_user)`

### `search.py`
**Router prefix**: `/`
- **GET /listings/search**
  - Function: `search_listings`
  - Parameters: `q: Optional[str] = Query(None, description="Search keyword"),     category: Optional[str] = Query(None, description="Filter by category"),     min_price: Optional[float] = Query(None, ge=0, description="Minimum price"), ...`
- **GET /listings/advanced-search**
  - Function: `advanced_search_listings`
  - Parameters: `keywords: Optional[List[str]] = Query(None, description="Multiple search keywords"),     categories: Optional[List[str]] = Query(None, description="Multiple categories"),     price_ranges: Optional[List[str]] = Query(Non...`
- **GET /listings/suggestions**
  - Function: `get_search_suggestions`
  - Parameters: `q: str = Query(..., min_length=2, description="Search query for suggestions"),     limit: int = Query(10, ge=1, le=20, description="Number of suggestions"),     db: Session = Depends(get_db)`
- **GET /listings/trending**
  - Function: `get_trending_searches`
  - Parameters: `days: int = Query(7, ge=1, le=30, description="Number of days to look back"),     limit: int = Query(10, ge=1, le=20),     db: Session = Depends(get_db)`

### `verification.py`
**Router prefix**: `/verification`
- **POST /verification/request**
  - Function: `request_verification`
  - Parameters: `payload: VerificationRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)`
- **POST /verification/verify-otp**
  - Function: `verify_otp`
  - Parameters: `payload: OTPVerify, db: Session = Depends(get_db), user: User = Depends(get_current_user)`
- **POST /verification/upload-id**
  - Function: `upload_id`
  - Parameters: `file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)`
- **GET /verification/status**
  - Function: `status`
  - Parameters: `db: Session = Depends(get_db), user: User = Depends(get_current_user)`
- **GET /verification/pending**
  - Function: `pending`
  - Parameters: `db: Session = Depends(get_db), admin: User = Depends(get_current_admin)`
- **POST /verification/approve/{user_id}**
  - Function: `approve`
  - Parameters: `user_id: str, review_action: AdminReviewAction, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)`
- **POST /verification/reject/{user_id}**
  - Function: `reject`
  - Parameters: `user_id: str, review_action: AdminReviewAction, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)`

## Updates Added
- Sign-up now requires `full_name` and `university_name`. Both are stored in the `users` table; no hardcoded domain→university mapping.
- Allowed university email domains are loaded from `app/data/allowed_domains_pk.txt` (override path via `ALLOWED_DOMAINS_FILE` env var).
- Listings endpoint now supports keyset-style pagination via `?limit=10&offset=0` (returns `total`, `count`, `next_offset`, and `items`).
- New `/profile` endpoints:
  - `GET /profile/me` — current user profile
  - `PATCH /profile/me` — update `full_name`, `phone`, `university_name`
  - `DELETE /profile/me` — delete your account (requires `password`)

> **Migrations**: Add columns `full_name`, `university_name`, `phone` to `users` table via Alembic before deploying.
