# Todo

## 진행 중

(없음)

## 할 일 (Backlog)

### 2단계 — 정보 확장
- [ ] 거래량 정보 추가
- [ ] yfinance fallback 검토 (FDR 장애 대비)

### 1단계 — 잔여
- [ ] 테스트 작성 및 통과 확인

### 3단계 — 고도화
- [ ] Supabase 연동 (알림 이력 저장)
- [ ] 웹 UI로 종목 관리
- [ ] 알림 임계값 설정 (예: -10% 이상일 때만 알림)
- [ ] 포트폴리오 뷰 (전체 종목 가중 평균 하락률 요약)

### 아이디어
- 멀티 채널 알림 (텔레그램, 슬랙)
- 뉴스 링크 연동
- 신고가 갱신 별도 알림

## 완료

### 1단계 (MVP) — 2026-03-25
- [x] 프로젝트 구조 생성 (uv + pyproject.toml)
- [x] fetcher.py, analyzer.py, formatter.py, notifier.py, main.py
- [x] config/watchlist.yaml
- [x] GitHub Actions 설정

### 2단계 (정보 확장) — 2026-03-25~26
- [x] Discord Embed 형식으로 메시지 개선
- [x] 하락률 구간별 색상/이모지 표시
- [x] 전일 대비 변동률 추가
- [x] 하락률 큰 순 정렬

### 2.5단계 (인프라) — 2026-03-27
- [x] Supabase pg_cron으로 GitHub Actions 정시 트리거

### 인프라/운영 — 2026-04-01
- [x] GitHub Actions schedule 제거 (Supabase pg_cron 전용으로 전환)
- [x] Supabase pg_cron 스케줄 변경: KST 9:10 + 13:10 (2회/일)
- [x] SCHD 종목 추가
- [x] pg_cron 관리 SQL 문서화 (docs/supabase-cron.md)
