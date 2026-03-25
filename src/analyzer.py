def analyze(stock_data: dict, peak_type: str, peak_price: float | None = None) -> dict:
    """고점 대비 하락률을 계산한다."""
    current = stock_data["current_price"]

    if peak_type == "manual":
        peak = peak_price
    else:
        peak = stock_data["high_52w"]

    drawdown = (current - peak) / peak * 100
    is_new_high = current >= peak

    return {
        "symbol": stock_data["symbol"],
        "current_price": current,
        "peak_price": peak,
        "drawdown": round(drawdown, 2),
        "is_new_high": is_new_high,
        "daily_change": stock_data.get("daily_change", 0.0),
    }
