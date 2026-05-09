# Quantitative-Financial-Risk-Modelling-and-Pandemic-Crisis-Simulation
A Streamlit-based analytical and simulation platform that integrates 
financial data science, econometrics, and machine learning to evaluate 
how different market sectors behave under stress events such as the 
COVID-19 pandemic.

## Tech Stack
- Python
- Streamlit
- Random Forest (scikit-learn)
- CAPM / Financial Econometrics
- Pandas / NumPy
- Yahoo Finance API
- Matplotlib

## What it does

The tool combines historical data analysis, risk computation, and 
predictive modelling to simulate portfolio value trajectories and 
sectoral resilience across two interactive tabs:

### Tab 1 - Sector Analysis
- Computes and visualises rolling Beta, volatility and cumulative 
  abnormal returns (CAR)
- Analyses sector behaviour across three pandemic phases: 
  Pre, Event and Recovery
- Supports both India and USA markets
- Outputs rolling β & σ plots, CAR plots and period summary tables

### Tab 2 - Portfolio Prediction
- Runs a Random Forest model trained on CAPM-based expected returns
- Simulates future portfolio value paths for each sector
- Input your own portfolio start value and see predicted evolution

## How to run

```bash
# Navigate to the src directory
cd src

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Follow the URL shown in the terminal to open the tool in your browser.

## Model Performance (MAE)

| Sector | MAE |
|--------|-----|
| Consumer Staples USA | 0.0046 |
| Health Care USA | 0.0059 |
| Healthcare Pharma India | 0.0059 |
| Materials USA | 0.0078 |
| Consumer Goods Services India | 0.0079 |
| Tech Communication India | 0.0071 |
| Utilities Essential India | 0.0105 |
| Industrials USA | 0.0117 |
| Financials USA | 0.0148 |
| Financials India | 0.0147 |
| Energy Materials India | 0.0143 |
| Industrials Infrastructure India | 0.0180 |
| Energy USA | 0.0200 |
| Consumer Discretionary USA | 0.0199 |
| Communication Services USA | 0.0214 |
| Information Technology USA | 0.0268 |

## Key Concepts

- **β (Beta)** - measures how tied a sector is to the overall market. 
  A spike in March 2020 means less diversification when it mattered most.
- **σ (Volatility)** - doubling means much larger day-to-day swings 
  and higher total risk.
- **CAR** - cumulative abnormal returns. Negative CAR during the shock 
  means the sector underperformed even after adjusting for risk.
- **κ (Kappa)** - how much volatility expanded in the crisis. 
  κ=2.1 means volatility more than doubled.

## Outputs

All outputs saved to `/output`:
- CSVs for basket returns, rolling β, rolling σ, CAPM AR/CAR, 
  period summary and simulated path
- PNG figures for each plot
- Trained models saved in `/output_models`

## Limitations

- Assumes linear CAPM relationship - ignores non-linear and 
  sentiment-driven effects
- Trained on 2019-2023 data only
- Uses only four features per model
- Each sector basket uses only three stocks
- Compounding errors can distort long-term projections

## Authors

Project developed as part of a Business and IT course at the University of Twente.
