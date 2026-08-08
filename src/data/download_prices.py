import pandas as pd

from datetime import date

import yfinance as yf

from src.data.database import get_connection


START_DATE = "2007-01-01"
END_DATE = date.today().isoformat()


def get_instruments():
    query = """
        SELECT instrument_id, ticker
        FROM instruments
        ORDER BY instrument_id;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def download_prices(ticker):
    data = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=False,
        progress=False,
    )

    if data.empty:
        raise ValueError(f"No data returned for {ticker}")

    # yfinance may return MultiIndex columns even for one ticker
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.reset_index()

    return data


def insert_prices(instrument_id, data):
    query = """
        INSERT INTO prices (
            instrument_id,
            date,
            open,
            high,
            low,
            close,
            adjusted_close,
            volume
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (instrument_id, date) DO NOTHING;
    """

    rows = []

    for _, row in data.iterrows():
        rows.append(
            (
                instrument_id,
                row["Date"].date(),
                float(row["Open"]),
                float(row["High"]),
                float(row["Low"]),
                float(row["Close"]),
                float(row["Adj Close"]),
                int(row["Volume"]) if row["Volume"] == row["Volume"] else None,
            )
        )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, rows)


def main():
    instruments = get_instruments()

    for instrument_id, ticker in instruments:
        print(f"Downloading {ticker}...")

        data = download_prices(ticker)

        print(f"Downloaded {len(data)} rows for {ticker}")

        insert_prices(instrument_id, data)

        print(f"Inserted {ticker} into PostgreSQL")


if __name__ == "__main__":
    main()