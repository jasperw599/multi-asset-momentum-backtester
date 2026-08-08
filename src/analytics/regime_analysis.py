import pandas as pd

from src.analytics.output import save_table

from src.backtest.costs import run_net_backtest
from src.analytics.benchmarks import build_benchmarks
from src.analytics.performance import calculate_metrics


REGIMES = {
    "GFC / Aftermath": (
        "2008-02-01",
        "2009-12-31",
    ),
    "Post-GFC Expansion": (
        "2010-01-01",
        "2019-12-31",
    ),
    "COVID Shock / Recovery": (
        "2020-01-01",
        "2021-12-31",
    ),
    "Inflation / Rate Shock": (
        "2022-01-01",
        "2023-12-31",
    ),
    "Recent Period": (
        "2024-01-01",
        "2026-12-31",
    ),
}


def build_comparison():
    portfolio = run_net_backtest(
        momentum_column="momentum_12_1",
        transaction_cost_bps=10,
        volatility_floor=None,
    )

    portfolio = portfolio.set_index("date")

    benchmarks = build_benchmarks()

    comparison = pd.concat(
        [
            portfolio["ts_net_return"].rename(
                "Time-Series"
            ),
            portfolio["cs_net_return"].rename(
                "Cross-Sectional"
            ),
            benchmarks["SPY"].rename("SPY"),
            benchmarks["60/40"].rename("60/40"),
        ],
        axis=1,
        join="inner",
    ).dropna()

    return comparison


def main():
    comparison = build_comparison()

    results = []

    for regime, (start, end) in REGIMES.items():

        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        period = comparison.loc[
            (comparison.index >= start)
            & (comparison.index <= end)
        ]

        if period.empty:
            continue

        for strategy in period.columns:

            metrics = calculate_metrics(
                period[strategy]
            )

            results.append(
                {
                    "Regime": regime,
                    "Strategy": strategy,
                    "Cumulative Return":
                        metrics["Cumulative Return"],
                    "Annualised Volatility":
                        metrics["Annualised Volatility"],
                    "Sharpe":
                        metrics["Sharpe Ratio"],
                    "Max Drawdown":
                        metrics["Maximum Drawdown"],
                }
            )

    results = pd.DataFrame(results)

    save_table(
        results,
        "regime_analysis.csv",
    )

    display = results.copy()

    for column in [
        "Cumulative Return",
        "Annualised Volatility",
        "Max Drawdown",
    ]:
        display[column] = (
            display[column] * 100
        ).map(lambda x: f"{x:.2f}%")

    display["Sharpe"] = (
        display["Sharpe"]
        .map(lambda x: f"{x:.2f}")
    )

    print("\nRegime Analysis:\n")

    print(
        display.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()