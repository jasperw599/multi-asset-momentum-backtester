import numpy as np
import pandas as pd

from src.data.database import get_engine
from src.backtest.costs import run_net_backtest
from src.analytics.performance import calculate_metrics


UNIVERSE = [
    "SPY", "QQQ", "IWM", "EFA", "EEM",
    "VNQ",
    "SHY", "IEF", "TLT",
    "GLD", "SLV", "DBC", "USO",
    "UUP", "FXE", "FXY",
]


def load_asset_returns():
    query = """
        SELECT
            ticker,
            date,
            daily_return
        FROM daily_returns
        WHERE daily_return IS NOT NULL
        ORDER BY date, ticker;
    """

    engine = get_engine()

    with engine.connect() as connection:
        data = pd.read_sql_query(query, connection)

    data["date"] = pd.to_datetime(data["date"])

    returns = data.pivot(
        index="date",
        columns="ticker",
        values="daily_return",
    ).sort_index()

    return returns


def monthly_rebalanced_portfolio(asset_returns, target_weights):
    """
    Simulate a portfolio that is reset to its target weights
    on the first available trading day of every month.
    """

    asset_returns = asset_returns.dropna().copy()

    current_values = None
    previous_month = None
    portfolio_returns = []

    for date, row in asset_returns.iterrows():

        current_month = date.to_period("M")

        # Rebalance at the beginning of each new month
        if current_values is None or current_month != previous_month:

            if current_values is None:
                portfolio_value = 1.0
            else:
                portfolio_value = current_values.sum()

            current_values = pd.Series(
                {
                    ticker: portfolio_value * weight
                    for ticker, weight in target_weights.items()
                }
            )

        previous_value = current_values.sum()

        # Apply today's asset returns
        current_values = current_values * (1 + row)

        new_value = current_values.sum()

        portfolio_return = (
            new_value / previous_value - 1
        )

        portfolio_returns.append(
            (date, portfolio_return)
        )

        previous_month = current_month

    return pd.Series(
        data=[x[1] for x in portfolio_returns],
        index=[x[0] for x in portfolio_returns],
    )


def build_benchmarks():
    returns = load_asset_returns()

    # -----------------------------------------
    # SPY benchmark
    # -----------------------------------------
    spy = returns["SPY"].dropna()

    # -----------------------------------------
    # 60/40 equity/bond benchmark
    # -----------------------------------------
    sixty_forty = monthly_rebalanced_portfolio(
        returns[["SPY", "IEF"]],
        {
            "SPY": 0.60,
            "IEF": 0.40,
        },
    )

    # -----------------------------------------
    # Equal-weight multi-asset benchmark
    # -----------------------------------------
    missing = [
        ticker
        for ticker in UNIVERSE
        if ticker not in returns.columns
    ]

    if missing:
        raise ValueError(
            f"Missing benchmark instruments: {missing}"
        )

    equal_weight = monthly_rebalanced_portfolio(
        returns[UNIVERSE],
        {
            ticker: 1 / len(UNIVERSE)
            for ticker in UNIVERSE
        },
    )

    return {
        "SPY": spy,
        "60/40": sixty_forty,
        "Equal-Weight Multi-Asset": equal_weight,
    }


def main():

    # Our momentum strategies
    portfolio = run_net_backtest()
    portfolio = portfolio.set_index("date")

    # Passive benchmarks
    benchmarks = build_benchmarks()

    # Put everything together
    comparison = pd.concat(
        [
            portfolio["ts_net_return"].rename(
                "Time-Series Momentum"
            ),
            portfolio["cs_net_return"].rename(
                "Cross-Sectional Momentum"
            ),
            benchmarks["SPY"].rename("SPY"),
            benchmarks["60/40"].rename("60/40"),
            benchmarks["Equal-Weight Multi-Asset"].rename(
                "Equal-Weight Multi-Asset"
            ),
        ],
        axis=1,
        join="inner",
    ).dropna()

    print(
        f"\nComparison period: "
        f"{comparison.index.min().date()} "
        f"to {comparison.index.max().date()}"
    )

    results = {}

    for strategy in comparison.columns:
        results[strategy] = calculate_metrics(
            comparison[strategy]
        )

    results = pd.DataFrame(results).T

    display = results.copy()

    percentage_columns = [
        "Cumulative Return",
        "CAGR",
        "Annualised Volatility",
        "Maximum Drawdown",
    ]

    for column in percentage_columns:
        display[column] = (
            display[column] * 100
        ).map(lambda x: f"{x:.2f}%")

    display["Sharpe Ratio"] = (
        display["Sharpe Ratio"]
        .map(lambda x: f"{x:.2f}")
    )

    print("\nStrategy vs Benchmark Performance:\n")
    print(display.to_string())


if __name__ == "__main__":
    main()