import matplotlib.pyplot as plt
import pandas as pd
from src.config import PROJECT_ROOT
from src.backtest.costs import run_net_backtest
from src.analytics.benchmarks import build_benchmarks

FIGURE_DIR = PROJECT_ROOT / "results" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

def build_comparison():
    portfolio = run_net_backtest()
    portfolio = portfolio.set_index("date")

    benchmarks = build_benchmarks()

    comparison = pd.concat(
        [
            portfolio["ts_net_return"].rename(
                "Time-Series Momentum"
            ),
            portfolio["cs_net_return"].rename(
                "Cross-Sectional Momentum"
            ),
            benchmarks["SPY"].rename("SPY"),
            benchmarks["60/40"].rename("60/40"),
            benchmarks["Equal-Weight Multi-Asset"].rename(
                "Equal-Weight Multi-Asset"
            ),
        ],
        axis=1,
        join="inner",
    ).dropna()

    return comparison


def plot_equity_curves(comparison):
    equity = (1 + comparison).cumprod()

    ax = equity.plot(
        figsize=(12, 7),
        linewidth=1.5,
    )

    ax.set_title("Strategy and Benchmark Equity Curves")
    ax.set_xlabel("Date")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR / "equity_curves.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.show()


def plot_drawdowns(comparison):
    equity = (1 + comparison).cumprod()

    running_max = equity.cummax()

    drawdowns = equity / running_max - 1

    ax = drawdowns.plot(
        figsize=(12, 7),
        linewidth=1.2,
    )

    ax.set_title("Strategy and Benchmark Drawdowns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR / "drawdowns.png",
        dpi=200,
    bbox_inches="tight",
    )
    plt.show()


def main():
    comparison = build_comparison()

    print(
        f"Plotting period: "
        f"{comparison.index.min().date()} "
        f"to {comparison.index.max().date()}"
    )

    plot_equity_curves(comparison)
    plot_drawdowns(comparison)


if __name__ == "__main__":
    main()