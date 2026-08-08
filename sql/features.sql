CREATE OR REPLACE VIEW daily_returns AS

WITH lagged_prices AS (
    SELECT
        p.instrument_id,
        i.ticker,
        i.asset_class,
        p.date,
        p.adjusted_close,

        LAG(p.adjusted_close) OVER (
            PARTITION BY p.instrument_id
            ORDER BY p.date
        ) AS previous_adjusted_close

    FROM prices p
    JOIN instruments i
        ON p.instrument_id = i.instrument_id
)

SELECT
    instrument_id,
    ticker,
    asset_class,
    date,
    adjusted_close,
    previous_adjusted_close,

    adjusted_close / previous_adjusted_close - 1
        AS daily_return

FROM lagged_prices;