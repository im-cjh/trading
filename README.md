# AI Trading System (KIS API)

한국투자증권(KIS) API를 활용한 AI 기반 자동 매매 시스템

## 시스템 아키텍처

```
데이터 수집 → 특징 추출 → AI 예측 → 전략 생성 → 주문 실행 → 모니터링
```

### 주요 컴포넌트

1. **Data Sources**: KIS 시세 API (REST + WebSocket)
2. **Data Ingestion**: Kafka + Redis 실시간 데이터 파이프라인
3. **Feature Store**: 기술지표 계산 (MACD, RSI, ATR)
4. **AI Model Server**: Transformer/LSTM 기반 예측
5. **Strategy Engine**: 리스크 관리 및 시그널 생성
6. **Order Executor**: KIS API 주문 실행
7. **Monitoring**: 대시보드 및 로깅
8. **Database**: PostgreSQL/SQLite 데이터 저장

## 설치 및 실행

### 사전 요구사항

- Python 3.9+
- Docker & Docker Compose
- 한국투자증권 API 인증 정보

### 설치

#### Windows 사용자

```bash
# 핵심 패키지만 설치 (권장)
pip install -r requirements-core.txt

# 데이터베이스 초기화
python scripts/setup_database.py
```

자세한 내용: [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)

#### Linux/Mac 사용자

```bash
# 전체 의존성 설치
pip install -r requirements.txt

# 데이터베이스 초기화
python scripts/setup_database.py
```

### 실행

```bash
# Docker 서비스 시작 (Kafka, Redis, PostgreSQL)
docker-compose up -d

# 모의 투자 모드로 실행
python src/main.py --mode mock

# 실거래 모드로 실행 (주의!)
python src/main.py --mode real
```

### 백테스팅

```bash
# 전략 백테스트
python scripts/backtest.py --start-date 2024-01-01 --end-date 2024-11-01
```

## 설정

설정 파일은 `config/` 디렉토리에 위치:

- `config.yaml`: 메인 설정 (API 엔드포인트, 리스크 파라미터)
- `credentials.yaml`: API 인증 정보 (git에서 제외됨)
- `logging_config.yaml`: 로깅 설정

### 모의투자 ↔ 실거래 전환

`config/config.yaml`에서 `trading_mode` 설정:

```yaml
trading_mode: mock  # 'mock' 또는 'real'
```

또는 실행 시 인자로 지정:

```bash
python src/main.py --mode real
```

## 리스크 관리

시스템은 다음 리스크 관리 기능을 포함:

- 일일 최대 손실 한도
- 종목별/전체 포지션 크기 제한
- 일일 최대 거래 횟수
- 긴급 중지 메커니즘
- 트레일링 스탑

## 모니터링

- **대시보드**: http://localhost:8000/dashboard
- **API 문서**: http://localhost:8000/docs
- **로그**: `logs/` 디렉토리

## 프로젝트 구조

```
stock/
├── config/                 # 설정 파일
├── src/
│   ├── api/               # KIS API 클라이언트
│   ├── ingestion/         # 데이터 수집
│   ├── features/          # 특징 추출
│   ├── models/            # AI 모델
│   ├── strategy/          # 거래 전략
│   ├── execution/         # 주문 실행
│   ├── monitoring/        # 모니터링
│   └── database/          # 데이터베이스
├── tests/                 # 테스트
├── scripts/               # 유틸리티 스크립트
└── docker-compose.yml     # Docker 설정
```

## 라이센스

MIT License
