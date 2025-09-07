# GLTR Webtoon Platform Architecture

## Project Overview
A web-based webtoon creation and publishing platform with AI integration capabilities.

## Tech Stack
- **Backend**: FastAPI (Python), PostgreSQL, SQLAlchemy
- **Frontend**: React 18, Ant Design, React Router v6
- **Authentication**: JWT-based auth with FastAPI security
- **File Storage**: Local storage (static/uploads), ready for S3 integration

## Database Schema
- **users**: User accounts and authentication
- **webtoons**: Main webtoon metadata
- **episodes**: Individual scenes/panels within webtoons
- **characters**: Character information per webtoon
- **edit_history**: Track all edits made to episodes
- **user_interactions**: Views, likes, bookmarks
- **comments**: User comments on webtoons
- **generation_sessions**: AI generation history
- **image_assets**: Image file management

## API Structure
- `/api/auth/*`: Authentication endpoints
- `/api/webtoons/*`: Webtoon CRUD operations
- `/api/episodes/*`: Episode management
- `/api/users/*`: User management
- `/api/interactions/*`: User interactions (likes, comments)

## Frontend Pages
1. **MainPage**: Grid layout with infinite scroll
2. **WebtoonPage**: Split view with viewer and interaction tools
3. **EditorPage**: Drag-and-drop scene management
4. **CreatePage**: Step-by-step webtoon creation
5. **ProfilePage**: User dashboard with statistics

## Key Features
- Infinite scroll on main page (2-column grid)
- Drag-and-drop scene reordering in editor
- Real-time text editing for dialogue/narration
- Image upload for episodes
- User roles: user, creator, admin
- Responsive design for mobile/tablet

## File Organization
```
backend/
  routers/     - API endpoint handlers
  models.py    - SQLAlchemy ORM models
  schemas.py   - Pydantic validation schemas
  auth.py      - JWT authentication logic
  database.py  - Database connection setup
  main.py      - FastAPI application entry

frontend/src/
  pages/       - Page components
  components/  - Reusable components
  contexts/    - React Context (AuthContext)
  services/    - API service layer
```

## Security
- JWT tokens for authentication
- Password hashing with bcrypt
- CORS configured for local development
- Role-based access control (user/creator/admin)

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

## Notes
- Static file serving configured for local development
- Ready for cloud storage (S3) integration
- Pagination implemented for webtoon lists
- Real-time updates using React Query