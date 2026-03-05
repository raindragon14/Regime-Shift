"""
Quant Project v2.0 - Regime Shift Analysis
============================================
Pipeline:
  1. Config & Logging
  2. Fetch Data (BTC, GLD, VIX, QQQ, SPY)
  3. H1: VIX-Panic Correlation
  4. H2: Multi-Asset Regime Shift
  5. H3: Event Study (Abnormal Returns)
  6. Beta Stress Test
  7. Generate All Charts
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import load_config, setup_logging, ensure_output_dir
from src.data_fetcher import fetch_market_data
from src.analysis import (
    run_full_analysis,
    run_regime_analysis,
    run_event_study,
    run_beta_stress_test,
)
from src.visualization import generate_all_charts


def main() -> None:
    """Menjalankan seluruh pipeline analisis v2.0."""

    # ── 1. Config & Logging ──────────────────────────────────
    config = load_config()
    logger = setup_logging(config)
    output_dir = ensure_output_dir(config)

    logger.info("=" * 65)
    logger.info("QUANT PROJECT v2.0 — Regime Shift Analysis")
    logger.info("=" * 65)

    # ── 2. Fetch Data ────────────────────────────────────────
    logger.info("[STEP 1/6] Menarik data pasar...")
    prices = fetch_market_data(
        tickers=config["data"]["tickers"],
        start_date=config["data"]["start_date"],
        end_date=config["data"].get("end_date"),
    )
    logger.info("Pratinjau data:\n%s", prices.tail().to_string())

    # ── 3. H1: VIX-Panic Correlation ────────────────────────
    logger.info("[STEP 2/6] H1: VIX-Panic Correlation...")
    log_returns, rolling_corr, h1_result = run_full_analysis(prices, config)

    # ── 4. H2: Multi-Asset Regime Shift ─────────────────────
    logger.info("[STEP 3/6] H2: Multi-Asset Regime Shift...")
    regime_result = run_regime_analysis(prices, config)

    # ── 5. H3: Event Study ──────────────────────────────────
    logger.info("[STEP 4/6] H3: Event Study (Abnormal Returns)...")
    event_results = run_event_study(prices, config)

    # ── 6. Beta Stress Test ─────────────────────────────────
    logger.info("[STEP 5/6] Beta Stress Test (VIX-Conditional Beta)...")
    beta_results = run_beta_stress_test(prices, config)

    # ── 7. Generate All Charts ──────────────────────────────
    logger.info("[STEP 6/6] Membuat visualisasi...")
    generate_all_charts(
        prices=prices,
        log_returns=log_returns,
        rolling_corr=rolling_corr,
        config=config,
        output_dir=output_dir,
        regime_result=regime_result,
        event_results=event_results,
        beta_results=beta_results,
    )

    # ── Summary ─────────────────────────────────────────────
    logger.info("=" * 65)
    logger.info("RINGKASAN HASIL")
    logger.info("-" * 65)

    # H1
    logger.info("[H1] VIX-Panic Correlation")
    logger.info("  Normal : %d hari | Avg Corr: %.4f",
                h1_result.normal_days, h1_result.avg_corr_normal)
    logger.info("  Panic  : %d hari | Avg Corr: %.4f",
                h1_result.panic_days, h1_result.avg_corr_panic)
    logger.info("  >> H1: %s", "TERBUKTI" if h1_result.is_proven else "BELUM TERBUKTI")

    # H2
    logger.info("[H2] Regime Shift")
    logger.info("  Avg Corr BTC-QQQ: %.4f", regime_result.avg_corr_risk_on)
    logger.info("  Avg Corr BTC-GLD: %.4f", regime_result.avg_corr_safe_haven)
    logger.info("  Crossovers: %d", len(regime_result.crossover_dates))

    # H3
    logger.info("[H3] Event Study")
    for evt in event_results.events:
        sig = "***" if evt.is_significant else ""
        logger.info("  %s: CAR=%.2f%%, p=%.4f %s",
                    evt.name, evt.car * 100, evt.p_value, sig)

    # Beta
    logger.info("[Beta Stress]")
    for b in beta_results:
        logger.info("  %-10s: Beta=%.3f (n=%d)", b.regime_name, b.beta, b.n_observations)

    logger.info("-" * 65)
    logger.info("Grafik tersimpan di: %s", output_dir.resolve())
    logger.info("=" * 65)


if __name__ == "__main__":
    main()
