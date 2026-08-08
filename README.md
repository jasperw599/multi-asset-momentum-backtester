\# Multi-Asset Systematic Momentum Backtester



A Python, SQL and PostgreSQL research platform for testing systematic momentum strategies across a diversified multi-asset ETF universe.



The project investigates:



> \*\*How robust is momentum across asset classes after accounting for transaction costs, portfolio risk, parameter uncertainty and strategy-selection bias?\*\*



The system implements both \*\*time-series momentum\*\* and \*\*cross-sectional momentum\*\*, with monthly portfolio construction, inverse-volatility weighting, transaction costs, benchmark comparison, parameter robustness tests, chronological holdout analysis, regime analysis and walk-forward model selection.



\---



\## Overview



The research pipeline covers:



1\. Historical market-data ingestion

2\. PostgreSQL storage and SQL feature engineering

3\. Time-series and cross-sectional momentum signals

4\. Inverse-volatility portfolio construction

5\. Monthly rebalancing with look-ahead protection

6\. Transaction-cost modelling

7\. Performance and benchmark analysis

8\. Parameter and cost sensitivity

9\. Portfolio-concentration analysis

10\. Chronological holdout testing

11\. Market-regime analysis

12\. Parameter-selection bias analysis

13\. Rolling walk-forward model selection

14\. Automated testing and reproducible result generation



\---



\## Technology



\- \*\*Python\*\* — research, portfolio construction, backtesting and analytics

\- \*\*PostgreSQL\*\* — structured market-data storage

\- \*\*SQL\*\* — return, volatility and momentum feature engineering

\- \*\*Docker\*\* — reproducible PostgreSQL environment

\- \*\*pandas / NumPy\*\* — data manipulation and numerical analysis

\- \*\*Matplotlib\*\* — performance visualisation

\- \*\*SQLAlchemy / psycopg\*\* — Python/PostgreSQL integration

\- \*\*pytest\*\* — automated strategy and backtest validation

\- \*\*yfinance\*\* — historical ETF market-data source



\---



\## Asset Universe



The research uses 16 liquid ETF proxies across several asset classes.



| Asset Class          | Instruments             |

| -------------------- | ----------------------- |

| US / Global Equities | SPY, QQQ, IWM, EFA, EEM |

| Real Estate          | VNQ                     |

| Government Bonds     | SHY, IEF, TLT           |

| Commodities          | GLD, SLV, DBC, USO      |

| FX Proxies           | UUP, FXE, FXY           |



The main backtest runs from approximately \*\*2008 to 2026\*\*, depending on the availability of the required trailing momentum history.



\---



\## Strategy Design



\### Time-Series Momentum



Each asset is evaluated against its own historical trend.



For the primary 12-1 specification:



\- positive momentum → long

\- negative momentum → short

\- zero momentum → neutral



The signal measures price performance from approximately 12 months ago to one month ago.



\---



\### Cross-Sectional Momentum



Assets are ranked against the rest of the universe each month.



\- top 25% → long

\- bottom 25% → short

\- middle 50% → neutral



The portfolio allocates 50% gross exposure to the long side and 50% to the short side.



\---



\## Benchmark Comparison



The momentum strategies are compared with three passive benchmarks:



\- SPY

\- a monthly rebalanced 60/40 SPY/IEF portfolio

\- an equal-weight portfolio across the 16-asset universe



Across the full sample, the passive benchmarks generally deliver stronger absolute and risk-adjusted returns. However, the time-series momentum strategy exhibits substantially lower volatility and maximum drawdown than passive equity exposure.



This comparison is therefore used to assess the strategy's risk characteristics rather than to claim that momentum outperforms passive investing.



!\[Strategy and Benchmark Equity Curves](results/figures/equity\_curves.png)



!\[Strategy Drawdowns](results/figures/drawdowns.png)



\---



\## Portfolio Construction



Positions are sized using \*\*inverse realised volatility\*\*:



\- lower-volatility assets receive larger nominal allocations

\- higher-volatility assets receive smaller allocations



The baseline portfolio is normalised to approximately 100% gross exposure.



Additional robustness analysis tests \*\*5% and 10% volatility floors\*\* to investigate whether inverse-volatility sizing creates excessive concentration in very low-volatility assets.



\---



\## Look-Ahead Protection



Signals formed at the end of month `t` are only applied to returns in month `t + 1`.



For example:



```text

January market information

&#x20;       ↓

January month-end signal

&#x20;       ↓

February portfolio

&#x20;       ↓

February realised returns

