# 시크릿 & 토큰 관리

## GitHub Personal Access Token (Fine-grained)
- **토큰 이름**: peak-drop-supabase-trigger
- **용도**: Supabase pg_cron에서 GitHub Actions workflow_dispatch 트리거
- **권한**: DodamKing/peak-drop 레포 Actions Read/Write
- **만료**: 없음
- **저장 위치**: Google Drive > 키페어 > 깃토큰 파일
- **사용 위치**: Supabase SQL (cron job 내 Authorization 헤더)

## Discord Webhook URL
- **용도**: 일일 리포트 전송
- **저장 위치**: GitHub 레포 Settings > Secrets > `DISCORD_WEBHOOK_URL`

## Supabase
- **프로젝트명**: dev (Seoul 리전)
- **DB 비밀번호 저장 위치**: Google Drive > 환경설정 > supabase > 데이터베이스 패스워드 파일
- **비밀번호 분실 시**: Supabase 대시보드 Settings > Database에서 리셋 가능
