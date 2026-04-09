# Peak-Drop (개인용 주식 고점 대비 하락률 알림 봇) 프로젝트 설계 문서

## 1. 개요
- **프로젝트명**: peak-drop
- **목적**: 보유/관심 종목의 **고점 대비 하락률**을 매일 정해진 시간에 계산하여 **디스코드로 리포트 알림**을 전송
- **특징**:
  - 실시간이 아닌 **일 1회 배치 리포트**
  - **무료 운영** (GitHub Actions)
  - **웹 UI/DB 없이 시작** (설정 파일 기반)
  - **점진적 정보 확장** — MVP는 핵심 지표만, 이후 정보를 추가해 나감
- **확장성**: 필요 시 Supabase + 웹 UI로 확장 가능

---

## 2. 핵심 요구사항
- 매일 한국시간 오전 10시에 실행
- 종목별:
  - 현재가 (전일 종가 기준)
  - 기준 고점 (52주 최고가 또는 수동 설정)
  - 고점 대비 하락률 계산
  - 최고가 갱신 여부 확인
- 결과를 **디스코드 웹훅으로 전송**
- API 실패 시 **에러 알림** 전송

---

## 3. 시스템 구조

```
GitHub Actions (cron: KST 10:00)
        ↓
    Python Script
        ↓
  FinanceDataReader로 가격 조회
        ↓
   고점/하락률 계산
        ↓
   리포트 생성
        ↓
Discord Webhook 전송
   (성공 리포트 or 에러 알림)
```

---

## 4. 기술 스택
- **언어**: Python 3.11+
- **패키지 관리**: uv (Astral) — 빠른 의존성 관리, `pyproject.toml` 기반
- **라이브러리**:
  - `FinanceDataReader` — 한국/미국 주식 데이터 조회 (한국 주식 지원, 안정적)
  - `requests` — Discord Webhook 전송
  - `PyYAML` — 설정 파일 파싱
  - `python-dotenv` — 로컬 개발용 `.env` 파일 지원
- **실행 환경**: GitHub Actions
- **알림 채널**: Discord Webhook
- **설정 관리**: YAML 파일
- **데이터 기준**: 전일 종가 기준 (KST 10:00 실행 시 한국 장중이나 전일 종가 데이터 사용)

---

## 5. 프로젝트 구조

```
peak-drop/
 ├── src/
 │   ├── __init__.py
 │   ├── main.py              # 엔트리포인트
 │   ├── fetcher.py            # 가격 데이터 조회 (FDR 래핑)
 │   ├── analyzer.py           # 고점/하락률 계산 로직
 │   ├── formatter.py          # 디스코드 메시지 포맷팅
 │   └── notifier.py           # Discord Webhook 전송
 ├── config/
 │   └── watchlist.yaml        # 종목 및 설정
 ├── tests/
 │   ├── test_fetcher.py
 │   ├── test_analyzer.py
 │   └── test_formatter.py
 ├── .github/
 │   └── workflows/
 │       └── daily-report.yml  # 스케줄 실행 설정
 ├── pyproject.toml             # 의존성 및 프로젝트 설정 (uv)
 ├── .env.example               # 환경변수 템플릿
 ├── .gitignore
 └── docs/
     └── plan.md               # 이 문서
```

### 구조 설계 이유
- **src/ 모듈 분리**: 역할별로 파일을 나누어 테스트와 유지보수가 쉬움
- **config/ 분리**: 코드와 설정을 분리하여 종목 추가/변경이 코드 수정 없이 가능
- **tests/**: 핵심 로직(계산, 포맷)은 테스트로 검증

---

## 6. 설정 파일 (config/watchlist.yaml)

```yaml
symbols:
  - symbol: QQQ
    name: Invesco QQQ
    market: US
    peak_type: manual
    peak_price: 478
  - symbol: NVDA
    name: NVIDIA
    market: US
    peak_type: auto_52w
  - symbol: 005930
    name: 삼성전자
    market: KR
    peak_type: auto_52w

settings:
  report_title: "Peak-Drop Daily Report"
```

---

## 7. 주요 로직

### 7.1 가격 조회 (fetcher.py)
- FinanceDataReader로 전일 종가 및 52주 데이터 조회
- 한국 종목(숫자 코드)과 미국 종목(알파벳 심볼) 모두 지원
- 조회 실패 시 해당 종목을 에러로 표시하고 나머지는 계속 처리

### 7.2 고점 계산 (analyzer.py)
- `manual`: 설정값 사용
- `auto_52w`: 52주 최고가 자동 조회

### 7.3 하락률 계산
```
drawdown = (현재가 - 고점) / 고점 × 100
```

### 7.4 리포트 생성 (formatter.py)
- Discord Embed 형식으로 깔끔하게 포맷팅
- 하락률 구간별 색상 표시 (향후)

### 7.5 알림 전송 (notifier.py)
- Discord Webhook POST 요청
- 성공 시 리포트 전송, 실패 시 에러 요약 전송

---

## 8. GitHub Actions 설정 (daily-report.yml)

```yaml
name: Peak-Drop Daily Report

on:
  schedule:
    - cron: '0 1 * * *'  # UTC 01:00 = KST 10:00
  workflow_dispatch:       # 수동 실행 지원

jobs:
  report:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync

      - name: Run report
        env:
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
        run: uv run python -m src.main
```

---

## 9. 디스코드 알림 예시

### 정상 리포트
```
📉 Peak-Drop Daily Report (2025-01-15 KST)
━━━━━━━━━━━━━━━━━━━━━━━

Invesco QQQ (QQQ)
  종가: $583.98 | 고점: $635.77
  하락률: -8.15%

NVIDIA (NVDA)
  종가: $175.20 | 고점: $207.04
  하락률: -15.38%

삼성전자 (005930)
  종가: ₩193,300 | 고점: ₩218,000
  하락률: -11.33%
```

### 에러 발생 시
```
⚠️ Peak-Drop Report — 일부 오류 발생

정상 조회: QQQ, NVDA
조회 실패: 005930 (데이터 조회 실패)
```

---

## 10. 에러 처리 전략
- **종목별 독립 처리**: 한 종목 실패가 전체를 멈추지 않음
- **에러 알림**: 실패 종목이 있으면 디스코드에 에러 요약 포함
- **전체 실패**: 스크립트 자체 에러 시 에러 메시지를 디스코드로 전송

---

## 11. 배포 방식
1. GitHub 저장소 생성 (peak-drop)
2. 코드 push
3. GitHub Settings > Secrets에 `DISCORD_WEBHOOK_URL` 등록
4. Actions 자동 실행 확인
5. `workflow_dispatch`로 수동 테스트 가능

---

## 12. 참고 사항
- **FDR 안정성**: FDR NaN 대응 완료 — 재시도(2회) + yfinance fallback(US) + NaN 행 자동 제거
- **데이터 시점**: KST 10:00 실행 시 한국 장은 개장 중이나, 조회 데이터는 전일 종가 기준. 미국 주식은 전일 장 마감(ET 16:00) 후 확정된 데이터 사용
- **uv 로컬 개발**: `uv sync`로 의존성 설치, `uv run python -m src.main`으로 실행

