import math
import time
import logging
from datetime import datetime, timedelta

import FinanceDataReader as fdr

logger = logging.getLogger(__name__)


def _clean_df(df, end: datetime):
    """오늘 날짜의 불완전 데이터 제거 + 중복/NaN 제거."""
    if df is None or df.empty:
        return df
    today_str = end.strftime("%Y-%m-%d")
    df = df[df.index.strftime("%Y-%m-%d") < today_str]
    df = df[~df.index.duplicated(keep="last")]
    df = df.dropna(subset=["Close"])
    return df


def _is_valid(df) -> bool:
    """DataFrame이 유효하고 마지막 Close가 NaN이 아닌지 확인."""
    if df is None or df.empty:
        return False
    last_close = df["Close"].iloc[-1]
    return not (math.isnan(last_close) if isinstance(last_close, float) else False)


def _fetch_fdr_with_retry(symbol: str, start_str: str, end_str: str, end: datetime,
                          max_retries: int = 2, delay: int = 5):
    """FDR 조회, NaN이면 재시도. 실패 시 None 반환."""
    for attempt in range(1 + max_retries):
        if attempt > 0:
            logger.warning(f"{symbol}: FDR 재시도 {attempt}/{max_retries} ({delay}초 대기)")
            time.sleep(delay)

        try:
            df = fdr.DataReader(symbol, start_str, end_str)
            df = _clean_df(df, end)
            if _is_valid(df):
                return df
        except Exception as e:
            logger.warning(f"{symbol}: FDR 조회 실패 — {e}")

    return None


def _fetch_yfinance(symbol: str, start_str: str, end_str: str, end: datetime):
    """yfinance fallback 조회. 실패 시 None 반환."""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_str, end=end_str, auto_adjust=False)
        df = _clean_df(df, end)
        if _is_valid(df):
            return df
    except Exception as e:
        logger.warning(f"{symbol}: yfinance 조회 실패 — {e}")
    return None


def _extract_prices(symbol: str, df) -> dict:
    """DataFrame에서 가격 정보를 추출한다. NaN이면 에러 반환."""
    current_price = round(float(df["Close"].iloc[-1]), 2)

    if math.isnan(current_price):
        return {"symbol": symbol, "error": "가격 데이터가 NaN입니다"}

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

        df = _fetch_fdr_with_retry(symbol, start_str, end_str, end)

        if df is None and market == "US":
            logger.warning(f"{symbol}: FDR 실패, yfinance fallback 시도")
            df = _fetch_yfinance(symbol, start_str, end_str, end)

        if df is None or df.empty:
            return {"symbol": symbol, "error": "데이터 조회 결과 없음"}

        return _extract_prices(symbol, df)
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}
