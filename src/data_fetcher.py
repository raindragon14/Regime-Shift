"""
Data Fetcher
=============
Modul untuk menarik data pasar dari Yahoo Finance
dengan retry logic untuk menangani kegagalan intermiten.
"""

import logging
import time
from typing import Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger("quant_project.data_fetcher")


def fetch_market_data(
    tickers: list[str],
    start_date: str,
    end_date: Optional[str] = None,
    max_retries: int = 3,
) -> pd.DataFrame:
    """
    Menarik data historis harga penutupan dari Yahoo Finance.

    Parameters
    ----------
    tickers : list[str]
        Daftar ticker symbol, contoh: ["BTC-USD", "GLD", "^VIX"].
    start_date : str
        Tanggal awal dalam format YYYY-MM-DD.
    end_date : str, optional
        Tanggal akhir. Default None (sampai hari ini).
    max_retries : int
        Jumlah percobaan ulang jika download gagal.

    Returns
    -------
    pd.DataFrame
        DataFrame dengan kolom per-ticker (harga penutupan).
    """
    logger.info("Memulai penarikan data untuk: %s", ", ".join(tickers))

    for attempt in range(1, max_retries + 1):
        try:
            raw = yf.download(tickers, start=start_date, end=end_date)

            if raw.empty:
                raise ValueError("Download mengembalikan DataFrame kosong")

            # Menangani format multi-index dari yfinance
            if isinstance(raw.columns, pd.MultiIndex):
                if "Adj Close" in raw.columns.get_level_values(0):
                    df = raw["Adj Close"]
                else:
                    df = raw["Close"]
            else:
                df = raw[["Close"]].rename(columns={"Close": tickers[0]})

            # Bersihkan missing values
            initial_rows = len(df)
            df = df.dropna()
            dropped = initial_rows - len(df)

            if df.empty:
                raise ValueError("Data kosong setelah membersihkan missing values")

            logger.info(
                "Data berhasil ditarik: %d baris (%d baris dihapus karena NaN)",
                len(df), dropped,
            )
            return df

        except Exception as e:
            if attempt < max_retries:
                wait = attempt * 3
                logger.warning(
                    "Percobaan %d/%d gagal: %s. Menunggu %d detik...",
                    attempt, max_retries, str(e), wait,
                )
                time.sleep(wait)
            else:
                logger.error("Gagal menarik data setelah %d percobaan: %s", max_retries, str(e))
                raise

    raise ValueError("Unexpected: gagal melewati semua percobaan")
