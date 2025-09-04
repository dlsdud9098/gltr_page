#!/bin/bash

# 웹툰 갤러리 배포 스크립트
# publisher.gltr-ous.us 도메인으로 배포

set -e  # 에러 발생 시 스크립트 중단

echo "🚀 웹툰 갤러리 배포 시작..."

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 배포 디렉토리
DEPLOY_DIR="/var/www/webtoon-gallery"
CURRENT_DIR="$(pwd)"

# 1. 프론트엔드 빌드
echo -e "${YELLOW}📦 프론트엔드 빌드 중...${NC}"
cd frontend
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 프론트엔드 빌드 실패${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 프론트엔드 빌드 완료${NC}"

# 2. 배포 디렉토리 생성 (권한이 있는 경우)
echo -e "${YELLOW}📁 배포 디렉토리 준비 중...${NC}"
if [ -w "/var/www" ]; then
    sudo mkdir -p $DEPLOY_DIR/frontend
    sudo mkdir -p $DEPLOY_DIR/backend
else
    echo -e "${YELLOW}⚠️  /var/www 디렉토리에 쓰기 권한이 없습니다. sudo 권한이 필요합니다.${NC}"
fi

# 3. 프론트엔드 파일 복사
echo -e "${YELLOW}📋 프론트엔드 파일 복사 중...${NC}"
sudo rm -rf $DEPLOY_DIR/frontend/*
sudo cp -r build/* $DEPLOY_DIR/frontend/
echo -e "${GREEN}✅ 프론트엔드 파일 복사 완료${NC}"

# 4. 백엔드 파일 복사
cd $CURRENT_DIR
echo -e "${YELLOW}📋 백엔드 파일 복사 중...${NC}"
sudo cp -r backend/* $DEPLOY_DIR/backend/
echo -e "${GREEN}✅ 백엔드 파일 복사 완료${NC}"

# 5. Python 가상환경 및 의존성 설치
echo -e "${YELLOW}🐍 Python 환경 설정 중...${NC}"
cd $DEPLOY_DIR/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
echo -e "${GREEN}✅ Python 환경 설정 완료${NC}"

# 6. systemd 서비스 파일 생성
echo -e "${YELLOW}⚙️  Systemd 서비스 설정 중...${NC}"
sudo tee /etc/systemd/system/webtoon-backend.service > /dev/null <<EOF
[Unit]
Description=Webtoon Gallery Backend
After=network.target mongodb.service

[Service]
Type=simple
User=www-data
WorkingDirectory=$DEPLOY_DIR/backend
Environment="PATH=$DEPLOY_DIR/backend/venv/bin"
ExecStart=$DEPLOY_DIR/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 7. 서비스 시작
echo -e "${YELLOW}🔄 서비스 재시작 중...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable webtoon-backend
sudo systemctl restart webtoon-backend
echo -e "${GREEN}✅ 백엔드 서비스 시작 완료${NC}"

# 8. Nginx 설정 복사 및 활성화
echo -e "${YELLOW}🌐 Nginx 설정 중...${NC}"
cd $CURRENT_DIR
sudo cp nginx.conf /etc/nginx/sites-available/publisher.gltr-ous.us
sudo ln -sf /etc/nginx/sites-available/publisher.gltr-ous.us /etc/nginx/sites-enabled/
sudo nginx -t
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Nginx 설정 오류${NC}"
    exit 1
fi
sudo systemctl reload nginx
echo -e "${GREEN}✅ Nginx 설정 완료${NC}"

# 9. 파일 권한 설정
echo -e "${YELLOW}🔒 파일 권한 설정 중...${NC}"
sudo chown -R www-data:www-data $DEPLOY_DIR
sudo chmod -R 755 $DEPLOY_DIR
echo -e "${GREEN}✅ 파일 권한 설정 완료${NC}"

# 10. 서비스 상태 확인
echo -e "${YELLOW}📊 서비스 상태 확인...${NC}"
if systemctl is-active --quiet webtoon-backend; then
    echo -e "${GREEN}✅ 백엔드 서비스 실행 중${NC}"
else
    echo -e "${RED}❌ 백엔드 서비스 실행 실패${NC}"
    sudo journalctl -u webtoon-backend -n 50
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx 서비스 실행 중${NC}"
else
    echo -e "${RED}❌ Nginx 서비스 실행 실패${NC}"
fi

echo -e "${GREEN}🎉 배포 완료!${NC}"
echo -e "${GREEN}🌐 사이트 주소: https://publisher.gltr-ous.us${NC}"
echo ""
echo "📝 추가 작업:"
echo "1. SSL 인증서 설정 (Let's Encrypt):"
echo "   sudo certbot --nginx -d publisher.gltr-ous.us"
echo "2. MongoDB가 실행 중인지 확인:"
echo "   sudo systemctl status mongodb"
echo "3. 로그 확인:"
echo "   - 백엔드: sudo journalctl -u webtoon-backend -f"
echo "   - Nginx: sudo tail -f /var/log/nginx/publisher.gltr-ous.us.error.log"