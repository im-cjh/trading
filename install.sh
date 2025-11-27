#!/bin/bash
# Linux/Mac용 설치 스크립트

echo "================================"
echo "AI Trading System 설치 시작"
echo "================================"
echo ""

# 필수 패키지 설치
echo "[1/8] pyyaml 설치..."
pip install pyyaml --quiet

echo "[2/8] pydantic 설치..."
pip install "pydantic>=2.0" --quiet

echo "[3/8] requests 설치..."
pip install requests --quiet

echo "[4/8] aiohttp 설치..."
pip install aiohttp --quiet

echo "[5/8] websockets 설치..."
pip install websockets --quiet

echo "[6/8] sqlalchemy 설치..."
pip install sqlalchemy --quiet

echo "[7/8] python-json-logger 설치..."
pip install python-json-logger --quiet

echo "[8/8] pytest 설치..."
pip install pytest pytest-asyncio --quiet

echo ""
echo "================================"
echo "설치 완료!"
echo "================================"
echo ""
echo "다음 단계:"
echo "1. 데이터베이스 초기화: python scripts/setup_database.py"
echo "2. 시스템 실행: python src/main.py --test"
