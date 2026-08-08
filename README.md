\# Multi-Asset Systematic Momentum Backtester



A systematic research and backtesting platform built with \*\*Python, SQL and PostgreSQL\*\* to evaluate momentum strategies across a diversified multi-asset ETF universe.



The project investigates:



> \*\*How robust is momentum across asset classes after accounting for transaction costs, portfolio risk, parameter uncertainty and strategy-selection bias?\*\*



Rather than optimising for the strongest historical backtest, the project focuses on whether results remain credible after introducing realistic implementation costs, alternative parameter choices, chronological testing, market regimes and rolling walk-forward selection.



\---



\## Key Features



\- Historical price ingestion across \*\*16 liquid ETF proxies\*\*

\- PostgreSQL market-data storage

\- SQL-based return, volatility and momentum feature engineering

\- Time-series and cross-sectional momentum strategies

\- Inverse-volatility portfolio construction

\- Monthly rebalancing with explicit look-ahead protection

\- Transaction-cost modelling based on portfolio turnover

\- Passive benchmark comparison

\- Momentum-horizon robustness testing

\- Transaction-cost sensitivity analysis

\- Volatility-floor and portfolio-concentration analysis

\- Chronological holdout testing

\- Market-regime analysis

\- Strategy-selection bias analysis

\- Rolling five-year walk-forward model selection

\- Automated validation with `pytest`

\- Reproducible CSV and PNG result generation



\---



\## Research Design



The research is built around a deliberately simple question: does momentum remain economically meaningful when the backtest is subjected to progressively stricter validation?



The workflow is:



```text

Historical market data

&#x20;       ↓

PostgreSQL database

&#x20;       ↓

SQL feature engineering

&#x20;       ↓

Monthly momentum signals

&#x20;       ↓

Portfolio construction

&#x20;       ↓

Next-month implementation

&#x20;       ↓

Transaction costs

&#x20;       ↓

Performance analysis

&#x20;       ↓

Robustness / holdout / regimes

&#x20;       ↓

Selection-bias testing

&#x20;       ↓

Walk-forward analysis

```



The intention is not to produce the highest possible historical Sharpe ratio. The objective is to understand \*\*which results survive reasonable changes in assumptions and which do not\*\*.



\---



\## Technology



| Technology | Use |

|---|---|

| \*\*Python\*\* | Backtesting, portfolio construction, analytics and testing |

| \*\*PostgreSQL\*\* | Structured historical market-data storage |

| \*\*SQL\*\* | Daily returns, realised volatility and momentum features |

| \*\*Docker\*\* | Reproducible PostgreSQL environment |

| \*\*pandas / NumPy\*\* | Data manipulation and numerical analysis |

| \*\*Matplotlib\*\* | Equity-curve and drawdown visualisation |

| \*\*SQLAlchemy / psycopg\*\* | Python/PostgreSQL integration |

| \*\*pytest\*\* | Automated validation |

| \*\*yfinance\*\* | Historical ETF price data |

| \*\*PyYAML\*\* | Central strategy and robustness configuration |



\---



\## Asset Universe



The strategy is tested across \*\*16 ETF proxies\*\* representing several major asset classes.



| Asset Class | Instruments |

|---|---|

| US / Global Equities | SPY, QQQ, IWM, EFA, EEM |

| Real Estate | VNQ |

| Government Bonds | SHY, IEF, TLT |

| Commodities | GLD, SLV, DBC, USO |

| FX Proxies | UUP, FXE, FXY |



Using multiple asset classes allows the project to test whether momentum behaviour is broader than a single equity-market effect.



The main research sample begins in approximately \*\*2008\*\*, after allowing sufficient history for the longest momentum signal.



\---



\# Strategy Methodology



\## Momentum Signals



Three momentum horizons are tested:



\- \*\*3-1 month momentum\*\*

\- \*\*6-1 month momentum\*\*

\- \*\*12-1 month momentum\*\*



