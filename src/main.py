import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.fetcher import fetch_stock_data
from src.analyzer import analyze
from src.formatter import format_report
from src.notifier import send_discord

load_dotenv()


def load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config" / "watchlist.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run():
    config = load_config()
    symbols = config["symbols"]
    title = config["settings"]["report_title"]
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")

    results = []
    errors = []

    for item in symbols:
        data = fetch_stock_data(item["symbol"], item["market"])

        if data.get("error"):
            errors.append(data)
            continue

        result = analyze(data, item["peak_type"], item.get("peak_price"))
        result["name"] = item.get("name", item["symbol"])
        results.append(result)

    message = format_report(results, errors, symbols, title)
    print(message)

    if not webhook_url:
        print("\n[WARN] DISCORD_WEBHOOK_URL이 설정되지 않아 전송을 건너뜁니다.")
        return

    try:
        send_discord(webhook_url, message)
        print("\n[OK] 디스코드 전송 완료")
    except Exception as e:
        error_msg = f"⚠️ Peak-Drop 전송 실패: {e}"
        print(f"\n[ERROR] {error_msg}")
        try:
            send_discord(webhook_url, error_msg)
        except Exception:
            pass


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")
        if webhook_url:
            try:
                send_discord(webhook_url, f"⚠️ Peak-Drop 스크립트 오류: {e}")
            except Exception:
                pass
        sys.exit(1)
