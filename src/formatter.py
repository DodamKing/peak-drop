from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))


def _format_price(price: float, market: str) -> str:
    if market == "KR":
        return f"₩{price:,.0f}"
    return f"${price:,.2f}"


def format_report(
    results: list[dict],
    errors: list[dict],
    symbols_config: list[dict],
    title: str,
) -> str:
    """디스코드 메시지를 생성한다."""
    now = datetime.now(KST)
    config_map = {s["symbol"]: s for s in symbols_config}

    lines = [f"📉 {title} ({now.strftime('%Y-%m-%d')} KST)"]
    lines.append("━" * 30)

    for r in results:
        cfg = config_map.get(r["symbol"], {})
        name = cfg.get("name", r["symbol"])
        market = cfg.get("market", "US")

        display = f"{name} ({r['symbol']})" if name != r["symbol"] else r["symbol"]

        current_str = _format_price(r["current_price"], market)
        peak_str = _format_price(r["peak_price"], market)

        lines.append("")
        if r["is_new_high"]:
            lines.append(f"🔥 {display}")
            lines.append(f"  종가: {current_str} | 고점: {peak_str}")
            lines.append(f"  🎉 신고가 갱신!")
        else:
            lines.append(f"{display}")
            lines.append(f"  종가: {current_str} | 고점: {peak_str}")
            lines.append(f"  하락률: {r['drawdown']}%")

    if errors:
        lines.append("")
        lines.append("⚠️ 조회 실패:")
        for e in errors:
            cfg = config_map.get(e["symbol"], {})
            name = cfg.get("name", e["symbol"])
            lines.append(f"  {name} ({e['symbol']}): {e['error']}")

    return "\n".join(lines)
