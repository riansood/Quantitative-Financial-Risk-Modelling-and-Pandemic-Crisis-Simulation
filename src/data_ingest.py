from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

OUT = Path("output"); OUT.mkdir(exist_ok=True, parents=True)

# --- Your feature engineering (kept, trimmed to essentials) ---
def engineer_features(df: pd.DataFrame, first_case_date, lockdown_date):
    df = df.copy().sort_index()
    df.index = pd.to_datetime(df.index)

    df["close"] = df["Adj Close"].fillna(df.get("Close"))
    df["daily_return"] = df["close"].pct_change()
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))

    window_short = 7
    window_mid = 14
    df[f"ma_{window_short}"] = df["close"].rolling(window_short).mean()
    df[f"ma_{window_mid}"] = df["close"].rolling(window_mid).mean()
    df[f"vol_{window_short}"] = df["log_return"].rolling(window_short).std()
    df[f"vol_{window_mid}"] = df["log_return"].rolling(window_mid).std()

    df["volume_change"] = df["Volume"].pct_change()
    df["volume_ma_7"] = df["Volume"].rolling(window_short).mean()

    df["ret_7d"] = df["close"].pct_change(periods=7)
    df["ret_14d"] = df["close"].pct_change(periods=14)

    df["days_since_first_case"] = (df.index - pd.to_datetime(first_case_date)).days.clip(lower=0)
    df["days_since_lockdown"]   = (df.index - pd.to_datetime(lockdown_date)).days.clip(lower=0)
    df["is_first_case_day"] = (df.index == pd.to_datetime(first_case_date)).astype(int)
    df["is_lockdown_day"]   = (df.index == pd.to_datetime(lockdown_date)).astype(int)
    return df

# --- Core utils for the tool ---
def download_prices(tickers, start, end):
    """
    Returns (Adj Close, Volume) DataFrames with columns named by tickers.
    Works for a single ticker (str) or a list of tickers.
    """
    df = yf.download(tickers, start=start, end=end, progress=False, auto_adjust=False)
    if df.empty:
        raise ValueError(f"No data returned for {tickers} — check ticker/date/network.")

    # Grab adj close & volume (may be Series or DataFrame depending on yfinance)
    adj = df["Adj Close"]
    vol = df["Volume"]

    # Normalize to 2D DataFrames
    if isinstance(adj, pd.Series):
        adj = adj.to_frame(name=tickers if isinstance(tickers, str) else adj.name)
    if isinstance(vol, pd.Series):
        vol = vol.to_frame(name=tickers if isinstance(tickers, str) else vol.name)

    # If a single ticker came back as a 1-col DataFrame, ensure the column is named with the ticker
    if isinstance(tickers, str):
        if adj.shape[1] == 1:
            adj.columns = [tickers]
        if vol.shape[1] == 1:
            vol.columns = [tickers]

    # Clean
    adj = adj.dropna(how="all")
    vol = vol.reindex(adj.index).fillna(0)

    return adj, vol


def compute_log_returns(close_df: pd.DataFrame):
    return np.log(close_df / close_df.shift(1))

def equal_weight_basket(returns_df: pd.DataFrame, name="basket"):
    """
    Equal-weighted log-return basket + index (cumprod of (1+lr)).
    """
    lr = returns_df.mean(axis=1).rename(f"{name}_log_return")
    idx = (1 + lr.fillna(0)).cumprod().rename(f"{name}_close_index")
    return pd.concat([lr, idx], axis=1)

def save_csv(df: pd.DataFrame, fname: str):
    p = OUT / fname
    df.to_csv(p, index=True)
    return p
