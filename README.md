# Peak-Drop

보유/관심 종목의 **고점 대비 하락률**을 매일 계산하여 디스코드로 알려주는 봇.

## 기능

- 매일 KST 10:00 자동 실행 (GitHub Actions)
- 종목별 현재가, 52주 최고가, 고점 대비 하락률 계산
- 디스코드 웹훅으로 리포트 전송
- 한국/미국 주식 모두 지원

## 디스코드 알림 예시

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

## 설정

### 1. 종목 설정

`config/watchlist.yaml`에서 종목을 추가/수정합니다.

```yaml
symbols:
  - symbol: QQQ
    name: Invesco QQQ
    market: US
    peak_type: auto_52w        # 52주 최고가 자동 조회
  - symbol: "005930"
    name: 삼성전자
    market: KR
    peak_type: manual          # 수동 고점 지정
    peak_price: 88000
```

### 2. 디스코드 웹훅

GitHub Settings > Secrets에 `DISCORD_WEBHOOK_URL`을 등록합니다.

### 3. 로컬 실행

```bash
uv sync
cp .env.example .env
# .env에 DISCORD_WEBHOOK_URL 입력
uv run python -m src.main
```

## 기술 스택

- Python 3.11+ / uv
- FinanceDataReader
- Discord Webhook
- GitHub Actions
