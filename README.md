# GLTR Webtoon Platform (No Auth Version)

AI를 활용한 창의적인 웹툰 제작 플랫폼 - 로그인 없이 사용 가능한 버전

## 📌 프로젝트 개요

GLTR Webtoon Platform은 AI 기술을 활용하여 텍스트에서 웹툰을 생성하고 편집할 수 있는 플랫폼입니다.
이 버전은 **로그인/회원가입 없이** 브라우저 세션 기반으로 작동합니다.

### 주요 기능

- **웹툰 생성 및 관리**: 새로운 웹툰을 생성하고 에피소드를 관리
- **AI 텍스트 변환**: 텍스트를 입력하면 AI가 자동으로 웹툰 장면 생성
- **드래그 앤 드롭 편집**: 장면 순서를 쉽게 변경
- **실시간 편집**: 대사, 설명, 나레이션 편집
- **무한 스크롤**: 메인 페이지에서 웹툰 목록 무한 스크롤
- **세션 기반 소유권**: 브라우저 세션으로 자신의 웹툰 관리
- **상호작용**: 좋아요, 댓글 기능

## 🛠 기술 스택

### Backend
- **FastAPI**: Python 웹 프레임워크
- **PostgreSQL**: 데이터베이스
- **SQLAlchemy**: ORM
- **Session-based**: 쿠키 기반 세션 관리
- **Uvicorn**: ASGI 서버

### Frontend
- **React 18**: UI 프레임워크
- **Ant Design**: UI 컴포넌트 라이브러리
- **React Router v6**: 라우팅
- **Axios**: HTTP 클라이언트 (withCredentials 설정)
- **React Query**: 데이터 페칭
- **React Beautiful DnD**: 드래그 앤 드롭

## 📦 설치 및 실행

### 1. PostgreSQL 데이터베이스 설정

```bash
# PostgreSQL 설치 후
createdb gltr_webtoon

# 스키마 적용
psql -U postgres -d gltr_webtoon -f database/schema.sql
```

### 2. Backend 설정

```bash
cd backend

# 가상환경 생성 (UV 사용)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
uv pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 편집하여 데이터베이스 정보 입력

# 서버 실행
python main.py
```

### 3. Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

### 4. 삭제할 파일들 (수동 삭제)

다음 파일들은 더 이상 필요하지 않으므로 삭제할 수 있습니다:
- `backend/auth.py`
- `backend/routers/auth_router.py`
- `backend/routers/users_router.py`
- `frontend/src/contexts/AuthContext.js`
- `frontend/src/components/PrivateRoute.js`
- `frontend/src/pages/LoginPage.js`
- `frontend/src/pages/LoginPage.css`
- `frontend/src/pages/RegisterPage.js`
- `frontend/src/pages/RegisterPage.css`
- `frontend/src/pages/ProfilePage.js`
- `frontend/src/pages/ProfilePage.css`

## 🗂 프로젝트 구조

```
gltr_page/
├── backend/
│   ├── routers/         # API 라우터
│   ├── static/          # 정적 파일
│   ├── database.py      # DB 연결
│   ├── main.py          # FastAPI 앱
│   ├── models.py        # SQLAlchemy 모델
│   ├── schemas.py       # Pydantic 스키마
│   └── session.py       # 세션 관리
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/  # React 컴포넌트
│       ├── pages/       # 페이지 컴포넌트
│       └── services/    # API 서비스
└── database/
    └── schema.sql       # DB 스키마
```

## 📝 API 엔드포인트

### 웹툰
- `GET /api/webtoons/`: 웹툰 목록
- `GET /api/webtoons/my`: 내 웹툰 목록 (세션 기반)
- `POST /api/webtoons/`: 웹툰 생성
- `GET /api/webtoons/{id}`: 웹툰 상세
- `PUT /api/webtoons/{id}`: 웹툰 수정 (소유자만)
- `DELETE /api/webtoons/{id}`: 웹툰 삭제 (소유자만)

### 에피소드
- `GET /api/episodes/webtoon/{id}`: 웹툰의 에피소드
- `POST /api/episodes/`: 에피소드 생성
- `PUT /api/episodes/{id}`: 에피소드 수정 (소유자만)
- `DELETE /api/episodes/{id}`: 에피소드 삭제 (소유자만)

### 상호작용
- `POST /api/interactions/like`: 좋아요 토글
- `GET /api/interactions/likes`: 내 좋아요 목록
- `POST /api/interactions/comments`: 댓글 작성
- `GET /api/interactions/comments/webtoon/{id}`: 웹툰 댓글

## 🎨 주요 페이지

1. **메인 페이지** (`/`): 웹툰 목록, 무한 스크롤
2. **웹툰 페이지** (`/webtoon/:id`): 웹툰 뷰어, 에피소드별 보기
3. **편집 페이지** (`/webtoon/:id/edit`): 드래그 앤 드롭, 씬 편집 (소유자만)
4. **생성 페이지** (`/create`): 새 웹툰 만들기, AI 텍스트 변환
5. **내 웹툰** (`/my-webtoons`): 세션 기반 내 웹툰 관리

## 🔐 세션 관리

- **브라우저 쿠키 기반**: 30일간 유지되는 세션 ID
- **자동 생성**: 첫 방문 시 자동으로 세션 생성
- **소유권 확인**: 세션 ID로 웹툰 소유권 확인
- **익명 사용**: 로그인 없이 웹툰 생성 및 관리 가능

## 🔐 환경 변수

### Backend (.env)
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/gltr_webtoon
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## 🎯 주요 특징

- **로그인 불필요**: 세션 기반으로 간편하게 사용
- **익명 작성**: 작가명을 입력하거나 익명으로 작성
- **브라우저별 관리**: 각 브라우저마다 독립적인 세션
- **30일 유지**: 세션이 30일간 유지되어 재방문 시에도 작품 관리 가능

## 📄 라이선스

MIT License

## 🤝 기여

프로젝트에 기여하고 싶으시다면 Pull Request를 보내주세요!

## 📞 문의

문의사항이 있으시면 Issue를 생성해주세요.