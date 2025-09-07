#!/bin/bash

# GLTR 웹툰 플랫폼 시작 스크립트
echo "🚀 GLTR 웹툰 플랫폼을 시작합니다..."

# 프로젝트 루트 디렉토리
PROJECT_ROOT="/home/apic/python/gltr_page"

# PID 파일 경로
PID_FILE="$PROJECT_ROOT/.server_pids"

# 이전 PID 파일이 있으면 삭제
rm -f "$PID_FILE"

# 백엔드 서버 시작
echo "📦 백엔드 서버 시작 중..."
cd "$PROJECT_ROOT/backend"
source "$PROJECT_ROOT/.venv/bin/activate"
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!
echo "BACKEND_PID=$BACKEND_PID" >> "$PID_FILE"
echo "✅ 백엔드 서버 시작됨 (PID: $BACKEND_PID)"

# 백엔드가 시작될 때까지 잠시 대기
sleep 3

# 프론트엔드 서버 시작
echo "🎨 프론트엔드 서버 시작 중..."
cd "$PROJECT_ROOT/frontend"
npm start > "$PROJECT_ROOT/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "FRONTEND_PID=$FRONTEND_PID" >> "$PID_FILE"
echo "✅ 프론트엔드 서버 시작됨 (PID: $FRONTEND_PID)"

echo ""
echo "========================================="
echo "✨ GLTR 웹툰 플랫폼이 성공적으로 시작되었습니다!"
echo "========================================="
echo "📌 백엔드: http://localhost:8000"
echo "📌 프론트엔드: http://localhost:3000"
echo "📌 API 문서: http://localhost:8000/docs"
echo ""
echo "💡 종료하려면 ./stop.sh를 실행하세요."
echo "📄 로그 확인:"
echo "   - 백엔드: tail -f backend.log"
echo "   - 프론트엔드: tail -f frontend.log"