The final month is excluded from the return window to reduce exposure to short-term reversal effects.



The primary specification uses \*\*12-1 momentum\*\*.



SQL window functions calculate the momentum features directly from stored adjusted closing prices.



\---



\## Time-Series Momentum



Time-series momentum compares each asset with its own historical price trend.



For each asset:



```text

Momentum > 0  → Long

Momentum < 0  → Short

Momentum = 0  → Neutral

```



This answers:



> Has this individual asset been trending upward or downward over the selected historical window?



Position sizes are subsequently adjusted using inverse realised volatility.



\---



\## Cross-Sectional Momentum



Cross-sectional momentum compares each asset with the rest of the universe.



Each month, the 16 instruments are ranked by momentum.



The portfolio then takes:



\- the strongest \*\*four assets long\*\*

\- the weakest \*\*four assets short\*\*

\- the middle eight assets remain neutral



The long side receives approximately \*\*50% gross exposure\*\* and the short side approximately \*\*50% gross exposure\*\*, producing a portfolio with approximately:



```text

Gross exposure = 100%

Net exposure   = 0%

```



before subsequent return movements.



\---



\# Portfolio Construction



\## Inverse-Volatility Weighting



Portfolio allocations are scaled using annualised \*\*20-trading-day realised volatility\*\*.



Conceptually:



```text

Lower realised volatility

&#x20;       ↓

Higher inverse-volatility weight



Higher realised volatility

&#x20;       ↓

Lower inverse-volatility weight

```



This prevents the portfolio from allocating equal nominal capital to assets with substantially different historical risk.



Time-series positions are normalised so that total absolute portfolio exposure equals approximately 100%.



Cross-sectional long and short positions are normalised separately to approximately +50% and -50%.



\---



\## Volatility Floors



A weakness of unconstrained inverse-volatility weighting is that extremely low-volatility assets can receive disproportionately large weights.



The project therefore tests:



```text

No volatility floor

5% volatility floor

10% volatility floor

```



This is treated as a \*\*robustness test\*\*, rather than selecting whichever floor gives the strongest historical performance.



The analysis shows that volatility floors substantially reduce extreme concentration while leaving the broad performance characteristics of the strategy relatively stable.



\---



\# Look-Ahead Protection



A core requirement of the backtest is that information is only used after it becomes observable.



Signals formed using month-end information from month `t` are applied only during month `t + 1`.



For example:



```text

January market data

&#x20;       ↓

January month-end signal

&#x20;       ↓

February target portfolio

&#x20;       ↓

February realised returns

```



The strategy therefore does \*\*not\*\* apply January's month-end signal retrospectively to January returns.



This timing logic is also tested automatically.



\---



\# Transaction Costs



Transaction costs are calculated from changes in portfolio weights between monthly rebalances.



The baseline assumption is:



```text

10 basis points per dollar traded

```



The project also evaluates:



```text

0 bps

5 bps

10 bps

25 bps

50 bps

```



This makes it possible to distinguish a strategy that remains viable under moderate implementation friction from one whose historical results depend on effectively free trading.



Average monthly turnover is higher for the cross-sectional strategy than for the time-series strategy, making cross-sectional momentum more sensitive to transaction-cost assumptions.



\---



\# Benchmarks



The momentum strategies are compared against three passive portfolios:



\- \*\*SPY\*\*

\- \*\*60/40 SPY/IEF portfolio\*\*, rebalanced monthly

\- \*\*Equal-weight 16-asset portfolio\*\*



The objective is not simply to determine whether momentum produces a higher terminal value.



The comparison also considers:



\- annualised return

\- annualised volatility

\- Sharpe ratio

\- maximum drawdown



\---



\# Primary Results



The primary strategy specification uses:



```text

Momentum horizon:       12-1

Rebalancing:            Monthly

Position sizing:        Inverse volatility

Volatility floor:       None

Transaction costs:      10 bps

```



