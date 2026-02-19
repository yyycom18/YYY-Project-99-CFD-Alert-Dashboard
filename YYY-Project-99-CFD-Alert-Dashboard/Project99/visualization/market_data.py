import pandas as pd
import yfinance as yf


def fetch_15m_data(symbol: str, lookback_days: int = 10) -> pd.DataFrame:
    """
    Fetch 15-minute OHLC data using yfinance.
    Returns dataframe with columns:
    open, high, low, close
    """

    try:
        df = yf.download(
            symbol,
            interval="15m",
            period=f"{lookback_days}d",
            auto_adjust=False,
            progress=False,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df = df.copy()
            df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close"]].copy()
        df.columns = ["open", "high", "low", "close"]

        df.dropna(inplace=True)
        df.sort_index(inplace=True)

        return df

    except Exception:
        return pd.DataFrame()
