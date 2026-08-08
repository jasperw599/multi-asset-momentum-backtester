import pandas as pd
import pytest

from src.signals.momentum import build_monthly_signals


def make_signal_data():
    dates = pd.to_datetime(
        [
            "2024-01-31",
            "2024-01-31",
            "2024-01-31",
            "2024-01-31",
            "2024-02-29",
            "2024-02-29",
            "2024-02-29",
            "2024-02-29",
        ]
    )

    return pd.DataFrame(
        {
            "instrument_id": [
                1, 2, 3, 4,
                1, 2, 3, 4,
            ],
            "ticker": [
                "A", "B", "C", "D",
                "A", "B", "C", "D",
            ],
            "asset_class": ["test"] * 8,
            "date": dates,
            "adjusted_close": [100.0] * 8,
            "daily_return": [0.0] * 8,
            "volatility_20d": [0.10] * 8,

            "momentum_3_1": [
                0.40, 0.20, -0.10, -0.30,
                0.50, 0.30, -0.20, -0.40,
            ],

            "momentum_6_1": [
                0.30, 0.10, -0.20, -0.40,
                0.40, 0.20, -0.30, -0.50,
            ],

            "momentum_12_1": [
                0.20, 0.10, -0.10, -0.20,
                0.30, 0.20, -0.20, -0.30,
            ],
        }
    )


def test_time_series_signal_matches_momentum_sign():
    data = make_signal_data()

    signals = build_monthly_signals(
        data,
        momentum_column="momentum_12_1",
    )

    assert (
        signals.loc[
            signals["momentum_12_1"] > 0,
            "ts_signal",
        ] == 1
    ).all()

    assert (
        signals.loc[
            signals["momentum_12_1"] < 0,
            "ts_signal",
        ] == -1
    ).all()


def test_cross_sectional_signal_selects_extremes():
    data = make_signal_data()

    signals = build_monthly_signals(
        data,
        momentum_column="momentum_12_1",
    )

    longs = signals[
        signals["cs_signal"] == 1
    ]["ticker"].tolist()

    shorts = signals[
        signals["cs_signal"] == -1
    ]["ticker"].tolist()

    assert longs == ["A"]
    assert shorts == ["D"]


def test_invalid_momentum_column_raises_error():
    data = make_signal_data()

    with pytest.raises(ValueError):
        build_monthly_signals(
            data,
            momentum_column="made_up_signal",
        )