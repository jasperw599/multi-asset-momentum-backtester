import pandas as pd
import pytest

from src.portfolio.weights import build_portfolio_weights


def make_test_signals():
    return pd.DataFrame(
        {
            "instrument_id": [1, 2, 3, 4],
            "ticker": ["A", "B", "C", "D"],
            "month": [
                pd.Period("2020-01"),
                pd.Period("2020-01"),
                pd.Period("2020-01"),
                pd.Period("2020-01"),
            ],
            "volatility_20d": [
                0.05,
                0.10,
                0.20,
                0.40,
            ],
            "ts_signal": [
                1,
                1,
                -1,
                -1,
            ],
            "cs_signal": [
                1,
                1,
                -1,
                -1,
            ],
        }
    )


def test_time_series_gross_exposure_equals_one():
    signals = make_test_signals()

    portfolio = build_portfolio_weights(signals)

    gross_exposure = portfolio["ts_weight"].abs().sum()

    assert gross_exposure == pytest.approx(1.0)


def test_cross_sectional_portfolio_is_market_neutral():
    signals = make_test_signals()

    portfolio = build_portfolio_weights(signals)

    gross_exposure = portfolio["cs_weight"].abs().sum()
    net_exposure = portfolio["cs_weight"].sum()

    assert gross_exposure == pytest.approx(1.0)
    assert net_exposure == pytest.approx(0.0)


def test_volatility_floor_reduces_concentration():
    signals = make_test_signals()

    no_floor = build_portfolio_weights(
        signals,
        volatility_floor=None,
    )

    with_floor = build_portfolio_weights(
        signals,
        volatility_floor=0.10,
    )

    no_floor_max = no_floor["ts_weight"].abs().max()
    floor_max = with_floor["ts_weight"].abs().max()

    assert floor_max < no_floor_max