from src.config import load_config
from src.config import PROJECT_ROOT
import numpy as np
import pandas as pd

from src.backtest.costs import run_net_backtest


CONFIG = load_config()

TRADING_DAYS = CONFIG["backtest"]["trading_days_per_year"]

RESULTS_DIR = PROJECT_ROOT / "results" / "tables"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def calculate_metrics(returns):
    returns = returns.dropna()

    if returns.empty:
        raise ValueError("Return series is empty.")

    total_return = (1 + returns).prod() - 1

    years = len(returns) / TRADING_DAYS

    cagr = (1 + total_return) ** (1 / years) - 1

    annualised_volatility = (
        returns.std(ddof=1) * np.sqrt(TRADING_DAYS)
    )

    annualised_return = (
        returns.mean() * TRADING_DAYS
    )

    sharpe_ratio = (
        annualised_return / annualised_volatility
        if annualised_volatility != 0
        else np.nan
    )

    equity_curve = (1 + returns).cumprod()

    running_max = equity_curve.cummax()

    drawdown = (
        equity_curve / running_max - 1
    )

    max_drawdown = drawdown.min()

    return {
        "Cumulative Return": total_return,
        "CAGR": cagr,
        "Annualised Volatility": annualised_volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Maximum Drawdown": max_drawdown,
    }


def main():
    portfolio = run_net_backtest()

    strategies = {
        "Time-Series Gross": portfolio["ts_return"],
        "Time-Series Net": portfolio["ts_net_return"],
        "Cross-Sectional Gross": portfolio["cs_return"],
        "Cross-Sectional Net": portfolio["cs_net_return"],
    }

    results = {}

    for name, returns in strategies.items():
        results[name] = calculate_metrics(returns)

    results = pd.DataFrame(results).T

    results.to_csv(
        RESULTS_DIR / "performance.csv",
        index=True,
    )
    percentage_columns = [
        "Cumulative Return",
        "CAGR",
        "Annualised Volatility",
        "Maximum Drawdown",
    ]

    display = results.copy()

    for column in percentage_columns:
        display[column] = (
            display[column] * 100
        ).map(lambda x: f"{x:.2f}%")

    display["Sharpe Ratio"] = (
        display["Sharpe Ratio"]
        .map(lambda x: f"{x:.2f}")
    )

    print("\nPerformance Statistics:\n")
    print(display.to_string())


if __name__ == "__main__":
    main()