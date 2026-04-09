# Changelog

## 2026-04-09
- FDR US 주식 NaN 데이터 대응: yfinance fallback 추가
- NaN 시 밀린 데이터 대신 에러 처리 (전일비 혼동 방지)
- yfinance 의존성 추가
- fetcher.py 리팩토링: 헬퍼 분리 (_clean_df, _has_nan_close, _fetch_fdr, _fetch_yfinance, _extract_prices)
- yfinance float32 정밀도 문제 해결 (가격 round 처리)

## 2026-04-01
- GitHub Actions schedule 제거, Supabase pg_cron 전용 트리거로 전환
- Supabase pg_cron 스케줄: KST 10:00 → KST 9:10 + 13:10 (2회/일)
- SCHD 종목 추가
- pg_cron 관리 SQL 문서화 (docs/supabase-cron.md)
- docs 기반 작업 관리 체계 구축 (todo.md, changelog.md 신규)
- CLAUDE.md 생성 (프로젝트 구조 진입점)
- docs/plan.md를 순수 설계 문서로 정리
- 범용 프로젝트 운영 가이드 작성 (docs/project-guide.md)
- 작업 프로세스 정립: 계획 → 검토 → 개선 → 검증 → 확정 → 구현

## 2026-03-27
- Supabase pg_cron 연동으로 GitHub Actions 정시 트리거 구현
- GitHub Actions cron 큐 지연 문제 해결 (KST 10시 → 오후 1시+ 지연)

## 2026-03-26
- 봇 로직 수정 (Embed, 정렬, 전일비 등)

## 2026-03-25
- 프로젝트 초기 생성 (MVP)
- 봇 메시지 형식 수정
