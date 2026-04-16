import math
import logging
from datetime import datetime, timedelta

import FinanceDataReader as fdr

logger = logging.getLogger(__name__)


def _clean_df(df, end: datetime):
    """오늘 날짜의 불완전 데이터 제거 + 중복 제거."""
    if df is None or df.empty:
        return df
    today_str = end.strftime("%Y-%m-%d")
    df = df[df.index.strftime("%Y-%m-%d") < today_str]
    df = df[~df.index.duplicated(keep="last")]
    return df


def _has_nan_close(df) -> bool:
    """마지막 행의 Close가 NaN인지 확인."""
    if df is None or df.empty:
        return True
    last_close = df["Close"].iloc[-1]
    return math.isnan(last_close) if isinstance(last_close, float) else False


def _fetch_fdr(symbol: str, start_str: str, end_str: str, end: datetime):
    """FDR 조회. (raw, cleaned) 반환, 실패 시 (None, None)."""
    try:
        raw = fdr.DataReader(symbol, start_str, end_str)
        cleaned = _clean_df(raw, end)
        if not _has_nan_close(cleaned):
            return raw, cleaned
    except Exception as e:
        logger.warning(f"{symbol}: FDR 조회 실패 — {e}")
    return None, None


def _fetch_yfinance(symbol: str, start_str: str, end_str: str, end: datetime):
    """yfinance fallback 조회. (raw, cleaned) 반환, 실패 시 (None, None)."""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        raw = ticker.history(start=start_str, end=end_str, auto_adjust=False)
        cleaned = _clean_df(raw, end)
        if not _has_nan_close(cleaned):
            return raw, cleaned
    except Exception as e:
        logger.warning(f"{symbol}: yfinance 조회 실패 — {e}")
    return None, None


def _extract_today_open(raw, end: datetime) -> float | None:
    """raw DF에서 당일 시가를 추출. 없거나 NaN이면 None."""
    if raw is None or raw.empty:
        return None
    today_str = end.strftime("%Y-%m-%d")
    today_rows = raw[raw.index.strftime("%Y-%m-%d") == today_str]
    if today_rows.empty:
        return None
    open_price = today_rows["Open"].iloc[-1]
    if isinstance(open_price, float) and math.isnan(open_price):
        return None
    return round(float(open_price), 2)


def _extract_prices(symbol: str, df) -> dict:
    """DataFrame에서 가격 정보를 추출한다."""
    current_price = round(float(df["Close"].iloc[-1]), 2)
    high_52w = round(float(df["Close"].max()), 2)

    if len(df) >= 2:
        prev_price = round(float(df["Close"].iloc[-2]), 2)
        daily_change = round((current_price - prev_price) / prev_price * 100, 2)
    else:
        prev_price = current_price
        daily_change = 0.0

    return {
        "symbol": symbol,
        "current_price": current_price,
        "prev_price": prev_price,
        "daily_change": daily_change,
        "high_52w": high_52w,
        "error": None,
    }


def fetch_stock_data(symbol: str, market: str) -> dict:
    """종목의 전일 종가, 52주 데이터, 전일 대비 변동률을 조회한다."""
    try:
        end = datetime.now()
        start = end - timedelta(days=365)
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")

        raw, df = _fetch_fdr(symbol, start_str, end_str, end)

        if df is None and market == "US":
            logger.warning(f"{symbol}: FDR 실패, yfinance fallback 시도")
            raw, df = _fetch_yfinance(symbol, start_str, end_str, end)

        if df is None:
            return {"symbol": symbol, "error": "데이터를 가져올 수 없습니다 (NaN 또는 조회 실패)"}

        result = _extract_prices(symbol, df)

        if market == "KR":
            today_open = _extract_today_open(raw, end)
            if today_open is not None:
                current = result["current_price"]
                result["daily_change"] = round((today_open - current) / current * 100, 2)

        return result
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}
