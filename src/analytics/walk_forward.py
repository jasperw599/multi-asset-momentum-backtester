import numpy as np
import pandas as pd

from src.analytics.output import save_table

from src.backtest.costs import run_net_backtest
from src.backtest.engine import load_daily_returns
from src.analytics.performance import calculate_metrics
from src.signals.momentum import load_features, build_monthly_signals
from src.portfolio.weights import build_portfolio_weights


MOMENTUM_SIGNALS = {
    "3-1": "momentum_3_1",
    "6-1": "momentum_6_1",
    "12-1": "momentum_12_1",
}

VOLATILITY_FLOORS = {
    "None": None,
    "5%": 0.05,
    "10%": 0.10,
}

LOOKBACK_YEARS = 5
TRANSACTION_COST_BPS = 10


def sharpe_ratio(returns):
    returns = returns.dropna()

    if len(returns) < 2:
        return np.nan

    volatility = returns.std(ddof=1)

    if volatility == 0:
        return np.nan

    return (
        returns.mean()
        / volatility
        * np.sqrt(252)
    )


def load_specifications():
    """
    Precompute returns and portfolio weights for every
    parameter specification.
    """

    features = load_features()

    specifications = {}

    for momentum_label, momentum_column in MOMENTUM_SIGNALS.items():

        for floor_label, floor in VOLATILITY_FLOORS.items():

            label = (
                f"{momentum_label} | "
                f"floor={floor_label}"
            )

            print(f"Loading {label}...")

            # Net returns used only for historical
            # parameter selection.
            portfolio = run_net_backtest(
                momentum_column=momentum_column,
                transaction_cost_bps=TRANSACTION_COST_BPS,
                volatility_floor=floor,
            )

            portfolio["date"] = pd.to_datetime(
                portfolio["date"]
            )

            portfolio = portfolio.set_index("date")

            # Build target weights separately so that the
            # final walk-forward simulation can calculate
            # TRUE turnover between changing specifications.
            signals = build_monthly_signals(
                features,
                momentum_column=momentum_column,
            )

            weights = build_portfolio_weights(
                signals,
                volatility_floor=floor,
            )

            weights["holding_month"] = (
                weights["month"] + 1
            )

            specifications[label] = {
                "ts_returns": portfolio["ts_net_return"],
                "cs_returns": portfolio["cs_net_return"],
                "weights": weights[
                    [
                        "instrument_id",
                        "holding_month",
                        "ts_weight",
                        "cs_weight",
                    ]
                ].copy(),
            }

    return specifications


def select_specifications(
    specifications,
    strategy,
):
    """
    Select the best specification using only the previous
    five calendar years.
    """

    return_key = (
        "ts_returns"
        if strategy == "Time-Series"
        else "cs_returns"
    )

    all_dates = pd.concat(
        [
            specification[return_key]
            for specification in specifications.values()
        ],
        axis=1,
    ).index

    first_year = all_dates.min().year
    last_year = all_dates.max().year

    selections = []

    for test_year in range(
        first_year + LOOKBACK_YEARS,
        last_year + 1,
    ):

        training_start = pd.Timestamp(
            year=test_year - LOOKBACK_YEARS,
            month=1,
            day=1,
        )

        training_end = pd.Timestamp(
            year=test_year - 1,
            month=12,
            day=31,
        )

        training_sharpes = {}

        for label, specification in specifications.items():

            returns = specification[return_key]

            training_returns = returns.loc[
                (returns.index >= training_start)
                & (returns.index <= training_end)
            ]

            training_sharpes[label] = sharpe_ratio(
                training_returns
            )

        valid_sharpes = {
            label: value
            for label, value in training_sharpes.items()
            if not np.isnan(value)
        }

        if not valid_sharpes:
            continue

        selected = max(
            valid_sharpes,
            key=valid_sharpes.get,
        )

        selections.append(
            {
                "Test Year": test_year,
                "Selected Specification": selected,
                "Training Sharpe":
                    valid_sharpes[selected],
            }
        )

    return pd.DataFrame(selections)


def build_selected_weights(
    specifications,
    selections,
    strategy,
):
    """
    Construct one continuous sequence of ACTUAL target
    weights from the specifications selected each year.
    """

    weight_column = (
        "ts_weight"
        if strategy == "Time-Series"
        else "cs_weight"
    )

    selected_weights = []

    for _, selection in selections.iterrows():

        year = int(selection["Test Year"])
        label = selection["Selected Specification"]

        weights = specifications[label]["weights"].copy()

        weights = weights[
            weights["holding_month"]
            .apply(lambda month: month.year == year)
        ].copy()

        weights = weights[
            [
                "instrument_id",
                "holding_month",
                weight_column,
            ]
        ]

        weights = weights.rename(
            columns={weight_column: "weight"}
        )

        selected_weights.append(weights)

    return pd.concat(
        selected_weights,
        ignore_index=True,
    )


