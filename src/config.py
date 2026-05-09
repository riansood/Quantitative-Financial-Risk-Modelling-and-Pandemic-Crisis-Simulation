#%%
from datetime import datetime

# Dates
DEFAULT_START = "2019-01-01"
DEFAULT_END   = "2023-01-01"

# COVID windows (India-centric)
PRE_START   = "2019-01-01"
PRE_END_IND     = "2020-02-19"
EVENT_START_IND = "2020-02-20"
EVENT_END_IND   = "2021-07-31"
REC_START_IND   = "2021-08-01"
REC_END = "2023-01-01"
# Benchmarks
INDIA_MARKET = "^NSEI"   # NIFTY 50
US_MARKET    = "^GSPC"   # S&P 500

# Rolling window (trading days)
ROLL_WIN = 60

# Preset India sectors (your list)
TICKERS_BY_SECTOR_IND = {
    "Tech_Communication": ["TCS.NS", "INFY.NS", "BHARTIARTL.NS"],
    "Healthcare_Pharma": ["DRREDDY.NS", "SUNPHARMA.NS", "CIPLA.NS"],
    "Financials": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
    "Consumer_Goods_Services": ["HINDUNILVR.NS", "TITAN.NS", "MARUTI.NS"],
    "Energy_Materials": ["RELIANCE.NS", "ONGC.NS", "TATASTEEL.NS"],
    "Industrials_Infrastructure": ["LT.NS", "BHEL.NS", "ASHOKLEY.NS"],
    "Utilities_Essential": ["NTPC.NS", "POWERGRID.NS", "TATAPOWER.NS"],
}

#%%
from datetime import datetime


# COVID windows (USA-centric)
PRE_END_USA     = "2020-02-20"
EVENT_START_USA = "2020-02-21"
EVENT_END_USA   = "2020-12-31"
REC_START_USA   = "2021-01-01"

TICKERS_BY_SECTOR_USA = {
    "Information Technology": ["AAPL", "MSFT", "NVDA"],
    "Health Care": ["JNJ", "PFE", "UNH"],
    "Financials": ["JPM", "BAC", "GS"],
    "Consumer Discretionary": ["AMZN", "TSLA", "HD"],
    "Consumer Staples": ["WMT", "PG", "KO"],
    "Energy": ["XOM", "CVX", "SLB"],
    "Industrials": ["CAT", "HON", "UPS"],
    "Utilities": ["NEE", "DUK", "SO"],
    "Communication Services": ["GOOG", "META", "NFLX"],
    "Materials": ["LIN", "SHW", "NEM"],
}
#Event dates for our reference we used for the report and basic analysis
# EVENT_DATES = {
#     # === PRE-COVID BUILDUP (Late 2019) ===
#     "2019-12-12": "US-China Phase One trade deal optimism",
#     "2020-01-21": "First confirmed COVID-19 case in the U.S.",
#     "2020-01-31": "U.S. declares public health emergency; WHO declares global emergency",
#
#     # === INITIAL COVID MARKET PANIC (Feb–Mar 2020) ===
#     "2020-02-19": "S&P 500 all-time high before COVID crash",
#     "2020-02-24": "COVID selloff begins",
#     "2020-03-09": "Black Monday I – pandemic panic",
#     "2020-03-12": "Black Thursday – global market crash",
#     "2020-03-15": "Fed cuts rates to near-zero (emergency move)",
#     "2020-03-16": "Largest one-day drop since 1987",
#     "2020-03-18": "Treasury & liquidity stress; corporate credit panic",
#     "2020-03-23": "Fed announces unlimited QE – market bottom",
#
#     # === STIMULUS + EARLY RECOVERY (Apr–Jun 2020) ===
#     "2020-04-02": "Weekly jobless claims hit record highs",
#     "2020-04-27": "Oil futures collapse – WTI negative price aftermath",
#     "2020-05-18": "Moderna vaccine trial news lifts markets",
#     "2020-06-08": "Nasdaq hits record high amid reopening optimism",
#     "2020-06-11": "Renewed selloff on second COVID wave fears",
#
#     # === POLICY + VACCINE PHASE (Jul–Dec 2020) ===
#     "2020-07-27": "U.S. fiscal stimulus talks stall – volatility spikes",
#     "2020-08-27": "Fed adopts average inflation targeting (AIT)",
#     "2020-10-13": "Tech correction amid U.S. election uncertainty",
#     "2020-11-09": "Pfizer vaccine efficacy announcement – massive rally",
#     "2020-12-21": "Congress passes $900B stimulus package",
#
#     # === POST-COVID VOLATILITY (2021) ===
#     "2021-01-06": "U.S. Capitol riot – political instability shock",
#     "2021-01-27": "GameStop / retail mania peak",
#     "2021-03-11": "Biden signs $1.9T American Rescue Plan",
#     "2021-05-12": "CPI shock – inflation fears emerge",
#     "2021-06-16": "Fed signals potential tapering – yield surge",
#     "2021-07-19": "Delta variant selloff",
#     "2021-09-20": "Evergrande crisis triggers global risk-off",
#     "2021-11-26": "Omicron variant selloff",
# }