\## Momentum Strategy Performance



| Strategy | Cumulative Return | CAGR | Annualised Volatility | Sharpe | Max Drawdown |

|---|---:|---:|---:|---:|---:|

| Time-Series Momentum | 30.69% | 1.46% | 4.39% | 0.35 | -11.95% |

| Cross-Sectional Momentum | 59.21% | 2.55% | 11.01% | 0.28 | -28.95% |



The primary momentum strategies generate positive historical returns but do \*\*not\*\* outperform the passive benchmarks on long-run absolute or risk-adjusted return.



The time-series strategy does, however, operate at substantially lower realised volatility and maximum drawdown than passive equity exposure.



This is an important research result: the project does not selectively present the backtest as a market-beating trading strategy.



\---



\## Benchmark Performance



Over the common comparison period:



| Portfolio | Cumulative Return | CAGR | Annualised Volatility | Sharpe | Max Drawdown |

|---|---:|---:|---:|---:|---:|

| SPY | 685.49% | 11.80% | 19.77% | 0.66 | -51.48% |

| 60/40 SPY/IEF | 348.08% | 8.45% | 11.12% | 0.79 | -31.86% |

| Equal-Weight Multi-Asset | 168.31% | 5.49% | 10.76% | 0.55 | -33.19% |

| Time-Series Momentum | 30.69% | 1.46% | 4.39% | 0.35 | -11.95% |

| Cross-Sectional Momentum | 59.21% | 2.55% | 11.01% | 0.28 | -28.95% |



The momentum portfolios therefore provide different historical \*\*risk characteristics\*\*, but not superior full-sample returns.



\---



\## Equity Curves



!\[Strategy and Benchmark Equity Curves](results/figures/equity\_curves.png)



\---



\## Drawdowns



!\[Strategy Drawdowns](results/figures/drawdowns.png)



\---



\# Robustness Analysis



\## Momentum Horizon Sensitivity



At the baseline 10 bps transaction-cost assumption:



| Horizon | TS CAGR | TS Sharpe | CS CAGR | CS Sharpe |

|---|---:|---:|---:|---:|

| 3-1 | 0.93% | 0.23 | 1.35% | 0.18 |

| 6-1 | 0.89% | 0.22 | 0.92% | 0.14 |

| 12-1 | 1.46% | 0.35 | 2.55% | 0.28 |



All three parameterisations remain positive over the full sample, but the differences are large enough to demonstrate meaningful parameter sensitivity.



The 12-1 specification performs best historically, but this result is treated cautiously rather than as evidence that 12-1 is inherently optimal.



\---



\## Transaction-Cost Sensitivity



| Trading Cost | TS CAGR | TS Sharpe | CS CAGR | CS Sharpe |

|---|---:|---:|---:|---:|

| 0 bps | 1.91% | 0.45 | 3.38% | 0.36 |

| 5 bps | 1.68% | 0.40 | 2.96% | 0.32 |

| 10 bps | 1.46% | 0.35 | 2.55% | 0.28 |

| 25 bps | 0.79% | 0.20 | 1.32% | 0.17 |

| 50 bps | -0.31% | -0.05 | -0.70% | -0.01 |



Performance deteriorates progressively as implementation costs rise.



At very high transaction costs, both strategies lose their historical profitability.



This result is particularly relevant for cross-sectional momentum because its average portfolio turnover is higher.



\---



\## Portfolio Concentration



Without a volatility floor, inverse-volatility weighting occasionally creates highly concentrated portfolios.



For time-series momentum:



```text

Largest historical position, no floor: 79.28%

Largest historical position, 5% floor:  36.80%

Largest historical position, 10% floor: 22.55%

```



The volatility-floor tests therefore demonstrate that portfolio construction assumptions can materially change concentration even when headline strategy performance changes relatively little.



\---



\# Chronological Holdout



The sample is divided at \*\*1 January 2017\*\*.



