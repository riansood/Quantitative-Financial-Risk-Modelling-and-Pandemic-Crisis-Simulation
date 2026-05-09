# app.py
import streamlit as st
import pandas as pd

from simulator import predict_price_path
from config import *
from data_ingest import download_prices, compute_log_returns, equal_weight_basket, save_csv
from metrics import rolling_beta, rolling_vol, summarize_periods, abnormal_and_car
from visuals import plot_series, plot_ar_car


st.set_page_config(page_title="Dynamic Risk Estimation Tool", layout="wide")
st.title("Dynamic Risk Estimation Tool — COVID-era Risk & Simulation")

# --- Tabs ---
tab1, tab2 = st.tabs([" Sector Analysis", " Portfolio Prediction"])

# -------------------------------------------------------------------
# TAB 1: Analysis
# -------------------------------------------------------------------
with tab1:
    st.header("Controls — Analysis")

    region = st.radio("Market Region", ["India", "USA"])

    if region == "India":
        sector_dict = TICKERS_BY_SECTOR_IND
        market = INDIA_MARKET
        event_start = pd.to_datetime(EVENT_START_IND)
        rec_start = pd.to_datetime(REC_START_IND)
    else:
        sector_dict = TICKERS_BY_SECTOR_USA
        market = US_MARKET
        event_start = pd.to_datetime(EVENT_START_USA)
        rec_start = pd.to_datetime(REC_START_USA)

    # Display COVID timeline information clearly
    st.markdown(f"""
    **COVID Periods — {region}**
    - **Event Start:** {event_start.date()}
    - **Recovery Start:** {rec_start.date()}
    - **Note:**  
      - Start date cannot be *after* Event Start ({event_start.date()})  
      - End date cannot be *before* Recovery Start ({rec_start.date()})
    """)

    # Date pickers with dynamic  enforcement
    start = st.date_input(
        "Start Date",
        pd.to_datetime(DEFAULT_START),
        max_value=event_start
    )
    end = st.date_input(
        "End Date",
        pd.to_datetime(DEFAULT_END),
        min_value=rec_start
    )




    sector = st.selectbox("Sector", list(sector_dict.keys()))
    tickers = sector_dict[sector]


    run_analysis = st.button("Run analysis")

    if run_analysis:
        st.subheader(f"Analysis for {sector} ({region})")
        adj, _ = download_prices(tickers, str(start), str(end))
        m_close, _ = download_prices(market, str(start), str(end))

        missing_tickers = [t for t in tickers if t not in adj.columns or adj[t].isna().all()]
        if missing_tickers:
            st.warning(f"Missing data for {missing_tickers}. Please rerun analysis on Tab 1.")

        asset_lr = compute_log_returns(adj)
        mkt_lr = compute_log_returns(m_close)
        basket = equal_weight_basket(asset_lr, name=sector)
        aset_lr = basket[f"{sector}_log_return"]
        m_lr = mkt_lr[market]

        beta = rolling_beta(aset_lr, m_lr)
        sigma = rolling_vol(aset_lr)

        summary = summarize_periods(beta, sigma).to_frame(name=sector).T
        st.subheader("Period Summary (β, σ, κ)")
        st.dataframe(summary.style.format("{:.3f}"))

        arcar = abnormal_and_car(aset_lr, m_lr)

        # region suffix
        suffix = "_IND" if region == "India" else "_USA"
        save_csv(basket, f"{sector}{suffix}_basket.csv")
        save_csv(beta.to_frame(), f"{sector}{suffix}_rolling_beta.csv")
        save_csv(sigma.to_frame(), f"{sector}{suffix}_rolling_sigma.csv")
        save_csv(arcar, f"{sector}{suffix}_event_study_arcar.csv")
        save_csv(summary, f"{sector}{suffix}_period_summary.csv")

        p_beta_sigma = plot_series(pd.concat([beta, sigma], axis=1),
                                   [beta.name, sigma.name],
                                   f"{sector} — Rolling Beta & Volatility ({region})",
                                   f"fig_{sector}{suffix}_beta_sigma.png",
                                   region=region)
        p_arcar = plot_ar_car(arcar,
                              f"{sector} — AR & CAR (Shock Window) ({region})",
                              f"fig_{sector}{suffix}_AR_CAR.png",
                              region=region)

        c1, c2 = st.columns(2)
        with c1:
            st.image(str(p_beta_sigma))
            st.image(str(p_arcar))
        with c2:
            st.caption("All CSVs/PNGs saved in /output for poster/report.")

# -------------------------------------------------------------------
# TAB 2: Portfolio Prediction
# -------------------------------------------------------------------
with tab2:
    st.header("Portfolio Value Simulation (COVID Intervals)")
    st.info(
        "**Dynamic Model Behavior:** Each time you change the analysis period or rerun the analysis, "
        "the prediction model recalibrates dates based on the most recent CAPM and RandomForest parameters. "
        "This ensures that forecasts reflect the newest data and market conditions."
    )
    region = st.radio("Region", ["India", "USA"], horizontal=True)
    if region == "India":
        available_sectors = [
            "Consumer_Goods_Services_IND", "Energy_Materials_IND", "Financials_IND",
            "Healthcare_Pharma_IND", "Industrials_Infrastructure_IND",
            "Tech_Communication_IND", "Utilities_Essential_IND"
        ]
    else:
        available_sectors = [
            "Communication Services_USA", "Consumer Discretionary_USA",
            "Consumer Staples_USA", "Energy_USA", "Financials_USA", "Health Care_USA",
            "Industrials_USA", "Information Technology_USA", "Materials_USA", "Utilities_USA"
        ]

    sector = st.selectbox("Select Sector", available_sectors)
    start_value = st.number_input("Portfolio value at PRE_START (e.g. 100000)", value=100.0)

    run_pred = st.button("Predict Portfolio Evolution")

    if run_pred:
        with st.spinner("Predicting prices..."):
            try:
                df, predicted, fig = predict_price_path(
                    sector=sector,
                    start_price=start_value
                )

                # --- Show Plot ---
                st.pyplot(fig)

                # Convert to DataFrame safely
                result_df = pd.DataFrame({
                    "Date": df,
                    "Predicted Portfolio Value": predicted
                })

                # --- Display Combined Data ---
                st.markdown("### Predicted Portfolio Values Over Time")
                st.dataframe(result_df, use_container_width=True)

                st.success("✅ Portfolio simulation completed successfully!")

            except Exception as e:
                st.warning(f"⚠️ Prediction failed: {e}")