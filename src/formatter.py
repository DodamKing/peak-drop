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


def _drawdown_bar(drawdown: float, bar_length: int = 10) -> str:
    """하락률을 시각적 바로 표현한다. 0%=빈 바, -50% 이상=풀 바."""
    filled = min(bar_length, int(abs(drawdown) / 50 * bar_length))
    return "█" * filled + "░" * (bar_length - filled)


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


def _build_embed(
    results: list[dict],
    errors: list[dict],
    config_map: dict,
    title: str,
    market: str,
    now: datetime,
) -> dict:
    """단일 마켓용 Embed를 생성한다."""
    sorted_results = sorted(results, key=lambda r: r["drawdown"])

    fields = []
    for r in sorted_results:
        cfg = config_map.get(r["symbol"], {})
        name = cfg.get("name", r["symbol"])

        display = f"{name} ({r['symbol']})" if name != r["symbol"] else r["symbol"]
        emoji = _drawdown_emoji(r["drawdown"])

        current_str = _format_price(r["current_price"], market)
        peak_str = _format_price(r["peak_price"], market)
        daily_str = _daily_change_str(r["daily_change"])

        if r["is_new_high"]:
            value = (
                f"🎉 **신고가 갱신!**\n"
                f"전일비 **{daily_str}** | {current_str}"
            )
        else:
            value = (
                f"{emoji} **{r['drawdown']}%**\n"
                f"전일비 **{daily_str}** | {current_str} / 고점 {peak_str}"
            )

        fields.append({"name": display, "value": value + "\n\u200b", "inline": False})

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
    market_flag = "🇰🇷" if market == "KR" else "🇺🇸"

    return {
        "title": f"{market_flag} {title}",
        "description": f"📅 {now.strftime('%Y-%m-%d')} KST",
        "color": _embed_color(worst),
        "fields": fields,
        "footer": {"text": "Peak-Drop Bot"},
        "timestamp": now.isoformat(),
    }


def format_embeds(
    results: list[dict],
    errors: list[dict],
    symbols_config: list[dict],
    title: str,
) -> list[dict]:
    """마켓별로 분리된 Embed 리스트를 생성한다."""
    now = datetime.now(KST)
    config_map = {s["symbol"]: s for s in symbols_config}

    kr_results = [r for r in results if config_map.get(r["symbol"], {}).get("market") == "KR"]
    us_results = [r for r in results if config_map.get(r["symbol"], {}).get("market") != "KR"]
    kr_errors = [e for e in errors if config_map.get(e["symbol"], {}).get("market") == "KR"]
    us_errors = [e for e in errors if config_map.get(e["symbol"], {}).get("market") != "KR"]

    embeds = []
    if kr_results or kr_errors:
        embeds.append(_build_embed(kr_results, kr_errors, config_map, title, "KR", now))
    if us_results or us_errors:
        embeds.append(_build_embed(us_results, us_errors, config_map, title, "US", now))

    return embeds