```text

Earlier sample:    pre-2017

Later holdout:     2017 onward

```



The primary strategy parameters are then evaluated separately across the two periods.



\### Time-Series Momentum



| Period | CAGR | Sharpe | Max Drawdown |

|---|---:|---:|---:|

| Earlier | 1.44% | 0.31 | -11.95% |

| Later | 1.48% | 0.40 | -11.65% |



\### Cross-Sectional Momentum



| Period | CAGR | Sharpe | Max Drawdown |

|---|---:|---:|---:|

| Earlier | 3.11% | 0.29 | -28.95% |

| Later | 2.03% | 0.29 | -19.89% |



Neither strategy collapses in the later period.



However, this is described as a \*\*chronological or pseudo-out-of-sample holdout\*\*, not a pristine out-of-sample experiment, because the overall dataset was available during project development.



\---



\# Market-Regime Analysis



Performance is also evaluated across several economically distinct periods:



\- Global Financial Crisis and aftermath

\- Post-GFC expansion

\- COVID shock and recovery

\- Inflation and interest-rate shock

\- Recent market period



The results show substantial variation through time.



The momentum strategies do not consistently outperform passive benchmarks in every regime.



This reinforces the conclusion that full-sample averages can conceal significant changes in strategy behaviour across market environments.



\---



\# Strategy-Selection Bias



Backtests become less credible when many strategies are tested and only the strongest historical result is reported.



To investigate this, the project evaluates:



```text

3 momentum horizons

×

3 volatility-floor assumptions

=

9 parameter specifications

```



For each strategy family, the specification with the highest Sharpe ratio in the earlier sample is selected and then evaluated on the later sample.



\### Selected Time-Series Specification



```text

Earlier selection: 12-1 momentum, 5% volatility floor

Earlier Sharpe:    0.36

Later Sharpe:      0.31

```



\### Selected Cross-Sectional Specification



```text

Earlier selection: 12-1 momentum, no volatility floor

Earlier Sharpe:    0.29

Later Sharpe:      0.29

```



The selected specifications retain positive later-period performance, but this does not prove the absence of overfitting.



Instead, the experiment demonstrates how parameter selection should be separated from subsequent evaluation.



\---



\# Walk-Forward Analysis



The strongest test in the project is a rolling walk-forward procedure.



For each calendar year:



```text

Previous five years

&#x20;       ↓

Evaluate nine specifications

&#x20;       ↓

Select highest training Sharpe

&#x20;       ↓

Freeze selected parameters

&#x20;       ↓

Apply during next calendar year

&#x20;       ↓

Repeat

```



Importantly, portfolio turnover is calculated across specification changes, so switching from one selected model to another incurs the appropriate trading cost.



\## Corrected Walk-Forward Results



| Strategy | Cumulative Return | CAGR | Annualised Volatility | Sharpe | Max Drawdown |

|---|---:|---:|---:|---:|---:|

| Time-Series | 9.03% | 0.64% | 4.75% | 0.16 | -19.65% |

| Cross-Sectional | 36.39% | 2.31% | 9.07% | 0.30 | -26.69% |



Rolling optimisation materially weakens the time-series strategy.



The cross-sectional strategy is more stable.



This is one of the most important findings in the project: \*\*selecting historically optimal parameters does not necessarily improve future performance and can make it worse.\*\*



\---



\# Automated Tests



The project includes automated tests covering strategy construction and backtesting logic.



Current tests check that:



\- time-series gross exposure is correctly normalised

\- cross-sectional gross exposure is correctly normalised

\- cross-sectional net exposure is approximately zero

\- volatility floors reduce portfolio concentration

\- month-end signals are assigned only to the following holding month

\- transaction costs reduce strategy equity relative to a zero-cost run

\- generated returns are finite and within valid bounds

\- time-series signals match momentum direction

\- cross-sectional signals select the intended extremes

\- invalid momentum specifications raise errors



