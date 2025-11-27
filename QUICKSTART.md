# 빠른 시작 가이드

## 1단계: 의존성 설치

```bash
pip install -r requirements.txt
```

## 2단계: 데이터베이스 초기화

```bash
python scripts/setup_database.py
```

## 3단계: 모드 확인

```bash
python scripts/switch_mode.py show
```

## 4단계(선택): Docker 서비스 시작

Kafka, Redis, PostgreSQL을 사용하려면:

```bash
docker-compose up -d
```

## 5단계: 시스템 실행

```bash
# 모의투자 모드로 시작
python src/main.py --mode mock

# 또는 테스트 모드
python src/main.py --test
```

## 모드 전환

```bash
# 모의투자 모드로 전환
python scripts/switch_mode.py mock

# 실거래 모드로 전환 (주의!)
python scripts/switch_mode.py real
```

## 테스트 실행

```bash
pytest tests/test_integration.py -v
```

## API 연결 테스트

```bash
python scripts/test_api.py
```
