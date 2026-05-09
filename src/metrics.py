import numpy as np
import pandas as pd
from config import *

def rolling_beta(asset_lr: pd.Series, mkt_lr: pd.Series, window=ROLL_WIN):
    df = pd.concat([asset_lr.rename("a"), mkt_lr.rename("m")], axis=1).dropna()
    cov = df["a"].rolling(window).cov(df["m"])
    var = df["m"].rolling(window).var()
    beta = (cov / var).rename(f"beta_{window}")
    return beta.reindex(asset_lr.index)

def rolling_vol(asset_lr: pd.Series, window=ROLL_WIN):
    return asset_lr.rolling(window).std().rename(f"sigma_{window}")

def period_masks(idx, region="India"):
    idx = pd.to_datetime(idx)
    if region == "India":
        pre = (idx >= pd.Timestamp(PRE_START)) & (idx <= pd.Timestamp(PRE_END_IND))
        shock = (idx >= pd.Timestamp(EVENT_START_IND)) & (idx <= pd.Timestamp(EVENT_END_IND))
        rec = (idx >= pd.Timestamp(REC_START_IND))
    else:
        pre = (idx >= pd.Timestamp(PRE_START)) & (idx <= pd.Timestamp(PRE_END_USA))
        shock = (idx >= pd.Timestamp(EVENT_START_USA)) & (idx <= pd.Timestamp(EVENT_END_USA))
        rec = (idx >= pd.Timestamp(REC_START_USA))
    return pre, shock, rec

def summarize_periods(beta_s: pd.Series, sigma_s: pd.Series, region="India"):
    pre, shock, rec = period_masks(beta_s.index, region)
    out = {
        "beta_pre": beta_s[pre].mean(),
        "beta_shock": beta_s[shock].mean(),
        "beta_rec": beta_s[rec].mean(),
        "sigma_pre": sigma_s[pre].mean(),
        "sigma_shock": sigma_s[shock].mean(),
        "sigma_rec": sigma_s[rec].mean(),
    }
    out["kappa"] = (out["sigma_shock"] / out["sigma_pre"]) if out["sigma_pre"] else np.nan
    return pd.Series(out)

def abnormal_and_car(asset_lr: pd.Series, mkt_lr: pd.Series, region="India"):
    df = pd.concat([asset_lr.rename("a"), mkt_lr.rename("m")], axis=1).dropna()
    df["AR"] = df["a"] - df["m"]
    if region == "India":
        sel = (df.index >= pd.Timestamp(PRE_START)) & (df.index <= pd.Timestamp(REC_END))
    else:
        sel = (df.index >= pd.Timestamp(PRE_START)) & (df.index <= pd.Timestamp(REC_END))
    out = df.loc[sel, ["AR"]].copy()
    out["CAR"] = out["AR"].cumsum()
    return out