Run the test suite with:



```powershell

pytest -v

```



\---



\# Database Design



The project separates instrument metadata from historical price observations.



\## `instruments`



Stores information including:



```text

instrument\_id

ticker

name

asset\_class

currency

source

```



\## `prices`



Stores:



```text

instrument\_id

date

open

high

low

close

adjusted\_close

volume

```



The two tables are linked by `instrument\_id`.



\---



\## SQL Feature Engineering



The SQL layer creates reusable database views rather than recalculating all features independently inside each Python analysis.



The pipeline calculates:



\- daily adjusted-close returns

\- 20-trading-day annualised realised volatility

\- 3-1 momentum

\- 6-1 momentum

\- 12-1 momentum



For example, the momentum calculation uses lagged adjusted prices through PostgreSQL window functions.



This separates:



```text

Data storage

&#x20;   ↓

Feature calculation

&#x20;   ↓

Strategy logic

&#x20;   ↓

Portfolio analysis

```



and makes the research pipeline easier to inspect and reproduce.



\---



\# Project Structure



```text

multi-asset-momentum-backtester/

│

├── config/

│   └── settings.yaml

│

├── results/

│   ├── figures/

│   │   ├── drawdowns.png

│   │   └── equity\_curves.png

│   │

│   └── tables/

│       ├── chronological\_holdout.csv

│       ├── cost\_sensitivity.csv

│       ├── parameter\_robustness.csv

│       ├── performance.csv

│       ├── regime\_analysis.csv

│       ├── selection\_bias.csv

│       ├── volatility\_floor\_sensitivity.csv

│       ├── walk\_forward\_cross\_sectional\_selections.csv

│       ├── walk\_forward\_summary.csv

│       └── walk\_forward\_time\_series\_selections.csv

│

├── sql/

│   ├── features.sql

│   ├── momentum\_features.sql

│   └── schema.sql

│

├── src/

│   ├── analytics/

│   │   ├── benchmarks.py

│   │   ├── cost\_sensitivity.py

│   │   ├── out\_of\_sample.py

│   │   ├── output.py

│   │   ├── performance.py

│   │   ├── plots.py

│   │   ├── regime\_analysis.py

│   │   ├── robustness.py

│   │   ├── selection\_bias.py

│   │   ├── volatility\_floor\_sensitivity.py

│   │   └── walk\_forward.py

│   │

│   ├── backtest/

│   │   ├── costs.py

│   │   └── engine.py

│   │

│   ├── data/

│   │   ├── database.py

│   │   ├── download\_prices.py

│   │   └── seed\_instruments.py

│   │

│   ├── portfolio/

│   │   └── weights.py

│   │

│   ├── signals/

│   │   └── momentum.py

│   │

│   └── config.py

│

├── tests/

│   ├── test\_backtest.py

│   ├── test\_portfolio.py

│   └── test\_signals.py

│

├── .env.example

├── .gitignore

├── docker-compose.yml

├── generate\_results.py

├── pytest.ini

├── requirements.txt

└── README.md

```



\---



\# Getting Started



The following instructions reproduce the project on \*\*Windows using PowerShell\*\*.



\## Prerequisites



Install:



\- Python 3.13

\- Git

\- Docker Desktop



Docker Desktop must be running before the PostgreSQL container can start.



\---



\## 1. Clone the Repository



```powershell

git clone https://github.com/jasperw599/multi-asset-momentum-backtester.git

cd multi-asset-momentum-backtester

```



\---



\## 2. Create a Virtual Environment



```powershell

python -m venv .venv

```



Activate it:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



Install the required Python packages:



```powershell

pip install -r requirements.txt

```



\---



\## 3. Configure Environment Variables



Create your local `.env` file from the supplied template:



```powershell

Copy-Item .env.example .env

```



Open it:



```powershell

notepad .env

```



The template contains:



