import pandas as pd

from src.analytics.output import save_table

from src.config import load_config

from src.backtest.costs import run_net_backtest
from src.analytics.performance import calculate_metrics


SPLIT_DATE = pd.Timestamp("2017-01-01")

CONFIG = load_config()

MOMENTUM_COLUMNS = (
    CONFIG["robustness"]["momentum_columns"]
)

VOLATILITY_FLOORS = (
    CONFIG["robustness"]["volatility_floors"]
)

TRANSACTION_COST_BPS = (
    CONFIG["strategy"]["transaction_cost_bps"]
)


def momentum_label(column):
    return (
        column
        .replace("momentum_", "")
        .replace("_", "-")
    )


def floor_label(floor):
    if floor is None:
        return "None"

    return f"{floor:.0%}"


def evaluate_period(returns):
    metrics = calculate_metrics(returns)

    return {
        "CAGR": metrics["CAGR"],
        "Sharpe": metrics["Sharpe Ratio"],
        "Max Drawdown": metrics["Maximum Drawdown"],
    }


def main():
    results = []

    for momentum_column in MOMENTUM_COLUMNS:

        for floor in VOLATILITY_FLOORS:

            momentum_name = momentum_label(
                momentum_column
            )

            floor_name = floor_label(floor)

            print(
                f"Testing {momentum_name}, "
                f"vol floor {floor_name}..."
            )

            portfolio = run_net_backtest(
                momentum_column=momentum_column,
                transaction_cost_bps=TRANSACTION_COST_BPS,
                volatility_floor=floor,
            )

            portfolio["date"] = pd.to_datetime(
                portfolio["date"]
            )

            earlier = portfolio[
                portfolio["date"] < SPLIT_DATE
            ]

            later = portfolio[
                portfolio["date"] >= SPLIT_DATE
            ]

            for strategy, return_column in {
                "Time-Series": "ts_net_return",
                "Cross-Sectional": "cs_net_return",
            }.items():

                earlier_metrics = evaluate_period(
                    earlier[return_column]
                )

                later_metrics = evaluate_period(
                    later[return_column]
                )

                results.append(
                    {
                        "Strategy": strategy,
                        "Momentum": momentum_name,
                        "Vol Floor": floor_name,
                        "Earlier Sharpe":
                            earlier_metrics["Sharpe"],
                        "Later Sharpe":
                            later_metrics["Sharpe"],
                        "Earlier CAGR":
                            earlier_metrics["CAGR"],
                        "Later CAGR":
                            later_metrics["CAGR"],
                        "Later Max DD":
                            later_metrics["Max Drawdown"],
                    }
                )

    results = pd.DataFrame(results)

    save_table(
        results,
        "selection_bias.csv",
    )

    print("\nAll Parameter Specifications:\n")

    display = results.copy()

    for column in [
        "Earlier CAGR",
        "Later CAGR",
        "Later Max DD",
    ]:
        display[column] = (
            display[column] * 100
        ).map(lambda x: f"{x:.2f}%")

    for column in [
        "Earlier Sharpe",
        "Later Sharpe",
    ]:
        display[column] = display[column].map(
            lambda x: f"{x:.2f}"
        )

    print(
        display.sort_values(
            ["Strategy", "Earlier Sharpe"],
            ascending=[True, False],
        ).to_string(index=False)
    )

    print("\nBest Earlier-Period Specification:\n")

    for strategy in [
        "Time-Series",
        "Cross-Sectional",
    ]:

        subset = results[
            results["Strategy"] == strategy
        ]

        best = subset.loc[
            subset["Earlier Sharpe"].idxmax()
        ]

        print(strategy)
        print(
            f"  Selected momentum: "
            f"{best['Momentum']}"
        )
        print(
            f"  Selected volatility floor: "
            f"{best['Vol Floor']}"
        )
        print(
            f"  Earlier Sharpe: "
            f"{best['Earlier Sharpe']:.2f}"
        )
        print(
            f"  Later Sharpe: "
            f"{best['Later Sharpe']:.2f}"
        )
        print(
            f"  Earlier CAGR: "
            f"{best['Earlier CAGR']:.2%}"
        )
        print(
            f"  Later CAGR: "
            f"{best['Later CAGR']:.2%}"
        )
        print()


if __name__ == "__main__":
    main()