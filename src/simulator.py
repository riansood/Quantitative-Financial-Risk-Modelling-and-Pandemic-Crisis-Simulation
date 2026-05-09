# simulator.py
import pandas as pd
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

# ---- CONFIG ----
DATA_DIR = Path("output")
OUT = Path("output_models")
OUT.mkdir(exist_ok=True)

# COVID windows for sectors
COVID_WINDOWS_IND = {
    "Pre": ("2019-01-01", "2020-02-19"),
    "Event": ("2020-02-20", "2021-07-31"),
    "Recovery": ("2021-08-01", "2023-01-01")
}
COVID_WINDOWS_USA = {
    "Pre": ("2019-01-01", "2020-02-20"),
    "Event": ("2020-02-21", "2020-12-31"),
    "Recovery": ("2021-01-01", "2023-01-01")
}


# ---- HELPERS ----
def get_covid_windows(sector: str):
    return COVID_WINDOWS_IND if "_IND" in sector else COVID_WINDOWS_USA


def get_sector_list():
    basket_files = list(DATA_DIR.glob("*_basket.csv"))
    return [f.stem.replace("_basket", "") for f in basket_files]


# ---- LOAD SINGLE SECTOR ----
def load_sector(sector_name: str):
    basket_file = DATA_DIR / f"{sector_name}_basket.csv"
    beta_file = DATA_DIR / f"{sector_name}_rolling_beta.csv"
    sigma_file = DATA_DIR / f"{sector_name}_rolling_sigma.csv"

    if not basket_file.exists() or not beta_file.exists() or not sigma_file.exists():
        print(f"Missing files for sector {sector_name}")
        return None

    df_basket = pd.read_csv(basket_file, parse_dates=["Date"])
    df_beta = pd.read_csv(beta_file, parse_dates=["Date"])
    df_sigma = pd.read_csv(sigma_file, parse_dates=["Date"])

    # lowercase columns
    df_basket.columns = [c.lower() for c in df_basket.columns]
    df_beta.columns = [c.lower() for c in df_beta.columns]
    df_sigma.columns = [c.lower() for c in df_sigma.columns]

    log_cols = [c for c in df_basket.columns if "log_return" in c]
    if not log_cols:
        print(f"No log_return column in {sector_name}")
        return None
    log_col = log_cols[0]

    df_basket["adj_close"] = (1 + df_basket[log_col].fillna(0)).cumprod()
    df_basket["log_return"] = df_basket[log_col]

    df = df_basket.merge(df_beta, on="date", how="left").merge(df_sigma, on="date", how="left")
    df["sector"] = sector_name

    # assign regime
    covid_windows = get_covid_windows(sector_name)
    df["regime"] = "Pre"
    for regime, (start, end) in covid_windows.items():
        mask = (df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))
        df.loc[mask, "regime"] = regime

    return df


# ---- FEATURE ENGINEERING ----
def add_features(df: pd.DataFrame):
    df = df.copy()
    df["ma_7"] = df["adj_close"].rolling(7).mean()
    df["ma_14"] = df["adj_close"].rolling(14).mean()
    df["vol_7"] = df["log_return"].rolling(7).std()
    df["vol_14"] = df["log_return"].rolling(14).std()
    df["mkt_ret"] = df.groupby("date")["log_return"].transform("mean")
    df["capm_exp"] = df["beta_60"] * df["mkt_ret"]

    for lag in range(1, 4):
        df[f'lag_{lag}'] = df['adj_close'].shift(lag)
        df[f'ret_{lag}'] = df['log_return'].shift(lag)

    df = pd.get_dummies(df, columns=['regime'], drop_first=True)
    df.fillna(0, inplace=True)
    return df