```text

POSTGRES\_USER=momentum\_user

POSTGRES\_PASSWORD=your\_password\_here

POSTGRES\_DB=momentum\_db

POSTGRES\_PORT=5432

```



Replace:



```text

your\_password\_here

```



with a local PostgreSQL password of your choice.



The real `.env` file is excluded from Git and should not be committed.



\---



\## 4. Start PostgreSQL



Start the database container:



```powershell

docker compose up -d

```



Check that it is running:



```powershell

docker ps

```



The container should appear as:



```text

momentum-postgres

```



\---



\## 5. Create the Database Schema



Run:



```powershell

Get-Content .\\sql\\schema.sql |

docker exec -i momentum-postgres psql -U momentum\_user -d momentum\_db

```



This creates the core database tables and indexes.



\---



\## 6. Seed the Instrument Universe



Run:



```powershell

python -m src.data.seed\_instruments

```



This inserts the 16 ETF instruments used by the project.



\---



\## 7. Download Historical Prices



Run:



```powershell

python -m src.data.download\_prices

```



Historical prices are downloaded through `yfinance` and inserted into PostgreSQL.



Because market data changes through time, newly generated results may differ slightly from the committed research outputs.



\---



\## 8. Create the SQL Feature Views



First create the daily-return view:



```powershell

Get-Content .\\sql\\features.sql |

docker exec -i momentum-postgres psql -U momentum\_user -d momentum\_db

```



Then create the momentum and volatility feature view:



```powershell

Get-Content .\\sql\\momentum\_features.sql |

docker exec -i momentum-postgres psql -U momentum\_user -d momentum\_db

```



The second view depends on the daily-return view, so these commands should be run in this order.



\---



\## 9. Run the Tests



```powershell

pytest -v

```



A successful setup should complete the test suite without failures.



\---



\## 10. Generate Research Results



Run:



```powershell

python generate\_results.py

```



This runs:



```text

performance

parameter robustness

cost sensitivity

volatility-floor sensitivity

chronological holdout

regime analysis

selection-bias analysis

walk-forward analysis

```



and writes generated tables into:



```text

results/tables/

```



\---



\## 11. Generate Figures



Run:



```powershell

python -m src.analytics.plots

```



The generated PNG files are written to:



```text

results/figures/

```



\---



\# Configuration



Core research settings are centralised in:



```text

config/settings.yaml

```



The configuration contains the baseline strategy and robustness assumptions, including:



```yaml

strategy:

&#x20; momentum\_column: momentum\_12\_1

&#x20; transaction\_cost\_bps: 10

&#x20; volatility\_floor: null



backtest:

&#x20; trading\_days\_per\_year: 252



robustness:

&#x20; momentum\_columns:

&#x20;   - momentum\_3\_1

&#x20;   - momentum\_6\_1

&#x20;   - momentum\_12\_1



&#x20; transaction\_cost\_bps:

&#x20;   - 0

&#x20;   - 5

&#x20;   - 10

&#x20;   - 25

&#x20;   - 50



&#x20; volatility\_floors:

&#x20;   - null

&#x20;   - 0.05

&#x20;   - 0.10



walk\_forward:

&#x20; lookback\_years: 5

```



Centralising these values helps prevent different analysis modules from silently using inconsistent assumptions.



\---



\# Running Individual Analyses



Each analysis can also be run independently.



\### Primary performance



```powershell

python -m src.analytics.performance

```



\### Parameter robustness



```powershell

python -m src.analytics.robustness

```



\### Transaction-cost sensitivity



```powershell

python -m src.analytics.cost\_sensitivity

```



\### Volatility-floor sensitivity



```powershell

python -m src.analytics.volatility\_floor\_sensitivity

```



\### Chronological holdout



```powershell

python -m src.analytics.out\_of\_sample

```



\### Regime analysis



```powershell

python -m src.analytics.regime\_analysis

```



\### Selection-bias analysis



```powershell

python -m src.analytics.selection\_bias

```



