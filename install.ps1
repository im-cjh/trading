# Windows 빠른 설치 스크립트
# 최소한의 패키지만 설치하여 시스템 실행

Write-Host "================================" -ForegroundColor Cyan
Write-Host "AI Trading System 설치 시작" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 필수 패키지 개별 설치
Write-Host "[1/8] pyyaml 설치..." -ForegroundColor Green
pip install pyyaml --quiet

Write-Host "[2/8] pydantic 설치..." -ForegroundColor Green
pip install "pydantic>=2.0" --quiet

Write-Host "[3/8] requests 설치..." -ForegroundColor Green
pip install requests --quiet

Write-Host "[4/8] aiohttp 설치..." -ForegroundColor Green
pip install aiohttp --quiet

Write-Host "[5/8] websockets 설치..." -ForegroundColor Green
pip install websockets --quiet

Write-Host "[6/8] sqlalchemy 설치..." -ForegroundColor Green
pip install sqlalchemy --quiet

Write-Host "[7/8] python-json-logger 설치..." -ForegroundColor Green
pip install python-json-logger --quiet

Write-Host "[8/8] pytest 설치..." -ForegroundColor Green
pip install pytest pytest-asyncio --quiet

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "설치 완료!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Yellow
Write-Host "1. 데이터베이스 초기화: python scripts/setup_database.py" -ForegroundColor White
Write-Host "2. 시스템 실행: python src/main.py --test" -ForegroundColor White
