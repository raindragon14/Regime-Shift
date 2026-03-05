"""
Quant Project - VIX Panic Correlation Analysis
===============================================
Menganalisis korelasi antara BTC dan Emas (GLD) ketika
Indeks VIX menembus zona panic (>30).
"""

from src.config import load_config
from src.data_fetcher import fetch_market_data
from src.analysis import run_full_analysis
from src.visualization import generate_all_charts
