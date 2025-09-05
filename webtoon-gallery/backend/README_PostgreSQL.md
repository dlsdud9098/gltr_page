# PostgreSQL Migration Guide

## Prerequisites
1. PostgreSQL 서버가 설치되어 있어야 합니다.
2. PostgreSQL 서버가 실행 중이어야 합니다.

## Setup Instructions

### 1. PostgreSQL 설치 (Windows)
```bash
# Chocolatey를 사용하는 경우
choco install postgresql

# 또는 공식 웹사이트에서 다운로드
# https://www.postgresql.org/download/windows/
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가합니다:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/webtoon_gallery
POSTGRES_SERVER_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/postgres
```

### 3. 의존성 설치
```bash
uv pip install asyncpg sqlalchemy alembic psycopg2-binary
```

### 4. 데이터베이스 생성 및 테이블 설정
```bash
python setup_db.py
```

### 5. 애플리케이션 실행
```bash
# PostgreSQL 버전 실행
python main_postgresql.py

# 또는
uvicorn main_postgresql:app --reload
```

## Database Schema

### Tables
- **webtoons**: 웹툰 메인 정보
- **episodes**: 에피소드 정보
- **characters**: 캐릭터 정보
- **webtoon_images**: 이미지 정보
- **storyboard_panels**: 스토리보드 패널 정보
- **genres**: 장르 마스터
- **tags**: 태그 마스터
- **webtoon_genres**: 웹툰-장르 연결 테이블
- **webtoon_tags**: 웹툰-태그 연결 테이블

## Migration from MongoDB/SQLite

기존 MongoDB 또는 SQLite에서 마이그레이션하는 경우:
1. 기존 데이터는 자동으로 삭제됩니다.
2. 샘플 데이터가 자동으로 생성됩니다.
3. 실제 데이터 마이그레이션이 필요한 경우 별도 스크립트 작성이 필요합니다.

## API Endpoints

API 엔드포인트는 기존과 동일합니다:
- `GET /api/webtoons` - 웹툰 목록 조회
- `GET /api/webtoons/{id}` - 특정 웹툰 조회
- `POST /api/webtoons` - 웹툰 생성
- `PUT /api/webtoons/{id}` - 웹툰 수정
- `DELETE /api/webtoons/{id}` - 웹툰 삭제
- `POST /api/webtoons/{id}/edit` - 웹툰 편집

## Troubleshooting

### PostgreSQL 연결 오류
```bash
# PostgreSQL 서비스 상태 확인 (Windows)
sc query postgresql

# PostgreSQL 서비스 시작 (Windows)
net start postgresql
```

### 권한 오류
PostgreSQL 사용자 권한 확인:
```sql
-- psql로 접속
psql -U postgres

-- 데이터베이스 권한 부여
GRANT ALL PRIVILEGES ON DATABASE webtoon_gallery TO postgres;
```