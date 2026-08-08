from src.data.database import get_connection


INSTRUMENTS = [
    ("SPY", "SPDR S&P 500 ETF Trust", "equity", "USD", "yfinance"),
    ("QQQ", "Invesco QQQ Trust", "equity", "USD", "yfinance"),
    ("IWM", "iShares Russell 2000 ETF", "equity", "USD", "yfinance"),
    ("EFA", "iShares MSCI EAFE ETF", "equity", "USD", "yfinance"),
    ("EEM", "iShares MSCI Emerging Markets ETF", "equity", "USD", "yfinance"),
    ("VNQ", "Vanguard Real Estate ETF", "real_estate", "USD", "yfinance"),

    ("SHY", "iShares 1-3 Year Treasury Bond ETF", "bond", "USD", "yfinance"),
    ("IEF", "iShares 7-10 Year Treasury Bond ETF", "bond", "USD", "yfinance"),
    ("TLT", "iShares 20+ Year Treasury Bond ETF", "bond", "USD", "yfinance"),

    ("GLD", "SPDR Gold Shares", "commodity", "USD", "yfinance"),
    ("SLV", "iShares Silver Trust", "commodity", "USD", "yfinance"),
    ("DBC", "Invesco DB Commodity Index Tracking Fund", "commodity", "USD", "yfinance"),
    ("USO", "United States Oil Fund", "commodity", "USD", "yfinance"),

    ("UUP", "Invesco DB US Dollar Index Bullish Fund", "fx", "USD", "yfinance"),
    ("FXE", "Invesco CurrencyShares Euro Trust", "fx", "USD", "yfinance"),
    ("FXY", "Invesco CurrencyShares Japanese Yen Trust", "fx", "USD", "yfinance"),
]


def seed_instruments():
    query = """
        INSERT INTO instruments (
            ticker,
            name,
            asset_class,
            currency,
            source
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (ticker) DO NOTHING;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, INSTRUMENTS)

    print(f"Loaded {len(INSTRUMENTS)} instruments into PostgreSQL.")


if __name__ == "__main__":
    seed_instruments()