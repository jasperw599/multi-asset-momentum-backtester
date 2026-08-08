from src.config import load_config
import numpy as np
import pandas as pd

from src.data.database import get_engine

CONFIG = load_config()

DEFAULT_MOMENTUM_COLUMN = (
    CONFIG["strategy"]["momentum_column"]
)

FEATURE_QUERY = """
    SELECT
        instrument_id,
        ticker,
        asset_class,
        date,
        adjusted_close,
        daily_return,
        volatility_20d,
        momentum_3_1,
        momentum_6_1,
        momentum_12_1
    FROM momentum_features
    WHERE momentum_12_1 IS NOT NULL
      AND volatility_20d IS NOT NULL
    ORDER BY date, ticker;
"""


def load_features():
    engine = get_engine()

    with engine.connect() as connection:
        data = pd.read_sql_query(FEATURE_QUERY, connection)

    data["date"] = pd.to_datetime(data["date"])

    return data


def build_monthly_signals(
    data,
    momentum_column=DEFAULT_MOMENTUM_COLUMN,
):
    valid_columns = {
        "momentum_3_1",
        "momentum_6_1",
        "momentum_12_1",
    }

    if momentum_column not in valid_columns:
        raise ValueError(
            f"Invalid momentum column: {momentum_column}"
        )

    data = data.copy()

    # Identify each calendar month
    data["month"] = data["date"].dt.to_period("M")

    # Exclude the latest incomplete calendar month
    latest_month = data["month"].max()
    data = data[data["month"] < latest_month]

    # Keep the final trading observation for each asset each month
    monthly = (
        data.sort_values(["instrument_id", "date"])
        .groupby(["instrument_id", "month"], as_index=False)
        .tail(1)
        .copy()
    )

    # Time-series momentum:
    # positive momentum = long
    # negative momentum = short
    # zero momentum = neutral
    monthly["ts_signal"] = np.sign(
        monthly[momentum_column]
    ).astype(int)

    # Cross-sectional momentum:
    # rank assets against each other within each month
    monthly["cs_rank"] = (
        monthly.groupby("month")[momentum_column]
        .rank(pct=True, method="first")
    )

    # Bottom 25% = short
    # Middle 50% = neutral
    # Top 25% = long
    monthly["cs_signal"] = np.select(
        [
            monthly["cs_rank"] <= 0.25,
            monthly["cs_rank"] > 0.75,
        ],
        [
            -1,
            1,
        ],
        default=0,
    )

    return monthly


def main():
    features = load_features()
    signals = build_monthly_signals(features)

    latest_date = signals["date"].max()

    latest = (
        signals[signals["date"] == latest_date]
        [
            [
                "ticker",
                "asset_class",
                "momentum_12_1",
                "volatility_20d",
                "ts_signal",
                "cs_rank",
                "cs_signal",
            ]
        ]
        .sort_values("momentum_12_1", ascending=False)
    )

    print(f"\nSignals for {latest_date.date()}\n")
    print(latest.to_string(index=False))


if __name__ == "__main__":
    main()