#!/bin/bash

# GLTR 웹툰 플랫폼 종료 스크립트
echo "🛑 GLTR 웹툰 플랫폼을 종료합니다..."

# 프로젝트 루트 디렉토리
PROJECT_ROOT="/home/apic/python/gltr_page"

# PID 파일 경로
PID_FILE="$PROJECT_ROOT/.server_pids"

# PID 파일이 존재하는지 확인
if [ -f "$PID_FILE" ]; then
    # PID 파일 읽기
    source "$PID_FILE"
    
    # 백엔드 서버 종료
    if [ ! -z "$BACKEND_PID" ]; then
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "📦 백엔드 서버 종료 중... (PID: $BACKEND_PID)"
            kill $BACKEND_PID
            echo "✅ 백엔드 서버 종료됨"
        else
            echo "⚠️  백엔드 서버가 이미 종료되었습니다"
        fi
    fi
    
    # 프론트엔드 서버 종료
    if [ ! -z "$FRONTEND_PID" ]; then
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "🎨 프론트엔드 서버 종료 중... (PID: $FRONTEND_PID)"
            kill $FRONTEND_PID
            echo "✅ 프론트엔드 서버 종료됨"
        else
            echo "⚠️  프론트엔드 서버가 이미 종료되었습니다"
        fi
    fi
    
    # PID 파일 삭제
    rm -f "$PID_FILE"
else
    echo "⚠️  실행 중인 서버를 찾을 수 없습니다 (PID 파일 없음)"
    echo ""
    echo "수동으로 종료를 시도합니다..."
fi

# 혹시 남아있는 프로세스 확인 및 종료
echo ""
echo "🔍 남은 프로세스 확인 중..."

# uvicorn 프로세스 종료
UVICORN_PIDS=$(pgrep -f "uvicorn main:app")
if [ ! -z "$UVICORN_PIDS" ]; then
    echo "📦 남은 백엔드 프로세스 종료 중..."
    kill $UVICORN_PIDS 2>/dev/null
    echo "✅ 백엔드 프로세스 종료됨"
fi

# react-scripts 프로세스 종료
REACT_PIDS=$(pgrep -f "react-scripts start")
if [ ! -z "$REACT_PIDS" ]; then
    echo "🎨 남은 프론트엔드 프로세스 종료 중..."
    kill $REACT_PIDS 2>/dev/null
    echo "✅ 프론트엔드 프로세스 종료됨"
fi

echo ""
echo "========================================="
echo "✨ GLTR 웹툰 플랫폼이 성공적으로 종료되었습니다!"
echo "========================================="
echo ""
echo "💡 다시 시작하려면 ./start.sh를 실행하세요."