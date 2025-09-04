# 웹툰 갤러리

노션 스타일의 웹툰 갤러리 애플리케이션입니다.

## 프로젝트 구조

```
webtoon-gallery/
├── backend/          # FastAPI 백엔드
│   ├── main.py
│   ├── database.py   # MongoDB 연결
│   ├── models.py     # 데이터 모델
│   ├── requirements.txt
│   ├── .env         # 환경 변수
│   └── static/
│       └── images/   # 웹툰 이미지 파일
├── frontend/         # React 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   ├── api/
│   │   ├── types/
│   │   └── styles/
│   └── package.json
└── docker-compose.yml # MongoDB 설정
```

## 실행 방법

### 1. MongoDB 실행

```bash
# Docker Compose를 사용하는 경우
docker-compose up -d

# 또는 로컬 MongoDB를 사용하는 경우
# MongoDB를 직접 설치하고 실행
```

### 2. 백엔드 실행

```bash
cd backend
pip install -r requirements.txt

# .env 파일 생성 (필요 시 수정)
cp .env.example .env

# 서버 실행
uvicorn main:app --reload --port 8000
```

### 3. 프론트엔드 실행

```bash
cd frontend
npm install
npm start
```

## 데이터베이스 구조

MongoDB에 저장되는 웹툰 데이터:

- **기본 정보**: 제목, 설명, 장르, 작가, 썸네일
- **에피소드**: 각 에피소드별 이미지, 스토리보드
- **제작 데이터**:
  - 캐릭터 정보 (이름, 설명, 디자인 프롬프트)
  - 스토리보드 (패널별 설명, 대사, 카메라 앵글)
  - 생성 프롬프트 (메인, 스타일, 씬별)
  - 이미지 생성 정보 (URL, 타입, 생성 날짜)
- **메타데이터**: 생성일, 수정일, 조회수, 좋아요 수

## 기능

- 메인 페이지: 
  - 웹툰 섬네일 갤러리 (세로 스크롤)
  - 무한 스크롤 (5개씩 로드)
- 상세 페이지: 
  - 왼쪽: 웹툰 이미지 (세로 스크롤)
  - 오른쪽: 웹툰 정보 및 편집 패널
- API 기능:
  - CRUD 작업 (생성, 조회, 수정, 삭제)
  - 필터링 (장르, 상태)
  - 페이지네이션

## 접속

- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- MongoDB: mongodb://localhost:27017