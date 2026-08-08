import pandas as pd

from src.analytics.output import save_table

from src.config import load_config

from src.backtest.costs import run_net_backtest
from src.analytics.performance import calculate_metrics


CONFIG = load_config()

MOMENTUM_COLUMNS = (
    CONFIG["robustness"]["momentum_columns"]
)


def momentum_label(column):
    return (
        column
        .replace("momentum_", "")
        .replace("_", "-")
    )


def main():
    results = []

    for column in MOMENTUM_COLUMNS:
        label = momentum_label(column)

        print(f"Running {label} momentum...")

        portfolio = run_net_backtest(
            momentum_column=column
        )

        ts_metrics = calculate_metrics(
            portfolio["ts_net_return"]
        )

        cs_metrics = calculate_metrics(
            portfolio["cs_net_return"]
        )

        results.append(
            {
                "Signal": label,
                "Strategy": "Time-Series",
                **ts_metrics,
            }
        )

        results.append(
            {
                "Signal": label,
                "Strategy": "Cross-Sectional",
                **cs_metrics,
            }
        )

    results = pd.DataFrame(results)
    
    save_table(
        results,
        "parameter_robustness.csv",
    )

    display = results[
        [
            "Signal",
            "Strategy",
            "Cumulative Return",
            "CAGR",
            "Annualised Volatility",
            "Sharpe Ratio",
            "Maximum Drawdown",
        ]
    ].copy()

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

    print("\nMomentum Parameter Robustness:\n")
    print(display.to_string(index=False))


if __name__ == "__main__":
    main()