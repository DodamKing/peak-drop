def analyze(stock_data: dict, peak_type: str, peak_price: float | None = None) -> dict:
    """고점 대비 하락률을 계산한다.

    Args:
        stock_data: fetcher에서 반환된 데이터
        peak_type: "manual" 또는 "auto_52w"
        peak_price: manual일 때 기준 고점

    Returns:
        {
            "symbol": str,
            "current_price": float,
            "peak_price": float,
            "drawdown": float,  # 퍼센트 (음수)
            "is_new_high": bool,
        }
    """
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
    }
