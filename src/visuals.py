from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from config import *

OUT = Path("output")
OUT.mkdir(exist_ok=True, parents=True)

def _region_suffix(region: str) -> str:
    """Return '_IND' or '_USA' suffix based on region."""
    return "_IND" if region.lower() == "india" else "_USA"

def plot_series(df, cols, title, fname, region="India"):
    """Plot rolling beta & sigma with COVID event lines and region-based filename."""
    fig, ax = plt.subplots(figsize=(8, 4))
    for c in cols:
        ax.plot(df.index, df[c], label=c)
    if region == "India":
        ax.axvline(pd.Timestamp(EVENT_START_IND), color="red", linestyle="--", linewidth=1.5, label="Event Start")
        ax.axvline(pd.Timestamp(EVENT_END_IND), color="red", linestyle="--", linewidth=1.5, label="Event End")
    else:
        ax.axvline(pd.Timestamp(EVENT_START_USA), color="red", linestyle="--", linewidth=1.5, label="Event Start")
        ax.axvline(pd.Timestamp(EVENT_END_USA), color="red", linestyle="--", linewidth=1.5, label="Event End")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # region-based file naming
    fname = fname.replace(".png", f"{_region_suffix(region)}.png")
    p = OUT / fname
    fig.tight_layout()
    fig.savefig(p, dpi=160)
    plt.close(fig)
    return p

def plot_series_sim(df, cols, title, fname, region="India"):
    """Plot simulated series, save with region suffix."""
    fig, ax = plt.subplots(figsize=(8, 4))
    for c in cols:
        ax.plot(df.index, df[c], label=c)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()

    fname = fname.replace(".png", f"{_region_suffix(region)}.png")
    p = OUT / fname
    fig.tight_layout()
    fig.savefig(p, dpi=160)
    plt.close(fig)
    return p

def plot_ar_car(df, title, fname, region="India"):
    """Plot CAR (Cumulative Abnormal Return) with COVID event lines per region."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df.index, df["CAR"], color="steelblue", linewidth=2, label="CAR (cumulative)")
    if region == "India":
        ax.axvline(pd.Timestamp(EVENT_START_IND), color="red", linestyle="--", linewidth=1.5, label="Event Start")
        ax.axvline(pd.Timestamp(EVENT_END_IND), color="red", linestyle="--", linewidth=1.5, label="Event End")
    else:
        ax.axvline(pd.Timestamp(EVENT_START_USA), color="red", linestyle="--", linewidth=1.5, label="Event Start")
        ax.axvline(pd.Timestamp(EVENT_END_USA), color="red", linestyle="--", linewidth=1.5, label="Event End")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Abnormal Return")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")

    fname = fname.replace(".png", f"{_region_suffix(region)}.png")
    p = OUT / fname
    fig.tight_layout()
    fig.savefig(p, dpi=160)
    plt.close(fig)
    return p
