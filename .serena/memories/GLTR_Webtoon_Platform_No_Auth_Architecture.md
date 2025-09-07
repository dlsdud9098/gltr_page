# GLTR Webtoon Platform Architecture (No Auth Version)

## Project Overview
A web-based webtoon creation and publishing platform with AI integration capabilities.
**No authentication required** - uses browser session-based management.

## Tech Stack
- **Backend**: FastAPI (Python), PostgreSQL, SQLAlchemy
- **Frontend**: React 18, Ant Design, React Router v6
- **Session Management**: Cookie-based sessions (30-day duration)
- **File Storage**: Local storage (static/uploads), ready for S3 integration

## Database Schema (Updated - No Auth)
- **webtoons**: Main webtoon metadata (session_id for ownership)
- **episodes**: Individual scenes/panels within webtoons
- **characters**: Character information per webtoon
- **edit_history**: Track all edits made to episodes (session-based)
- **comments**: Comments on webtoons (anonymous with session_id)
- **generation_sessions**: AI generation history
- **image_assets**: Image file management
- **likes**: Session-based likes (replaced user_interactions)

## API Structure (Updated - No Auth)
- `/api/webtoons/*`: Webtoon CRUD operations
- `/api/episodes/*`: Episode management
- `/api/interactions/*`: Likes and comments

## Frontend Pages (Updated - No Auth)
1. **MainPage**: Grid layout with infinite scroll
2. **WebtoonPage**: Split view with viewer and interaction tools
3. **EditorPage**: Drag-and-drop scene management (owner check via session)
4. **CreatePage**: Step-by-step webtoon creation
5. **MyWebtoonsPage**: Session-based webtoon management

## Key Features
- **No login required**: Automatic session creation via cookies
- **Session-based ownership**: 30-day cookie duration
- **Anonymous creation**: Optional author name field
- **Infinite scroll**: 2-column grid on main page
- **Drag-and-drop**: Scene reordering in editor
- **Real-time editing**: Text editing for dialogue/narration
- **Image upload**: For episodes and thumbnails
- **Responsive design**: Mobile/tablet friendly

## File Organization
```
backend/
  routers/          - API endpoint handlers
  models.py         - SQLAlchemy ORM models
  schemas.py        - Pydantic validation schemas
  session.py        - Session management utilities
  database.py       - Database connection setup
  main.py          - FastAPI application entry

frontend/src/
  pages/           - Page components
  components/      - Reusable components
  services/        - API service layer (with withCredentials)
```

## Security & Session Management
- **Cookie-based sessions**: httpOnly, SameSite=lax
- **30-day duration**: Sessions persist for 30 days
- **SHA256 session IDs**: Secure session ID generation
- **Ownership checks**: Session-based ownership verification
- **CORS configured**: Allows credentials for cookie handling

## Development Setup
1. PostgreSQL database: gltr_webtoon
2. Backend runs on port 8000
3. Frontend runs on port 3000
4. UV for Python package management
5. Environment variables in .env files

## Integration Points for text2cuts
- Generation sessions table ready for AI integration
- API structure supports batch episode creation
- Edit history tracks AI-generated vs manual edits
- Character management system in place

## Changes from Auth Version
- Removed all authentication endpoints and logic
- Replaced user_id with session_id throughout
- Added session management utilities
- Updated all ownership checks to use sessions
- Simplified frontend by removing login/register/profile pages
- Added "My Webtoons" page for session-based management
- Updated API to handle cookies properly

## Notes
- Sessions automatically created on first visit
- Each browser has independent session
- Static file serving configured for local development
- Ready for cloud storage (S3) integration
- Pagination implemented for webtoon lists
- Real-time updates using React Query