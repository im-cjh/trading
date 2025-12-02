# 🧠 AI Trading Research System

**한국투자증권(KIS) API 기반의 AI 자동 매매 및 리서치 플랫폼**

이 시스템은 단순한 자동 매매를 넘어, **뉴스 데이터 수집, AI 감성 분석, 펀더멘털 분석**을 통해 유망 종목을 스스로 발굴하고, **5가지 전략**을 동시에 시뮬레이션하여 최적의 수익 모델을 찾는 연구용 플랫폼입니다.

---

## 시스템 아키텍처

```mermaid
graph TD
    subgraph "1. Data Layer"
        A[KIS API] --> B(Market Data)
        C[Naver News] --> D(News Crawler)
    end

    subgraph "2. Universe Selector"
        D --> E[Sentiment Analyzer<br/>(KR-FinBert-SC)]
        B --> F[Fundamental Analyzer<br/>(Momentum/Value)]
        E & F --> G[Universe Selector]
        G --> H[(Watchlist.json)]
    end

    subgraph "3. Strategy Engine"
        H --> I{Strategy Pool}
        I --> S1[RSI Strategy]
        I --> S2[SMA Strategy]
        I --> S3[Bollinger Strategy]
        I --> S4[MACD Strategy]
        I --> S5[Stochastic Strategy]
    end

    subgraph "4. Execution & Simulation"
        S1 & S2 & S3 & S4 & S5 --> J[Virtual Executor]
        J --> K[(Virtual Trades DB)]
        S1 & S2 & S3 & S4 & S5 --> L[Real Executor]
        L --> M[KIS Order System]
    end

    subgraph "5. Automation"
        N[Scheduler] -->|Weekly| G
        N -->|Real-time| I
    end
```

## ✨ 주요 기능

### 1️⃣ 자동 종목 선정 (Universe Selector)
*   **News Crawler**: 네이버 금융 주요 뉴스를 실시간으로 수집
*   **AI 감성 분석**: `snunlp/KR-FinBert-SC` 모델을 사용하여 뉴스의 긍/부정 점수 산출
*   **모멘텀/펀더멘털 분석**:
    *   **Factor (40%)**: ROE, PER, EPS 성장률
    *   **Supply (30%)**: 외국인/기관 수급 분석
    *   **Volatility (30%)**: 저변동성 종목 우대
*   **주간 리밸런싱**: 매주 월요일 08:00에 Top 15 종목 자동 갱신

### 2️⃣ 멀티 전략 시뮬레이션 (Multi-Strategy)
5가지 알고리즘이 동시에 돌아가며 경쟁합니다:
*   **RSI**: 과매수/과매도 역추세 매매
*   **SMA**: 이동평균선 골든/데드크로스 추세 매매
*   **Bollinger**: 볼린저 밴드 상/하단 터치 매매
*   **MACD**: MACD 시그널 교차 매매
*   **Stochastic**: 스토캐스틱 오실레이터 매매

### 3️⃣ 베이지안 최적화 (Bayesian Optimization) 🆕
*   **자동 파라미터 튜닝**: 과거 데이터로 각 전략의 최적 파라미터 자동 탐색
*   **백테스팅 프레임워크**: 실제 시장 데이터로 전략 성과 검증
*   **주간 자동 재최적화**: 매주 일요일 새벽 2시에 자동으로 파라미터 업데이트
*   **성과 비교 대시보드**: 전략별 수익률, 승률, 샤프비율을 시각화
*   **CPU 전용**: GPU 없이도 일반 PC에서 실행 가능 ✅

### 4️⃣ 가상 매매 엔진 (Virtual Trading)
*   실제 계좌를 쓰지 않고도 전략의 성과를 검증할 수 있는 가상 매매 시스템 탑재
*   `virtual_trades` 테이블에 전략별 수익률, 승률, MDD 등을 별도로 기록

---

## 🚀 설치 및 실행

이 프로젝트는 **Docker 환경(권장)**과 **로컬 환경** 모두를 지원합니다.

### 옵션 A: Docker 환경 (권장)
가장 간편한 방법입니다. 모든 의존성(DB, Redis, Kafka, AI 라이브러리)이 자동으로 설정됩니다.

1. **설치 및 빌드**
   ```bash
   git clone https://github.com/your-repo/ai-trading-system.git
   cd ai-trading-system
   cp config/credentials.yaml.template config/credentials.yaml
   # (credentials.yaml에 API 키 입력)
   
   docker-compose up -d --build
   ```

2. **실행 (통합 모드)**
   ```bash
   # 스케줄러 + 트레이딩 봇 동시 실행
   docker exec -it trading-bot python3 -m src.main --mode mock
   ```

3. **성과 분석**
   ```bash
   docker exec -it trading-bot python3 scripts/analyze_strategies.py
   ```

---

### 옵션 B: 로컬 환경 (개발용)
직접 Python 환경을 구성하고 싶을 때 사용합니다.

1. **의존성 설치**
   ```bash
   # Python 3.9+ 필요
   pip install -r requirements.txt
   pip install -r requirements-ml.txt
   ```

2. **데이터베이스 초기화**
   ```bash
   python scripts/setup_database.py
   ```

3. **인프라 실행 (Docker Compose)**
   DB, Redis, Kafka는 Docker로 띄우는 것이 편리합니다.
   ```bash
   docker-compose up -d postgres redis kafka zookeeper
   ```

4. **실행**
   ```bash
   python -m src.main --mode mock
   ```

---

## 🛠️ 유틸리티 명령어

### 모드 전환 및 확인
```bash
# 현재 모드 확인
python scripts/switch_mode.py show

# 모의투자/실전투자 전환
python scripts/switch_mode.py mock
python scripts/switch_mode.py real
```

### 베이지안 최적화 🆕
```bash
# 전략 파라미터 최적화 (30분~2시간 소요)
python scripts/optimize_strategies.py

# 최적화 결과 확인 (차트 + 테이블)
python scripts/view_optimization_results.py

# 최적 파라미터 적용
python scripts/apply_optimized_params.py
```

### 테스트 및 검증
```bash
# API 연결 테스트
python scripts/test_api.py

# 전체 단위 테스트
pytest tests/

# 전략 성과 분석
python scripts/analyze_strategies.py
```

---

## 📂 프로젝트 구조
```
trading/
├── config/                 # 설정 파일 (API 키, 종목 리스트)
├── src/
│   ├── analysis/          # AI/펀더멘털 분석 (Sentiment, Fundamentals)
│   ├── data/              # 데이터 수집 (Crawler)
│   ├── database/          # DB 모델 (Schema)
│   ├── strategy/          # 매매 전략 (RSI, SMA, MACD...)
│   ├── universe/          # 종목 선정 엔진 (Selector)
│   ├── main.py            # 메인 실행 파일
│   ├── scheduler.py       # 스케줄러
│   └── simulation.py      # 시뮬레이션 전용 러너
├── scripts/               # 유틸리티 (DB셋업, 분석)
├── Dockerfile             # Rocky Linux 9 이미지 빌드 설정
└── docker-compose.yml     # 컨테이너 오케스트레이션
```

## 🛠️ 기술 스택
*   **Language**: Python 3.9
*   **OS**: Rocky Linux 9
*   **AI/ML**: PyTorch, Transformers (BERT), Scikit-learn
*   **Data**: Pandas, NumPy, TA-Lib
*   **Infra**: Docker, PostgreSQL, Redis, Kafka
