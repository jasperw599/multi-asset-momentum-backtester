import pandas as pd

from src.analytics.output import save_table

from src.config import load_config

from src.backtest.costs import run_net_backtest
from src.analytics.performance import calculate_metrics
from src.signals.momentum import load_features, build_monthly_signals
from src.portfolio.weights import build_portfolio_weights


CONFIG = load_config()

VOLATILITY_FLOORS = (
    CONFIG["robustness"]["volatility_floors"]
)


def floor_label(floor):
    if floor is None:
        return "No Floor"

    return f"{floor:.0%} Floor"


def calculate_concentration(volatility_floor):
    features = load_features()

    signals = build_monthly_signals(
        features,
        momentum_column="momentum_12_1",
    )

    weights = build_portfolio_weights(
        signals,
        volatility_floor=volatility_floor,
    )

    monthly = (
        weights.groupby("month")
        .agg(
            ts_max_weight=(
                "ts_weight",
                lambda x: x.abs().max()
            ),
            cs_max_weight=(
                "cs_weight",
                lambda x: x.abs().max()
            ),
        )
    )

    return {
        "TS Avg Max Weight": monthly["ts_max_weight"].mean(),
        "TS Largest Weight": monthly["ts_max_weight"].max(),
        "CS Avg Max Weight": monthly["cs_max_weight"].mean(),
        "CS Largest Weight": monthly["cs_max_weight"].max(),
    }


def main():
    results = []

    for floor in VOLATILITY_FLOORS:
        label = floor_label(floor)

        print(f"Running {label}...")

        portfolio = run_net_backtest(
            momentum_column="momentum_12_1",
            transaction_cost_bps=10,
            volatility_floor=floor,
        )

        ts_metrics = calculate_metrics(
            portfolio["ts_net_return"]
        )

        cs_metrics = calculate_metrics(
            portfolio["cs_net_return"]
        )

        concentration = calculate_concentration(floor)

        results.append(
            {
                "Floor": label,
                "Strategy": "Time-Series",
                "CAGR": ts_metrics["CAGR"],
                "Sharpe": ts_metrics["Sharpe Ratio"],
                "Max Drawdown": ts_metrics["Maximum Drawdown"],
                "Avg Max Weight": concentration["TS Avg Max Weight"],
                "Largest Weight": concentration["TS Largest Weight"],
            }
        )

        results.append(
            {
                "Floor": label,
                "Strategy": "Cross-Sectional",
                "CAGR": cs_metrics["CAGR"],
                "Sharpe": cs_metrics["Sharpe Ratio"],
                "Max Drawdown": cs_metrics["Maximum Drawdown"],
                "Avg Max Weight": concentration["CS Avg Max Weight"],
                "Largest Weight": concentration["CS Largest Weight"],
            }
        )

    results = pd.DataFrame(results)

    save_table(
        results,
        "volatility_floor_sensitivity.csv",
    )

    display = results.copy()

    for column in [
        "CAGR",
        "Max Drawdown",
        "Avg Max Weight",
        "Largest Weight",
    ]:
        display[column] = (
            display[column] * 100
        ).map(lambda x: f"{x:.2f}%")

    display["Sharpe"] = (
        display["Sharpe"]
        .map(lambda x: f"{x:.2f}")
    )

    print("\nVolatility Floor Sensitivity:\n")
    print(display.to_string(index=False))


if __name__ == "__main__":
    main()