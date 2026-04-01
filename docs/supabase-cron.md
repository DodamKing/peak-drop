# Supabase pg_cron 관리

Supabase 대시보드 > SQL Editor에서 실행한다.

## 현재 설정

- **프로젝트**: dev (Seoul 리전)
- **스케줄**: 월~금 KST 9:10, KST 13:10 (2회/일)
- **동작**: pg_net으로 GitHub Actions workflow_dispatch 호출

## 현재 cron job 확인

```sql
SELECT * FROM cron.job;
```

## 기존 job 삭제

기존 KST 10:00 job이 있으면 먼저 삭제:

```sql
-- job 목록에서 jobid 확인 후
SELECT cron.unschedule(jobid);
```

## 새 job 등록

### 오전 (KST 9:10 = UTC 0:10)

```sql
SELECT cron.schedule(
  'peak-drop-morning',
  '10 0 * * 1-5',
  $$
  SELECT net.http_post(
    url := 'https://api.github.com/repos/DodamKing/peak-drop/actions/workflows/daily-report.yml/dispatches',
    headers := jsonb_build_object(
      'Authorization', 'Bearer <GITHUB_TOKEN>',
      'Accept', 'application/vnd.github.v3+json',
      'User-Agent', 'supabase-cron'
    ),
    body := jsonb_build_object('ref', 'main')
  );
  $$
);
```

### 오후 (KST 13:10 = UTC 4:10)

```sql
SELECT cron.schedule(
  'peak-drop-afternoon',
  '10 4 * * 1-5',
  $$
  SELECT net.http_post(
    url := 'https://api.github.com/repos/DodamKing/peak-drop/actions/workflows/daily-report.yml/dispatches',
    headers := jsonb_build_object(
      'Authorization', 'Bearer <GITHUB_TOKEN>',
      'Accept', 'application/vnd.github.v3+json',
      'User-Agent', 'supabase-cron'
    ),
    body := jsonb_build_object('ref', 'main')
  );
  $$
);
```

> `<GITHUB_TOKEN>` 위치에 실제 토큰을 넣는다. 토큰 저장 위치: [secrets.md](secrets.md) 참고

## 변경 이력

| 날짜 | 변경 내용 |
|------|-----------|
| 2026-03-27 | 최초 설정: KST 10:00 월~금 1회 |
| 2026-04-01 | KST 9:10 + KST 13:10 월~금 2회로 변경 |
