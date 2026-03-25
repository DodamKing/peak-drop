from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))


def _format_price(price: float, market: str) -> str:
    if market == "KR":
        return f"₩{price:,.0f}"
    return f"${price:,.2f}"


def _drawdown_emoji(drawdown: float) -> str:
    if drawdown >= 0:
        return "🔥"
    if drawdown > -5:
        return "🟢"
    if drawdown > -10:
        return "🟡"
    if drawdown > -20:
        return "🟠"
    return "🔴"


def _daily_change_str(change: float) -> str:
    sign = "+" if change >= 0 else ""
    return f"{sign}{change}%"


def _embed_color(worst_drawdown: float) -> int:
    """가장 큰 하락률 기준으로 embed 색상을 결정한다."""
    if worst_drawdown >= 0:
        return 0x00FF00  # green
    if worst_drawdown > -5:
        return 0x57F287  # light green
    if worst_drawdown > -10:
        return 0xFEE75C  # yellow
    if worst_drawdown > -20:
        return 0xF97316  # orange
    return 0xED4245  # red


def format_embed(
    results: list[dict],
    errors: list[dict],
    symbols_config: list[dict],
    title: str,
) -> dict:
    """디스코드 Embed 메시지를 생성한다."""
    now = datetime.now(KST)
    config_map = {s["symbol"]: s for s in symbols_config}

    # 하락률 큰 순으로 정렬
    sorted_results = sorted(results, key=lambda r: r["drawdown"])

    fields = []
    for r in sorted_results:
        cfg = config_map.get(r["symbol"], {})
        name = cfg.get("name", r["symbol"])
        market = cfg.get("market", "US")

        display = f"{name} ({r['symbol']})" if name != r["symbol"] else r["symbol"]
        emoji = _drawdown_emoji(r["drawdown"])

        current_str = _format_price(r["current_price"], market)
        peak_str = _format_price(r["peak_price"], market)
        daily_str = _daily_change_str(r["daily_change"])

        if r["is_new_high"]:
            value = f"종가: {current_str} | 고점: {peak_str}\n🎉 신고가 갱신! | 전일비: {daily_str}"
        else:
            value = f"종가: {current_str} | 고점: {peak_str}\n{emoji} 하락률: {r['drawdown']}% | 전일비: {daily_str}"

        fields.append({"name": display, "value": value, "inline": False})

    if errors:
        error_lines = []
        for e in errors:
            cfg = config_map.get(e["symbol"], {})
            name = cfg.get("name", e["symbol"])
            error_lines.append(f"{name} ({e['symbol']}): {e['error']}")
        fields.append({
            "name": "⚠️ 조회 실패",
            "value": "\n".join(error_lines),
            "inline": False,
        })

    worst = sorted_results[0]["drawdown"] if sorted_results else 0

    embed = {
        "title": f"📉 {title}",
        "description": f"📅 {now.strftime('%Y-%m-%d')} KST",
        "color": _embed_color(worst),
        "fields": fields,
        "footer": {"text": "Peak-Drop Bot"},
        "timestamp": now.isoformat(),
    }

    return embed