def calculate_actual_turnover(selected_weights):
    """
    Calculate turnover from the actual sequence of selected
    portfolios, including transitions between models.
    """

    weights = selected_weights.sort_values(
        ["instrument_id", "holding_month"]
    ).copy()

    weights["previous_weight"] = (
        weights.groupby("instrument_id")["weight"]
        .shift(1)
        .fillna(0.0)
    )

    weights["turnover"] = (
        weights["weight"]
        - weights["previous_weight"]
    ).abs()

    monthly_turnover = (
        weights.groupby(
            "holding_month",
            as_index=False,
        )
        .agg(turnover=("turnover", "sum"))
    )

    monthly_turnover["transaction_cost"] = (
        monthly_turnover["turnover"]
        * TRANSACTION_COST_BPS
        / 10000
    )

    return monthly_turnover


def simulate_selected_portfolio(selected_weights):
    """
    Apply the selected target weights to future daily returns,
    then charge transaction costs based on actual changes in
    those selected weights.
    """

    returns = load_daily_returns()

    merged = returns.merge(
        selected_weights,
        left_on=["instrument_id", "month"],
        right_on=["instrument_id", "holding_month"],
        how="inner",
    )

    merged["contribution"] = (
        merged["weight"]
        * merged["daily_return"]
    )

    portfolio = (
        merged.groupby("date", as_index=False)
        .agg(
            gross_return=("contribution", "sum")
        )
        .sort_values("date")
    )

    portfolio["month"] = (
        portfolio["date"].dt.to_period("M")
    )

    turnover = calculate_actual_turnover(
        selected_weights
    )

    portfolio = portfolio.merge(
        turnover,
        left_on="month",
        right_on="holding_month",
        how="left",
    )

    portfolio[
        ["turnover", "transaction_cost"]
    ] = portfolio[
        ["turnover", "transaction_cost"]
    ].fillna(0.0)

    first_date = (
        portfolio.groupby("month")["date"]
        .transform("min")
    )

    portfolio["cost_today"] = np.where(
        portfolio["date"] == first_date,
        portfolio["transaction_cost"],
        0.0,
    )

    portfolio["net_return"] = (
        portfolio["gross_return"]
        - portfolio["cost_today"]
    )

    return portfolio


def main():
    specifications = load_specifications()

    summary_results = []

    for strategy in [
        "Time-Series",
        "Cross-Sectional",
    ]:

        selections = select_specifications(
            specifications,
            strategy,
        )

        selected_weights = build_selected_weights(
            specifications,
            selections,
            strategy,
        )

        portfolio = simulate_selected_portfolio(
            selected_weights
        )

        # Calculate realised return in each test year
        portfolio["year"] = portfolio["date"].dt.year

        yearly_returns = (
            portfolio.groupby("year")["net_return"]
            .apply(lambda x: (1 + x).prod() - 1)
        )

        selections["Test Return"] = (
            selections["Test Year"]
            .map(yearly_returns)
        )

        metrics = calculate_metrics(
            portfolio["net_return"]
        )

        summary_results.append(
            {
                "Strategy": strategy,
                **metrics,
            }
        )

        strategy_slug = (
            strategy
            .lower()
            .replace("-", "_")
        )

        save_table(
            selections,
            f"walk_forward_{strategy_slug}_selections.csv",
        )

        print(
            f"\n{strategy} "
            f"Corrected Walk-Forward Selections:\n"
        )

        display = selections.copy()

        display["Training Sharpe"] = (
            display["Training Sharpe"]
            .map(lambda x: f"{x:.2f}")
        )

        display["Test Return"] = (
            display["Test Return"] * 100
        ).map(lambda x: f"{x:.2f}%")

        print(
            display.to_string(index=False)
        )

        print(
            f"\n{strategy} "
            f"Corrected Walk-Forward Performance:"
        )

        print(
            "Cumulative Return:",
            f"{metrics['Cumulative Return']:.2%}"
        )

        print(
            "CAGR:",
            f"{metrics['CAGR']:.2%}"
        )

        print(
            "Annualised Volatility:",
            f"{metrics['Annualised Volatility']:.2%}"
        )

        print(
            "Sharpe Ratio:",
            f"{metrics['Sharpe Ratio']:.2f}"
        )

        print(
            "Maximum Drawdown:",
            f"{metrics['Maximum Drawdown']:.2%}"
        )


    summary_results = pd.DataFrame(
        summary_results
    )

    save_table(
        summary_results,
        "walk_forward_summary.csv",
    )

if __name__ == "__main__":
    main()