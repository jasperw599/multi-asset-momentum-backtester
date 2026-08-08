CREATE OR REPLACE VIEW momentum_features AS

SELECT
    instrument_id,
    ticker,
    asset_class,
    date,
    adjusted_close,
    daily_return,

    -- 20-trading-day realised volatility, annualised
    STDDEV_SAMP(daily_return) OVER (
        PARTITION BY instrument_id
        ORDER BY date
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) * SQRT(252.0) AS volatility_20d,

    -- 3-1 month momentum
    LAG(adjusted_close, 21) OVER (
        PARTITION BY instrument_id
        ORDER BY date
    )
    /
    LAG(adjusted_close, 63) OVER (
        PARTITION BY instrument_id
        ORDER BY date
    ) - 1 AS momentum_3_1,

    -- 6-1 month momentum
    LAG(adjusted_close, 21) OVER (
        PARTITION BY instrument_id
        ORDER BY date
    )
    /
    LAG(adjusted_close, 126) OVER (
        PARTITION BY instrument_id
        ORDER BY date
    ) - 1 AS momentum_6_1,

    -- 12-1 month momentum
    LAG(adjusted_close, 21) OVER (
        PARTITION BY instrument_id
        ORDER BY date
    )
    /
    LAG(adjusted_close, 252) OVER (
        PARTITION BY instrument_id
        ORDER BY date
    ) - 1 AS momentum_12_1

FROM daily_returns;