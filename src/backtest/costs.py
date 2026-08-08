from src.config import load_config
import numpy as np
import pandas as pd

from src.signals.momentum import load_features, build_monthly_signals
from src.portfolio.weights import build_portfolio_weights
from src.backtest.engine import run_backtest


CONFIG = load_config()

TRANSACTION_COST_BPS = CONFIG["strategy"]["transaction_cost_bps"]


def calculate_monthly_turnover(
    momentum_column="momentum_12_1",
    transaction_cost_bps=TRANSACTION_COST_BPS,
    volatility_floor=None,
):
    features = load_features()
    signals = build_monthly_signals(
	features,
	momentum_column=momentum_column,
    )
    weights = build_portfolio_weights(
        signals,
        volatility_floor=volatility_floor,
    )

    # January signal -> February holding month
    weights["holding_month"] = weights["month"] + 1

    weights = weights.sort_values(
        ["instrument_id", "holding_month"]
    )

    # Previous month's target weights
    weights["previous_ts_weight"] = (
        weights.groupby("instrument_id")["ts_weight"]
        .shift(1)
        .fillna(0.0)
    )

    weights["previous_cs_weight"] = (
        weights.groupby("instrument_id")["cs_weight"]
        .shift(1)
        .fillna(0.0)
    )

    # Amount traded
    weights["ts_turnover"] = (
        weights["ts_weight"]
        - weights["previous_ts_weight"]
    ).abs()

    weights["cs_turnover"] = (
        weights["cs_weight"]
        - weights["previous_cs_weight"]
    ).abs()

    monthly = (
        weights.groupby("holding_month", as_index=False)
        .agg(
            ts_turnover=("ts_turnover", "sum"),
            cs_turnover=("cs_turnover", "sum"),
        )
    )

    cost_rate = transaction_cost_bps / 10000

    monthly["ts_cost"] = monthly["ts_turnover"] * cost_rate
    monthly["cs_cost"] = monthly["cs_turnover"] * cost_rate

    return monthly


def run_net_backtest(
    momentum_column="momentum_12_1",
    transaction_cost_bps=TRANSACTION_COST_BPS,
    volatility_floor=None,
):
    portfolio = run_backtest(
        momentum_column=momentum_column,
        volatility_floor=volatility_floor,
    )

    costs = calculate_monthly_turnover(
        momentum_column=momentum_column,
        transaction_cost_bps=transaction_cost_bps,
        volatility_floor=volatility_floor,
    )

    portfolio["month"] = portfolio["date"].dt.to_period("M")

    portfolio = portfolio.merge(
        costs,
        left_on="month",
        right_on="holding_month",
        how="left",
    )

    portfolio[
        ["ts_turnover", "cs_turnover", "ts_cost", "cs_cost"]
    ] = portfolio[
        ["ts_turnover", "cs_turnover", "ts_cost", "cs_cost"]
    ].fillna(0.0)

    # Charge transaction costs once: on the first trading day
    # of each holding month
    first_dates = (
        portfolio.groupby("month")["date"]
        .transform("min")
    )

    portfolio["ts_cost_today"] = np.where(
        portfolio["date"] == first_dates,
        portfolio["ts_cost"],
        0.0,
    )

    portfolio["cs_cost_today"] = np.where(
        portfolio["date"] == first_dates,
        portfolio["cs_cost"],
        0.0,
    )

    portfolio["ts_net_return"] = (
        portfolio["ts_return"]
        - portfolio["ts_cost_today"]
    )

    portfolio["cs_net_return"] = (
        portfolio["cs_return"]
        - portfolio["cs_cost_today"]
    )

    portfolio["ts_net_equity"] = (
        1 + portfolio["ts_net_return"]
    ).cumprod()

    portfolio["cs_net_equity"] = (
        1 + portfolio["cs_net_return"]
    ).cumprod()

    return portfolio


def main():
    portfolio = run_net_backtest()

    print("\nTransaction cost assumption:")
    print(f"{TRANSACTION_COST_BPS} basis points per dollar traded")

    print("\nAverage monthly turnover:")
    print(
        "Time-series:",
        round(portfolio.groupby("month")["ts_turnover"].first().mean(), 3)
    )
    print(
        "Cross-sectional:",
        round(portfolio.groupby("month")["cs_turnover"].first().mean(), 3)
    )

    print("\nFinal gross vs net equity:")

    print(
        "Time-series gross:",
        round(portfolio["ts_equity"].iloc[-1], 3)
    )

    print(
        "Time-series net:",
        round(portfolio["ts_net_equity"].iloc[-1], 3)
    )

    print(
        "Cross-sectional gross:",
        round(portfolio["cs_equity"].iloc[-1], 3)
    )

    print(
        "Cross-sectional net:",
        round(portfolio["cs_net_equity"].iloc[-1], 3)
    )


if __name__ == "__main__":
    main()