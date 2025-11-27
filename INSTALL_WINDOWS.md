# Windows 설치 가이드

## 단계별 설치

### 1. 핵심 패키지만 먼저 설치 (권장)

```bash
pip install -r requirements-core.txt
```

이 방법으로 시스템의 **핵심 기능**을 먼저 실행할 수 있습니다:
- KIS API 연결
- 주문 실행 (모의투자/실거래)
- 데이터베이스 저장
- WebSocket 실시간 데이터

### 2. 데이터베이스 초기화

```bash
python scripts/setup_database.py
```

### 3. 시스템 실행 테스트

```bash
python src/main.py --test
```

### 4. (선택) AI/ML 패키지 설치

AI 모델 개발(Phase 4-5)이 필요할 때 설치:

```bash
# pandas, numpy, scikit-learn
pip install pandas numpy scikit-learn

# Technical analysis
pip install ta

# PyTorch (CPU 버전, Windows용)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Transformers
pip install transformers
```

## 전체 설치 (모든 의존성)

컴파일러가 설치되어 있다면:

```bash
pip install -r requirements.txt
```

### 컴파일러 설치 (선택)

numpy 등의 패키지 빌드가 필요하면:
- **Visual Studio Build Tools** 설치
- 또는 **Anaconda** 사용 (미리 컴파일된 패키지 제공)

## 문제 해결

### "No module named 'yaml'" 오류

```bash
pip install pyyaml
```

### numpy 빌드 오류

옵션 1: 미리 컴파일된 wheel 사용
```bash
pip install numpy --only-binary :all:
```

옵션 2: Anaconda 사용
```bash
conda install numpy pandas scikit-learn
```

### PostgreSQL 드라이버 설치 실패

SQLite로 충분하면 생략 가능. PostgreSQL을 사용하려면:

```bash
# 옵션 1: 바이너리 패키지
pip install psycopg2-binary

# 옵션 2: Anaconda
conda install psycopg2
```

## 최소 동작 환경

다음 패키지만 있으면 시스템이 동작합니다:
- pyyaml
- pydantic
- requests
- aiohttp
- sqlalchemy

```bash
pip install pyyaml pydantic requests aiohttp sqlalchemy
```

## 검증

설치 후 다음 명령으로 확인:

```bash
# API 테스트 (Mock 모드)
python scripts/test_api.py

# 시스템 실행
python src/main.py --mode mock
```