# ---- TRAIN SINGLE SECTOR MODEL (CAPM) WITH STRATIFIED SPLIT ----
def train_sector_model_capm_stratified(df: pd.DataFrame):
    df = df.copy()

    features = ["beta_60", "sigma_60", "vol_7", "vol_14"] + \
               [f'lag_{i}' for i in range(1, 4)] + [f'ret_{i}' for i in range(1, 3)] + \
               [c for c in df.columns if c.startswith("regime_")]

    X = df[features]
    y = df["capm_exp"]

    if len(X) < 20:
        print(f"Not enough data for sector {df['sector'].iloc[0]}")
        return None, None, None

    # Stratified train/test split based on regime
    regime_cols = [c for c in df.columns if c.startswith("regime_")]
    if regime_cols:
        regime_labels = df[regime_cols].idxmax(axis=1)
    else:
        regime_labels = pd.Series(["Pre"] * len(df))
    #Split training and test set on random shuffle because we have the data from 2019-2023 and make
    # predictions for a similar such period in the future.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=regime_labels, random_state=42, shuffle=True
    )

    scaler = StandardScaler().fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestRegressor(n_estimators=300, max_depth=10, random_state=42)
    model.fit(X_train_scaled, y_train)

    preds = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, preds)

    sector_name = df['sector'].iloc[0]
    joblib.dump(model, OUT / f"rf_model_{sector_name}_capm.joblib")
    joblib.dump(scaler, OUT / f"scaler_{sector_name}_capm.joblib")

    summary = {
        "sector": sector_name,
        "MAE": mae,
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    }

    print(f"[{sector_name}] CAPM Model MAE={mae:.6f}")
    return model, scaler, summary


# ---- TRAIN ALL SECTORS (CAPM) ----
def train_all_sectors_capm():
    models = {}
    scalers = {}
    summary_rows = []

    sectors = get_sector_list()
    for sector in sectors:
        df = load_sector(sector)
        if df is None or df.empty:
            continue
        df = add_features(df)
        model, scaler, summary = train_sector_model_capm_stratified(df)
        if model:
            models[sector] = model
            scalers[sector] = scaler
            summary_rows.append(summary)

    return models, scalers, pd.DataFrame(summary_rows)


# ---- PREDICT PRICE PATH FROM CAPM ----
def predict_price_path(sector, start_price=100):
    model_path = OUT / f"rf_model_{sector}_capm.joblib"
    scaler_path = OUT / f"scaler_{sector}_capm.joblib"

    if not model_path.exists() or not scaler_path.exists():
        print(f"Model/scaler for {sector} missing. Training now...")
        train_all_sectors_capm()

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    df = load_sector(sector)
    df = add_features(df)

    features = ["beta_60", "sigma_60", "vol_7", "vol_14"] + \
               [f'lag_{i}' for i in range(1, 4)] + [f'ret_{i}' for i in range(1, 3)] + \
               [c for c in df.columns if c.startswith("regime_")]
    X_scaled = scaler.transform(df[features])
    df["pred_capm"] = model.predict(X_scaled)

    price_path = [start_price]
    for ret in df["pred_capm"].values:
        price_path.append(price_path[-1] * (1 + ret))
    price_path = price_path[1:]

    # Shift dates +10 years (To show prediction for future on the front end)
    shifted_dates = pd.to_datetime(df["date"]) + pd.DateOffset(years=10)

    # --- Plot with shifted dates ---
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(shifted_dates, price_path, color='orange', lw=2, label='Predicted Price')
    ax.set_xlabel("Date ")
    ax.set_ylabel("Price")
    ax.set_title(f"{sector} — Predicted Price Using CAPM Expected Return, assuming a "
                 f"pandemic pre lockdown from 2029 (hopefully does not happen!)")
    ax.grid(True, alpha=0.3)
    ax.legend()

    return shifted_dates, price_path, fig


# ---- MAIN ----

# ---- MAIN ----
if __name__ == "__main__":
    models, scalers, summary_df = train_all_sectors_capm()
    print("\n=== MODEL SUMMARY ===")
    print(summary_df)

    # Example: plot for first sector
    sectors = get_sector_list()
    if sectors:
        sector = sectors[0]
        dates, prices, fig = predict_price_path(sector, start_price=100)
        plt.show()
