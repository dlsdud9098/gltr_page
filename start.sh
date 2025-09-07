#!/bin/bash

# GLTR 웹툰 플랫폼 시작 스크립트
echo "🚀 GLTR 웹툰 플랫폼을 시작합니다..."

# 프로젝트 루트 디렉토리
PROJECT_ROOT="/home/apic/python/gltr_page"

# PID 파일 경로
PID_FILE="$PROJECT_ROOT/.server_pids"

# 이전 PID 파일이 있으면 삭제
rm -f "$PID_FILE"

# 사용 가능한 포트 찾기 함수
find_available_port() {
    local port=$1
    local max_port=$2
    
    while [ $port -le $max_port ]; do
        if ! lsof -Pi :$port -t >/dev/null 2>&1; then
            echo $port
            return 0
        fi
        ((port++))
    done
    
    echo -1
    return 1
}

# 백엔드 포트 찾기 (8000부터 시작)
echo "🔍 백엔드용 사용 가능한 포트 확인 중..."
BACKEND_PORT=$(find_available_port 8000 8010)

if [ $BACKEND_PORT -eq -1 ]; then
    echo "❌ 백엔드용 사용 가능한 포트를 찾을 수 없습니다 (8000-8010)"
    exit 1
fi

if [ $BACKEND_PORT -ne 8000 ]; then
    echo "⚠️  포트 8000이 사용 중입니다. 포트 $BACKEND_PORT을 사용합니다."
fi

# 프론트엔드 포트 찾기 (3000부터 시작)
echo "🔍 프론트엔드용 사용 가능한 포트 확인 중..."
FRONTEND_PORT=$(find_available_port 3000 3010)

if [ $FRONTEND_PORT -eq -1 ]; then
    echo "❌ 프론트엔드용 사용 가능한 포트를 찾을 수 없습니다 (3000-3010)"
    exit 1
fi

if [ $FRONTEND_PORT -ne 3000 ]; then
    echo "⚠️  포트 3000이 사용 중입니다. 포트 $FRONTEND_PORT을 사용합니다."
fi

# 프론트엔드 .env 파일 업데이트
echo "📝 프론트엔드 환경 변수 업데이트 중..."
echo "REACT_APP_API_URL=http://localhost:$BACKEND_PORT" > "$PROJECT_ROOT/frontend/.env"
echo "PORT=$FRONTEND_PORT" >> "$PROJECT_ROOT/frontend/.env"

# 백엔드 서버 시작
echo "📦 백엔드 서버 시작 중... (포트: $BACKEND_PORT)"
cd "$PROJECT_ROOT/backend"
source "$PROJECT_ROOT/.venv/bin/activate"
uv run uvicorn main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!
echo "BACKEND_PID=$BACKEND_PID" >> "$PID_FILE"
echo "BACKEND_PORT=$BACKEND_PORT" >> "$PID_FILE"
echo "✅ 백엔드 서버 시작됨 (PID: $BACKEND_PID, 포트: $BACKEND_PORT)"

# 백엔드가 시작될 때까지 잠시 대기
sleep 3

# 프론트엔드 서버 시작
echo "🎨 프론트엔드 서버 시작 중... (포트: $FRONTEND_PORT)"
cd "$PROJECT_ROOT/frontend"
npm start > "$PROJECT_ROOT/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "FRONTEND_PID=$FRONTEND_PID" >> "$PID_FILE"
echo "FRONTEND_PORT=$FRONTEND_PORT" >> "$PID_FILE"
echo "✅ 프론트엔드 서버 시작됨 (PID: $FRONTEND_PID, 포트: $FRONTEND_PORT)"

echo ""
echo "========================================="
echo "✨ GLTR 웹툰 플랫폼이 성공적으로 시작되었습니다!"
echo "========================================="
echo "📌 백엔드: http://localhost:$BACKEND_PORT"
echo "📌 프론트엔드: http://localhost:$FRONTEND_PORT"
echo "📌 API 문서: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "💡 종료하려면 ./stop.sh를 실행하세요."
echo "📄 로그 확인:"
echo "   - 백엔드: tail -f backend.log"
echo "   - 프론트엔드: tail -f frontend.log"