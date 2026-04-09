# Peak-Drop 프로젝트 가이드

주식 고점 대비 하락률을 매일 계산해서 디스코드로 알려주는 봇.

## 프로젝트 구조

```
peak-drop/
├── CLAUDE.md                  # (이 파일) 작업 진입점
├── src/
│   ├── main.py                # 진입점 — 파이프라인 오케스트레이션
│   ├── fetcher.py             # FinanceDataReader로 주가 조회
│   ├── analyzer.py            # 고점 대비 하락률 계산
│   ├── formatter.py           # 디스코드 Embed 메시지 생성
│   └── notifier.py            # 디스코드 웹훅 전송
├── config/
│   └── watchlist.yaml         # 종목 목록 및 설정
├── .github/workflows/
│   └── daily-report.yml       # GitHub Actions 스케줄 (UTC 01:00 = KST 10:00)
├── docs/
│   ├── plan.md                # 설계 문서
│   ├── todo.md                # 할일/진행 관리
│   ├── changelog.md           # 작업 이력
│   ├── secrets.md             # 토큰/시크릿 위치 정리
│   ├── supabase-cron.md       # Supabase pg_cron 관리 (SQL 포함)
│   └── project-guide.md       # 범용 프로젝트 운영 가이드 (템플릿)
├── pyproject.toml             # 의존성 (uv 기반)
└── tests/                     # 테스트 (미작성)
```

## 실행 파이프라인

```
main.run()
  → watchlist.yaml 로드
  → 종목별 fetcher.fetch_stock_data(symbol, market) — FDR 조회
  → analyzer.analyze(data, peak_type, peak_price) — 하락률 계산
  → formatter.format_embed(results, errors, symbols, title) — Embed 생성
  → notifier.send_discord_embed(webhook_url, embed) — 전송
```

## 핵심 데이터 흐름

- **fetcher** 반환: `{symbol, current_price, prev_price, daily_change, high_52w, error}`
- **analyzer** 반환: `{symbol, current_price, peak_price, drawdown, is_new_high, daily_change}`
- **peak_type**: `auto_52w` (52주 최고가 자동) 또는 `manual` (수동 지정)
- **drawdown 공식**: `(현재가 - 고점) / 고점 * 100`

## 인프라

- **스케줄**: Supabase pg_cron이 GitHub Actions workflow_dispatch를 트리거 (KST 9:10 + 13:10, 월~금)
- **환경변수**: `DISCORD_WEBHOOK_URL` (GitHub Secrets)
- **로컬 실행**: `uv run python -m src.main` (.env에 웹훅 URL 필요)

## 개발 현황

- 1단계 MVP: 완료 (테스트 미작성)
- 2단계 정보 확장: Embed/이모지/전일비/정렬 완료, 거래량 미구현
- 2단계 안정성: FDR 재시도 + yfinance fallback 완료
- 2.5단계 인프라: Supabase pg_cron 트리거 완료
- 3단계 고도화: 미착수 (Supabase 이력 저장, 웹 UI, 알림 임계값, 포트폴리오 뷰)

## 작업 시 참고

- 할일/진행 상황 → `docs/todo.md`
- 작업 이력 → `docs/changelog.md`
- 상세 설계 → `docs/plan.md`
- Supabase pg_cron 관리 → `docs/supabase-cron.md`
- 시크릿 위치 → `docs/secrets.md`
- 종목 추가/변경 → `config/watchlist.yaml` (코드 수정 불필요)
- 기술 스택: Python 3.11+, uv, FinanceDataReader, yfinance, requests, PyYAML, python-dotenv

## 작업 규칙

- 모든 작업은 **계획 → 검토 → 개선 → 검증 → 확정 → 구현** 프로세스를 따른다
- 확정 전에는 코드를 건��리지 않는다
- 코드 작업 후 반드시 `docs/todo.md`와 `docs/changelog.md`를 함께 업데이트
- 프로젝트 구조가 바뀌면 이 파일(`CLAUDE.md`)도 업데이트
- 프로세스 상세 → `docs/project-guide.md` 3~4절 참고
