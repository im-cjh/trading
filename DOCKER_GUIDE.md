# Docker 환경 가이드

이 가이드는 **Rocky Linux 9 + Zsh** 환경으로 구성된 Docker 컨테이너를 사용하여 트레이딩 시스템을 설정하고 테스트하는 방법을 설명합니다.

## 1. 사전 준비

*   **Docker Desktop**이 설치되어 있고 실행 중이어야 합니다.

## 2. 환경 구축 및 실행

다음 명령어로 전체 시스템(DB, Kafka, Redis, Trading Bot)을 구축하고 실행합니다.

```bash
# 이미지 빌드 및 백그라운드 실행
docker-compose up -d --build
```

*   최초 실행 시 이미지를 다운로드하고 빌드하느라 시간이 조금 걸릴 수 있습니다.
*   실행 후에는 `trading-bot` 컨테이너가 대기 모드(`tail -f /dev/null`)로 실행됩니다.

## 3. 컨테이너 접속

구축된 리눅스 환경에 접속합니다. (Root 권한, Zsh 쉘)

```bash
docker exec -it trading-bot zsh
```

접속하면 `af-magic` 테마가 적용된 Zsh 터미널이 나타납니다.

## 4. 테스트 및 실행

컨테이너 내부에서 다음 명령어로 시스템을 테스트할 수 있습니다.

### 모의투자 모드 (테스트용)

```bash
python3 -m src.main --mode mock
```

*   실제 주문을 내지 않고 로그만 출력합니다.
*   시스템이 정상적으로 동작하는지 확인하는 용도입니다.

### 실전투자 모드 (주의!)

```bash
python3 -m src.main --mode real
```

*   **실제 계좌에서 주문이 발생합니다.**
*   `config/credentials.yaml` 파일이 올바르게 설정되어 있어야 합니다.

## 5. 유용한 명령어

### 로그 확인

컨테이너 밖에서 로그를 확인하려면:

```bash
docker-compose logs -f trading-bot
```

### 시스템 종료

```bash
docker-compose down
```

### 재빌드 (Dockerfile 수정 시)

```bash
docker-compose up -d --build
```
