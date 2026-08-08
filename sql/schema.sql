CREATE TABLE IF NOT EXISTS instruments (
    instrument_id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    asset_class VARCHAR(30) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    source VARCHAR(30) NOT NULL DEFAULT 'yfinance'
);

CREATE TABLE IF NOT EXISTS prices (
    instrument_id INTEGER NOT NULL
        REFERENCES instruments(instrument_id)
        ON DELETE CASCADE,

    date DATE NOT NULL,
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    adjusted_close DOUBLE PRECISION NOT NULL,
    volume BIGINT,

    PRIMARY KEY (instrument_id, date),

    CHECK (high >= low),
    CHECK (volume IS NULL OR volume >= 0)
);

CREATE INDEX IF NOT EXISTS idx_prices_date
ON prices(date);