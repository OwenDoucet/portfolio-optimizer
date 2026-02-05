import streamlit as st
import pandas as pd
import altair as alt

from data import load_price_data
from portfolio import compute_returns, expected_returns, covariance_matrix, portfolio_return, portfolio_risk
from optimizer import maximize_return_given_risk
from max_sharpe import maximize_sharpe
from helper import get_active_sectors, build_full_sector_caps
from frontier import generate_efficient_frontier

# -------------------------
# App Title
# -------------------------
st.set_page_config(page_title="Portfolio Optimizer", layout="wide")
st.title("📈 Portfolio Optimizer")
st.caption("Developed by Owen Doucet")
st.markdown("[Connect with me on LinkedIn](https://www.linkedin.com/in/owen-doucet-2151b7336/)")


# -------------------------
# Sidebar Inputs
# -------------------------
with st.sidebar:
    st.header("Portfolio Inputs")
    tickers_input = st.text_input("Tickers (comma-separated)", "AAPL,MSFT,GOOG,AMZN")
    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    rf = st.number_input("Risk-free rate", value=0.023, format="%.3f")
    target_risk = st.slider("Target Risk", 0.1, 0.5, 0.25)

    method = st.selectbox("Optimization Method", ["Max Sharpe", "Target Risk"])

# -------------------------
# Get sectors and caps
# -------------------------
sectors, active_sectors = get_active_sectors(tickers)

user_sector_caps = {}
if st.sidebar.checkbox("Set sector max caps"):
    st.sidebar.subheader("Sector Max Caps")
    for sector in active_sectors:
        user_sector_caps[sector] = st.sidebar.slider(
            f"Max {sector} (%)", 0, 100, 100
        ) / 100

sector_max = build_full_sector_caps(sectors, user_sector_caps)

# -------------------------
# Load Data
# -------------------------
date_input = st.date_input("Start Date for Stock Data (YYYY-MM-DD)", value=pd.to_datetime("2019-01-01"))
prices = load_price_data(tickers, date_input)
returns = compute_returns(prices)

mu = expected_returns(returns)
Sigma = covariance_matrix(returns)

# -------------------------
# Run Optimization
# -------------------------
if st.button("Run Optimization"):
    if method == "Max Sharpe":
        weights = maximize_sharpe(mu, Sigma, tickers, sectors, rf, sector_max)
    else:
        weights = maximize_return_given_risk(mu, Sigma, target_risk, tickers, sectors, sector_max)

    # -------------------------
    # Portfolio Summary
    # -------------------------
    st.subheader("Optimal Portfolio Allocation")
    portfolio_df = pd.DataFrame({
        "Ticker": tickers,
        "Weight": weights
    })

    total_sector = sum(sector_max.values())
    if total_sector < 1:
        st.markdown(
            f'<span style="color:orange">⚠️ Total sector caps below 100%: {total_sector*100:.1f}%</span>',
            unsafe_allow_html=True
        )
    else:
        # Show portfolio table
        st.table(portfolio_df.style.format({"Weight": "{:.2%}"}))

        # Show key metrics
        col1, col2 = st.columns(2)
        col1.metric("Expected Return", f"{portfolio_return(weights, mu):.2%}")
        col2.metric("Portfolio Risk", f"{portfolio_risk(weights, Sigma):.2%}")

        # Pie chart for allocation
        st.subheader("Portfolio Allocation Pie Chart")
        pie_chart = alt.Chart(portfolio_df).mark_arc().encode(
            theta="Weight",
            color="Ticker",
            tooltip=["Ticker", alt.Tooltip("Weight", format=".2%")]
        )
        st.altair_chart(pie_chart, use_container_width=True)

        risks, rets, _ = generate_efficient_frontier(mu, Sigma)

        st.subheader("Efficient Frontier")
        frontier_df = pd.DataFrame({
            "Risks": risks,
            "Return": rets
        })
        optimal_point = pd.DataFrame({
            "Risk": [portfolio_risk(weights, Sigma)],
            "Return": [portfolio_return(weights, mu)]
        })

        frontier_chart = alt.Chart(frontier_df).mark_circle(
            size = 30,
            opacity = 0.4
        ).encode(
            x=alt.X("Risk", title="Portfolio Risk"),
            y=alt.Y("Return", title="Expected Return"),
            tooltip=[
                alt.Tooltip("Risk", format=".2%f"),
                alt.Tooltip("Return", format=".2%f")
            ]
        )
        optimal_chart = alt.Chart(optimal_point).mark_point(
            size=200,
            shape="diamond",
            color="red"
        ).encode(
            x="Risk",
            y="Return",
            tooltip=[
                alt.Tooltip("Risk", format=".2%"),
                alt.Tooltip("Return", format=".2%")
            ]
        )

        layered_chart = alt.layer(
            frontier_chart,
            optimal_chart
        ).resolve_scale(
            x="shared",
            y="shared"
        )

        st.altair_chart(layered_chart, use_container_width=True)
