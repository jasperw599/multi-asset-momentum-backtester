import pandas as pd

from src.data.database import get_engine
from src.signals.momentum import load_features, build_monthly_signals
from src.portfolio.weights import build_portfolio_weights


DAILY_RETURNS_QUERY = """
    SELECT
        instrument_id,
        ticker,
        date,
        daily_return
    FROM daily_returns
    WHERE daily_return IS NOT NULL
    ORDER BY date, instrument_id;
"""


def load_daily_returns():
    engine = get_engine()

    with engine.connect() as connection:
        data = pd.read_sql_query(
            DAILY_RETURNS_QUERY,
            connection
        )

    data["date"] = pd.to_datetime(data["date"])
    data["month"] = data["date"].dt.to_period("M")

    return data

def assign_holding_month(weights):
    """
    A portfolio formed at the end of month t is held
    during month t + 1.

    This prevents look-ahead bias by ensuring that
    information observed at month-end is only applied
    to subsequent returns.
    """
    weights = weights.copy()

    weights["holding_month"] = (
        weights["month"] + 1
    )

    return weights

def run_backtest(
    momentum_column="momentum_12_1",
    volatility_floor=None,
):
    # -----------------------------------------
    # Build month-end portfolio weights
    # -----------------------------------------
    features = load_features()
    signals = build_monthly_signals(
        features,
	momentum_column=momentum_column,
    )
    weights = build_portfolio_weights(
	signals,
        volatility_floor=volatility_floor,
    )

    # A signal calculated at the end of January
    # is used during February, etc.
    weights = assign_holding_month(weights)

    weights = weights[
        [
            "instrument_id",
            "holding_month",
            "ts_weight",
            "cs_weight",
        ]
    ]

    # -----------------------------------------
    # Load subsequent daily returns
    # -----------------------------------------
    returns = load_daily_returns()

    # Match each day's return to the portfolio
    # chosen at the previous month-end
    backtest = returns.merge(
        weights,
        left_on=["instrument_id", "month"],
        right_on=["instrument_id", "holding_month"],
        how="inner",
    )

    # -----------------------------------------
    # Individual asset contributions
    # -----------------------------------------
    backtest["ts_contribution"] = (
        backtest["ts_weight"]
        * backtest["daily_return"]
    )

    backtest["cs_contribution"] = (
        backtest["cs_weight"]
        * backtest["daily_return"]
    )

    # -----------------------------------------
    # Aggregate into portfolio daily returns
    # -----------------------------------------
    portfolio = (
        backtest.groupby("date", as_index=False)
        .agg(
            ts_return=("ts_contribution", "sum"),
            cs_return=("cs_contribution", "sum"),
        )
        .sort_values("date")
    )

    # -----------------------------------------
    # Equity curves
    # Start with £1
    # -----------------------------------------
    portfolio["ts_equity"] = (
        1 + portfolio["ts_return"]
    ).cumprod()

    portfolio["cs_equity"] = (
        1 + portfolio["cs_return"]
    ).cumprod()

    return portfolio


def main():
    portfolio = run_backtest()

    print("\nFirst five backtest observations:\n")
    print(portfolio.head().to_string(index=False))

    print("\nLast five backtest observations:\n")
    print(portfolio.tail().to_string(index=False))

    print("\nFinal equity values:")
    print(
        "Time-series momentum:",
        round(portfolio["ts_equity"].iloc[-1], 3)
    )
    print(
        "Cross-sectional momentum:",
        round(portfolio["cs_equity"].iloc[-1], 3)
    )


if __name__ == "__main__":
    main()