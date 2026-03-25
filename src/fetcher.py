from datetime import datetime, timedelta

import FinanceDataReader as fdr


def fetch_stock_data(symbol: str, market: str) -> dict:
    """종목의 전일 종가 및 52주 데이터를 조회한다.

    Returns:
        {
            "symbol": str,
            "current_price": float,
            "high_52w": float,
            "error": None
        }
        실패 시:
        {
            "symbol": str,
            "error": str
        }
    """
    try:
        end = datetime.now()
        start = end - timedelta(days=365)

        df = fdr.DataReader(symbol, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

        if df is None or df.empty:
            return {"symbol": symbol, "error": "데이터 조회 결과 없음"}

        current_price = float(df["Close"].iloc[-1])
        high_52w = float(df["Close"].max())

        return {
            "symbol": symbol,
            "current_price": current_price,
            "high_52w": high_52w,
            "error": None,
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}
