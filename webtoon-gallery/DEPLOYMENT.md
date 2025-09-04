# 배포 가이드 - publisher.gltr-ous.us

## 📌 도메인 정보
- **도메인**: publisher.gltr-ous.us
- **서버**: nginx 사용 중
- **백엔드 포트**: 8000
- **프론트엔드**: React 빌드 파일

## 🚀 빠른 배포

```bash
# 배포 스크립트 실행
chmod +x deploy.sh
./deploy.sh
```

## 📁 프로젝트 구조

```
/var/www/webtoon-gallery/
├── frontend/          # React 빌드 파일
│   └── (build files)
└── backend/          # FastAPI 서버
    ├── main.py
    ├── models_v2.py
    ├── database.py
    ├── import_data.py
    └── static/       # 정적 이미지 파일
```

## 🔧 수동 배포 단계

### 1. 프론트엔드 빌드
```bash
cd frontend
npm run build
```

### 2. 백엔드 서버 실행
```bash
cd backend
# 가상환경 활성화
source venv/bin/activate
# 또는 uv 사용
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Nginx 설정
```bash
# nginx.conf를 sites-available로 복사
sudo cp nginx.conf /etc/nginx/sites-available/publisher.gltr-ous.us

# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/publisher.gltr-ous.us /etc/nginx/sites-enabled/

# Nginx 재시작
sudo nginx -t  # 설정 테스트
sudo systemctl reload nginx
```

## 🔒 SSL 인증서 설정 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt-get install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d publisher.gltr-ous.us
```

## 📊 MongoDB 설정

```bash
# MongoDB 시작
sudo systemctl start mongodb

# 참조 데이터 초기화
cd backend
uv run python import_data.py --init

# 샘플 데이터 임포트
uv run python import_data.py data/sample_webtoons.json
```

## 🔍 서비스 상태 확인

```bash
# 백엔드 서비스
sudo systemctl status webtoon-backend

# Nginx
sudo systemctl status nginx

# MongoDB
sudo systemctl status mongodb
```

## 📝 로그 확인

```bash
# 백엔드 로그
sudo journalctl -u webtoon-backend -f

# Nginx 액세스 로그
sudo tail -f /var/log/nginx/publisher.gltr-ous.us.access.log

# Nginx 에러 로그
sudo tail -f /var/log/nginx/publisher.gltr-ous.us.error.log
```

## 🌐 접속 URL
- **프로덕션**: https://publisher.gltr-ous.us
- **API 문서**: https://publisher.gltr-ous.us/docs

## 📦 환경 변수

### 프론트엔드 (.env.production)
```
REACT_APP_API_URL=https://publisher.gltr-ous.us
REACT_APP_ENVIRONMENT=production
```

### 백엔드 (.env.production)
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=webtoon_gallery
DOMAIN=publisher.gltr-ous.us
```

## 🔄 업데이트 방법

1. 코드 변경 후 git push
2. 서버에서 git pull
3. 프론트엔드 재빌드 (필요시)
4. 백엔드 서비스 재시작
```bash
sudo systemctl restart webtoon-backend
```

## ⚠️ 주의사항
- MongoDB가 실행 중이어야 함
- 포트 8000이 방화벽에서 열려있어야 함 (내부용)
- 포트 80, 443이 외부에 열려있어야 함