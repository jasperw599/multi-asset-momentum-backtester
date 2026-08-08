import pandas as pd
import pytest

from src.backtest.engine import assign_holding_month
from src.backtest.costs import run_net_backtest


def test_signals_are_applied_to_next_month():
    weights = pd.DataFrame(
        {
            "instrument_id": [1, 2],
            "month": [
                pd.Period("2024-01"),
                pd.Period("2024-06"),
            ],
            "ts_weight": [0.5, -0.5],
            "cs_weight": [0.5, -0.5],
        }
    )

    result = assign_holding_month(weights)

    assert result.loc[0, "holding_month"] == pd.Period(
        "2024-02"
    )

    assert result.loc[1, "holding_month"] == pd.Period(
        "2024-07"
    )


def test_transaction_costs_reduce_final_equity():
    no_cost = run_net_backtest(
        momentum_column="momentum_12_1",
        transaction_cost_bps=0,
        volatility_floor=None,
    )

    with_cost = run_net_backtest(
        momentum_column="momentum_12_1",
        transaction_cost_bps=10,
        volatility_floor=None,
    )

    assert (
        with_cost["ts_net_equity"].iloc[-1]
        <
        no_cost["ts_net_equity"].iloc[-1]
    )

    assert (
        with_cost["cs_net_equity"].iloc[-1]
        <
        no_cost["cs_net_equity"].iloc[-1]
    )


def test_backtest_returns_are_finite():
    portfolio = run_net_backtest(
        momentum_column="momentum_12_1",
        transaction_cost_bps=10,
        volatility_floor=None,
    )

    assert portfolio["ts_net_return"].notna().all()
    assert portfolio["cs_net_return"].notna().all()

    assert (
        portfolio["ts_net_return"].abs() < 1
    ).all()

    assert (
        portfolio["cs_net_return"].abs() < 1
    ).all()