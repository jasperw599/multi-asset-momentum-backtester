import pandas as pd

from src.analytics.output import save_table

from src.config import load_config

from src.backtest.costs import run_net_backtest
from src.analytics.performance import calculate_metrics


CONFIG = load_config()

COST_LEVELS = (
    CONFIG["robustness"]["transaction_cost_bps"]
)


def main():
    results = []

    for cost_bps in COST_LEVELS:

        print(f"Running backtest at {cost_bps} bps...")

        portfolio = run_net_backtest(
            momentum_column="momentum_12_1",
            transaction_cost_bps=cost_bps,
        )

        ts_metrics = calculate_metrics(
            portfolio["ts_net_return"]
        )

        cs_metrics = calculate_metrics(
            portfolio["cs_net_return"]
        )

        results.append(
            {
                "Cost (bps)": cost_bps,
                "Strategy": "Time-Series",
                **ts_metrics,
            }
        )

        results.append(
            {
                "Cost (bps)": cost_bps,
                "Strategy": "Cross-Sectional",
                **cs_metrics,
            }
        )

    results = pd.DataFrame(results)

    save_table(
        results,
        "cost_sensitivity.csv",
    )

    display = results[
        [
            "Cost (bps)",
            "Strategy",
            "Cumulative Return",
            "CAGR",
            "Sharpe Ratio",
            "Maximum Drawdown",
        ]
    ].copy()

    percentage_columns = [
        "Cumulative Return",
        "CAGR",
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

    print("\nTransaction Cost Sensitivity:\n")
    print(display.to_string(index=False))


if __name__ == "__main__":
    main()