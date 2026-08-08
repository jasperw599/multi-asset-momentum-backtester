import numpy as np

from src.config import load_config

from src.signals.momentum import load_features, build_monthly_signals

CONFIG = load_config()

DEFAULT_VOLATILITY_FLOOR = (
    CONFIG["strategy"]["volatility_floor"]
)

def build_portfolio_weights(
    signals,
    volatility_floor=DEFAULT_VOLATILITY_FLOOR,
):
    data = signals.copy()

    # Inverse volatility:
    # lower-volatility assets receive larger nominal weights
    volatility = data["volatility_20d"].copy()

    if volatility_floor is not None:
        volatility = volatility.clip(
            lower=volatility_floor
        )

    data["effective_volatility"] = volatility

    data["inverse_volatility"] = (
        1.0 / data["effective_volatility"]
    )

    # --------------------------------------------------
    # TIME-SERIES MOMENTUM PORTFOLIO
    # --------------------------------------------------

    data["ts_raw_weight"] = (
        data["ts_signal"]
        * data["inverse_volatility"]
    )

    ts_gross_exposure = (
        data.groupby("month")["ts_raw_weight"]
        .transform(lambda x: x.abs().sum())
    )

    data["ts_weight"] = (
        data["ts_raw_weight"]
        / ts_gross_exposure
    )

    # --------------------------------------------------
    # CROSS-SECTIONAL MOMENTUM PORTFOLIO
    # --------------------------------------------------

    data["cs_long_raw"] = np.where(
        data["cs_signal"] == 1,
        data["inverse_volatility"],
        0.0,
    )

    data["cs_short_raw"] = np.where(
        data["cs_signal"] == -1,
        data["inverse_volatility"],
        0.0,
    )

    long_total = (
        data.groupby("month")["cs_long_raw"]
        .transform("sum")
        .replace(0, np.nan)
    )

    short_total = (
        data.groupby("month")["cs_short_raw"]
        .transform("sum")
        .replace(0, np.nan)
    )

    # Allocate 50% gross exposure to longs
    # and 50% gross exposure to shorts
    data["cs_weight"] = 0.0

    long_mask = data["cs_signal"] == 1
    short_mask = data["cs_signal"] == -1

    data.loc[long_mask, "cs_weight"] = (
        0.5
        * data.loc[long_mask, "cs_long_raw"]
        / long_total[long_mask]
    )

    data.loc[short_mask, "cs_weight"] = (
        -0.5
        * data.loc[short_mask, "cs_short_raw"]
        / short_total[short_mask]
    )

    return data


def main():
    features = load_features()
    signals = build_monthly_signals(features)
    portfolio = build_portfolio_weights(signals)

    latest_month = portfolio["month"].max()

    latest = portfolio[
        portfolio["month"] == latest_month
    ][
        [
            "ticker",
            "asset_class",
            "momentum_12_1",
            "volatility_20d",
            "ts_signal",
            "ts_weight",
            "cs_signal",
            "cs_weight",
        ]
    ].sort_values("ts_weight", ascending=False)

    print(f"\nPortfolio weights for {latest_month}\n")
    print(latest.to_string(index=False))

    print("\nChecks:")
    print(
        "TS gross exposure:",
        latest["ts_weight"].abs().sum()
    )
    print(
        "CS gross exposure:",
        latest["cs_weight"].abs().sum()
    )
    print(
        "CS net exposure:",
        latest["cs_weight"].sum()
    )


if __name__ == "__main__":
    main()