\### Walk-forward analysis



```powershell

python -m src.analytics.walk\_forward

```



\---



\# Generated Outputs



The repository includes generated research outputs so the results can be inspected without rerunning the full database pipeline.



\## Tables



```text

results/tables/

├── chronological\_holdout.csv

├── cost\_sensitivity.csv

├── parameter\_robustness.csv

├── performance.csv

├── regime\_analysis.csv

├── selection\_bias.csv

├── volatility\_floor\_sensitivity.csv

├── walk\_forward\_cross\_sectional\_selections.csv

├── walk\_forward\_summary.csv

└── walk\_forward\_time\_series\_selections.csv

```



\## Figures



```text

results/figures/

├── drawdowns.png

└── equity\_curves.png

```



\---



\# Interpretation



The main conclusion of the project is \*\*not\*\* that momentum produced exceptional historical returns.



Instead, the research demonstrates several broader points:



1\. Momentum remains positive across several reasonable parameter choices, but performance is parameter-sensitive.

2\. Transaction costs materially weaken results.

3\. Inverse-volatility weighting can produce severe concentration without additional controls.

4\. The primary strategy remains positive in a later chronological sample.

5\. Strategy behaviour varies substantially across market regimes.

6\. Historical parameter rankings are unstable.

7\. Rolling optimisation can reduce rather than improve realised strategy performance.

8\. Backtest credibility depends as much on validation methodology as on headline historical returns.



The research therefore emphasises \*\*robustness, implementation realism and model-selection discipline\*\* rather than maximising an in-sample performance statistic.



\---



\# Limitations



This project intentionally uses a relatively transparent research design, but several limitations remain.



\### ETF proxies



The universe uses ETFs rather than futures, institutional total-return indices or directly traded spot instruments.



ETF structure can introduce tracking error, management fees and instrument-specific behaviour.



\### Historical data source



Price data is downloaded through `yfinance`.



Historical datasets can be revised and may not exactly reproduce institutional market-data feeds.



\### Transaction costs



Trading costs are represented using fixed basis-point assumptions.



The model does not explicitly estimate:



\- bid-ask spread variation

\- market impact

\- short-borrow fees

\- financing costs

\- liquidity constraints



\### Short positions



The backtest assumes short exposure can be obtained whenever required.



Real implementation could face instrument-specific borrowing constraints and costs.



\### Risk-free rate



The reported Sharpe ratios use a zero risk-free rate.



\### Portfolio risk model



Inverse realised volatility is used for position sizing, but the strategy does not implement a full covariance-based portfolio optimiser.



\### Survivorship and instrument selection



The ETF universe is fixed for the research exercise and does not represent a fully investable historical universe selected independently at every point in time.



\### Chronological holdout



The post-2017 sample is a useful chronological test but is not described as completely untouched out-of-sample data because the full dataset was visible during development.



\### Model-selection bias



Testing several parameter configurations inherently creates a risk of research overfitting.



The selection-bias and walk-forward experiments reduce this problem but cannot eliminate it completely.



\### Future performance



All reported figures are historical backtest results and should not be interpreted as forecasts of future returns.



\---



\# Reproducibility Notes



To reproduce the committed analysis as closely as possible:



1\. use the dependency versions in `requirements.txt`

2\. use the PostgreSQL Docker configuration supplied in `docker-compose.yml`

3\. use the strategy settings in `config/settings.yaml`

4\. create the SQL views in the documented order

5\. run the automated tests before generating outputs

6\. run `generate\_results.py` without altering the baseline configuration



Historical market-data updates may still lead to small differences between newly generated results and the committed outputs.



\---



\# Disclaimer



This repository is an \*\*educational and research project\*\*.



It is not investment advice, does not represent a live trading strategy and does not claim that the historical results shown here are achievable in future markets.



Backtested performance is hypothetical and is subject to modelling assumptions, data limitations and implementation costs.

