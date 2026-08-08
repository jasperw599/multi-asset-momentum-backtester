import pandas as pd

from src.analytics.output import save_table

from src.backtest.costs import run_net_backtest
from src.analytics.performance import calculate_metrics


SPLIT_DATE = pd.Timestamp("2017-01-01")


def format_metrics(metrics):
    return {
        "Cumulative Return": metrics["Cumulative Return"],
        "CAGR": metrics["CAGR"],
        "Annualised Volatility": metrics["Annualised Volatility"],
        "Sharpe Ratio": metrics["Sharpe Ratio"],
        "Maximum Drawdown": metrics["Maximum Drawdown"],
    }


def main():

    # Keep the primary specification fixed:
    # 12-1 momentum, 10 bps costs, no volatility floor.
    portfolio = run_net_backtest(
        momentum_column="momentum_12_1",
        transaction_cost_bps=10,
        volatility_floor=None,
    )

    portfolio["date"] = pd.to_datetime(portfolio["date"])

    earlier = portfolio[
        portfolio["date"] < SPLIT_DATE
    ].copy()

    later = portfolio[
        portfolio["date"] >= SPLIT_DATE
    ].copy()

    results = []

    periods = {
        "Earlier Period": earlier,
        "Later Holdout": later,
    }

    for period_name, data in periods.items():

        ts_metrics = calculate_metrics(
            data["ts_net_return"]
        )

        cs_metrics = calculate_metrics(
            data["cs_net_return"]
        )

        results.append(
            {
                "Period": period_name,
                "Strategy": "Time-Series",
                **format_metrics(ts_metrics),
            }
        )

        results.append(
            {
                "Period": period_name,
                "Strategy": "Cross-Sectional",
                **format_metrics(cs_metrics),
            }
        )

    results = pd.DataFrame(results)

    save_table(
        results,
        "chronological_holdout.csv",
    )

    display = results.copy()

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

    print("\nChronological Holdout Analysis:\n")
    print(display.to_string(index=False))


if __name__ == "__main__":
    main()