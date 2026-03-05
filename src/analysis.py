"""
Analysis Module v2.0
=====================
Modul analisis lengkap untuk Regime Shift hypothesis:
- H1: VIX-Panic Rolling Correlation
- H2: Multi-Asset Regime Shift (BTC vs QQQ vs GLD)
- H3: Event Study (Abnormal Returns)
- Beta Stress Test (VIX-Conditional Beta)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

logger = logging.getLogger("quant_project.analysis")


# =========================================================
# Data Classes
# =========================================================

@dataclass
class HypothesisResult:
    """H1: Hasil evaluasi hipotesis VIX-Panic Correlation."""
    avg_corr_normal: float
    avg_corr_panic: float
    panic_days: int
    normal_days: int
    is_proven: bool
    vix_threshold: float
    corr_threshold: float


@dataclass
class RegimeShiftResult:
    """H2: Hasil analisis multi-asset regime shift."""
    corr_risk_on: pd.Series       # Rolling corr BTC vs QQQ
    corr_safe_haven: pd.Series    # Rolling corr BTC vs GLD
    crossover_dates: list         # Tanggal crossover
    avg_corr_risk_on: float
    avg_corr_safe_haven: float


@dataclass
class EventResult:
    """Hasil satu event study."""
    name: str
    date: str
    alpha: float
    beta: float
    abnormal_returns: pd.Series   # AR per hari di event window
    car: float                    # Cumulative Abnormal Return
    t_stat: float
    p_value: float
    is_significant: bool


@dataclass
class EventStudyResults:
    """H3: Kumpulan hasil event study."""
    events: list[EventResult] = field(default_factory=list)


@dataclass
class BetaStressResult:
    """Hasil Beta Stress Test per VIX regime."""
    regime_name: str
    vix_range: list
    beta: float
    alpha: float
    r_squared: float
    n_observations: int


# =========================================================
# Core Analysis Functions
# =========================================================

def compute_log_returns(prices: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Menghitung log return harian untuk kolom yang ditentukan."""
    log_ret = pd.DataFrame(index=prices.index)
    for col in columns:
        log_ret[col] = np.log(prices[col] / prices[col].shift(1))

    log_ret = log_ret.dropna()
    logger.info("Log returns dihitung untuk: %s (%d baris)", columns, len(log_ret))
    return log_ret


def compute_rolling_correlation(
    log_returns: pd.DataFrame,
    col_a: str,
    col_b: str,
    window: int = 30,
) -> pd.Series:
    """Menghitung rolling correlation antara dua kolom."""
    corr = log_returns[col_a].rolling(window=window).corr(log_returns[col_b])
    logger.info(
        "Rolling correlation (%d-hari) dihitung: %s vs %s",
        window, col_a, col_b,
    )
    return corr


# =========================================================
# H1: VIX-Panic Correlation
# =========================================================

def evaluate_hypothesis(
    rolling_corr: pd.Series,
    vix_values: pd.Series,
    vix_threshold: float = 30.0,
    corr_threshold: float = 0.5,
) -> HypothesisResult:
    """
    H1: Evaluasi apakah korelasi BTC-GLD meningkat saat VIX > threshold.
    """
    combined = pd.DataFrame({
        "correlation": rolling_corr,
        "vix": vix_values,
    }).dropna()

    panic = combined[combined["vix"] > vix_threshold]
    normal = combined[combined["vix"] <= vix_threshold]

    avg_panic = panic["correlation"].mean() if len(panic) > 0 else float("nan")
    avg_normal = normal["correlation"].mean() if len(normal) > 0 else float("nan")
    is_proven = avg_panic > corr_threshold

    result = HypothesisResult(
        avg_corr_normal=avg_normal,
        avg_corr_panic=avg_panic,
        panic_days=len(panic),
        normal_days=len(normal),
        is_proven=is_proven,
        vix_threshold=vix_threshold,
        corr_threshold=corr_threshold,
    )

    logger.info("=== H1: VIX-Panic Correlation ===")
    logger.info("Normal : %d hari | Avg Corr: %.4f", result.normal_days, result.avg_corr_normal)
    logger.info("Panic  : %d hari | Avg Corr: %.4f", result.panic_days, result.avg_corr_panic)
    logger.info("H1: %s", "TERBUKTI" if is_proven else "BELUM TERBUKTI")
    return result


# =========================================================
# H2: Multi-Asset Regime Shift
# =========================================================

def run_regime_analysis(
    prices: pd.DataFrame,
    config: dict,
) -> RegimeShiftResult:
    """
    H2: Menghitung rolling correlation BTC vs QQQ dan BTC vs GLD
    untuk mendeteksi regime shift.
    """
    regime_cfg = config["regime_analysis"]
    window = regime_cfg["rolling_window"]

    risk_on = regime_cfg["pairs"]["risk_on"]
    safe_haven = regime_cfg["pairs"]["safe_haven"]

    # Hitung log returns untuk semua aset
    all_assets = list(set([
        risk_on["asset"], risk_on["benchmark"],
        safe_haven["asset"], safe_haven["benchmark"],
    ]))
    log_ret = compute_log_returns(prices, all_assets)

    # Rolling correlations
    corr_risk_on = compute_rolling_correlation(
        log_ret, risk_on["asset"], risk_on["benchmark"], window
    )
    corr_safe_haven = compute_rolling_correlation(
        log_ret, safe_haven["asset"], safe_haven["benchmark"], window
    )

    # Detect crossover points (BTC-GLD > BTC-QQQ)
    combined = pd.DataFrame({
        "risk_on": corr_risk_on,
        "safe_haven": corr_safe_haven,
    }).dropna()

    diff = combined["safe_haven"] - combined["risk_on"]
    sign_changes = (diff.shift(1) * diff) < 0
    crossover_dates = combined.index[sign_changes].tolist()

    result = RegimeShiftResult(
        corr_risk_on=corr_risk_on,
        corr_safe_haven=corr_safe_haven,
        crossover_dates=crossover_dates,
        avg_corr_risk_on=corr_risk_on.mean(),
        avg_corr_safe_haven=corr_safe_haven.mean(),
    )

    logger.info("=== H2: Regime Shift Analysis ===")
    logger.info("Avg Corr BTC-QQQ (Risk-On) : %.4f", result.avg_corr_risk_on)
    logger.info("Avg Corr BTC-GLD (Safe Haven): %.4f", result.avg_corr_safe_haven)
    logger.info("Crossover events terdeteksi: %d", len(crossover_dates))
    return result


# =========================================================
# H3: Event Study (Abnormal Returns)
# =========================================================

def run_event_study(
    prices: pd.DataFrame,
    config: dict,
) -> EventStudyResults:
    """
    H3: Event Study untuk menghitung Abnormal Return BTC
    saat event geopolitik menggunakan Market Model.

    AR_t = R_BTC_t - (alpha + beta * R_SPY_t)
    """
    es_cfg = config["event_study"]
    target = es_cfg["target_asset"]
    benchmark = es_cfg["market_benchmark"]
    est_window = es_cfg["estimation_window"]
    evt_before = es_cfg["event_window_before"]
    evt_after = es_cfg["event_window_after"]

    # Log returns
    log_ret = compute_log_returns(prices, [target, benchmark])

    results = EventStudyResults()

    for event in es_cfg["events"]:
        event_name = event["name"]
        event_date = pd.Timestamp(event["date"])

        # Cari index terdekat (jika event date bukan trading day)
        if event_date not in log_ret.index:
            mask = log_ret.index >= event_date
            if not mask.any():
                logger.warning("Event '%s' di luar jangkauan data, dilewati.", event_name)
                continue
            event_date = log_ret.index[mask][0]

        event_idx = log_ret.index.get_loc(event_date)

        # Estimation window
        est_start = max(0, event_idx - evt_before - est_window)
        est_end = event_idx - evt_before
        if est_end - est_start < 30:
            logger.warning("Estimation window terlalu pendek untuk '%s', dilewati.", event_name)
            continue

        est_data = log_ret.iloc[est_start:est_end]

        # OLS regression: R_BTC = alpha + beta * R_SPY
        X = sm.add_constant(est_data[benchmark].values)
        y = est_data[target].values
        model = sm.OLS(y, X).fit()
        alpha = model.params[0]
        beta = model.params[1]

        # Event window
        evt_start = max(0, event_idx - evt_before)
        evt_end = min(len(log_ret), event_idx + evt_after + 1)
        evt_data = log_ret.iloc[evt_start:evt_end]

        # Abnormal returns
        expected = alpha + beta * evt_data[benchmark]
        ar = evt_data[target] - expected
        car = ar.sum()

        # T-test: apakah CAR signifikan secara statistik
        if len(ar) > 1 and ar.std() > 0:
            t_stat = car / (ar.std() * np.sqrt(len(ar)))
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=len(ar) - 1))
        else:
            t_stat = 0.0
            p_value = 1.0

        event_result = EventResult(
            name=event_name,
            date=str(event_date.date()),
            alpha=alpha,
            beta=beta,
            abnormal_returns=ar,
            car=car,
            t_stat=t_stat,
            p_value=p_value,
            is_significant=p_value < 0.05,
        )
        results.events.append(event_result)

        logger.info(
            "Event '%s' (%s): CAR=%.4f, t=%.2f, p=%.4f %s",
            event_name, event_date.date(), car, t_stat, p_value,
            "[SIGNIFICANT]" if event_result.is_significant else "",
        )

    logger.info("=== H3: Event Study selesai (%d events) ===", len(results.events))
    return results


# =========================================================
# Beta Stress Test (VIX-Conditional Beta)
# =========================================================

def run_beta_stress_test(
    prices: pd.DataFrame,
    config: dict,
) -> list[BetaStressResult]:
    """
    Menghitung conditional beta BTC vs SPY di berbagai VIX regime.
    Jika beta turun saat VIX naik, BTC makin "safe haven".
    """
    beta_cfg = config["beta_stress"]
    target = beta_cfg["target_asset"]
    benchmark = beta_cfg["market_benchmark"]
    regimes = beta_cfg["vix_regimes"]

    log_ret = compute_log_returns(prices, [target, benchmark])
    vix = prices["^VIX"].reindex(log_ret.index)
    log_ret["VIX"] = vix

    results = []
    logger.info("=== Beta Stress Test ===")

    for regime_name, vix_range in regimes.items():
        low, high = vix_range
        mask = (log_ret["VIX"] >= low) & (log_ret["VIX"] < high)
        regime_data = log_ret[mask]

        if len(regime_data) < 10:
            logger.warning("Regime '%s': terlalu sedikit data (%d baris)", regime_name, len(regime_data))
            continue

        X = sm.add_constant(regime_data[benchmark].values)
        y = regime_data[target].values
        model = sm.OLS(y, X).fit()

        result = BetaStressResult(
            regime_name=regime_name,
            vix_range=vix_range,
            beta=model.params[1],
            alpha=model.params[0],
            r_squared=model.rsquared,
            n_observations=len(regime_data),
        )
        results.append(result)

        logger.info(
            "Regime %-10s (VIX %d-%d): Beta=%.3f, Alpha=%.5f, R2=%.3f, N=%d",
            regime_name, low, high, result.beta, result.alpha,
            result.r_squared, result.n_observations,
        )

    return results


# =========================================================
# Full Pipeline (H1 — backward compatible)
# =========================================================

def run_full_analysis(
    prices: pd.DataFrame,
    config: dict,
) -> tuple[pd.DataFrame, pd.Series, HypothesisResult]:
    """
    Menjalankan pipeline H1 (backward compatible).
    """
    params = config["analysis"]
    tickers = config["data"]["tickers"]

    asset_cols = [t for t in tickers if "VIX" not in t.upper() and t in prices.columns]
    vix_col = [t for t in tickers if "VIX" in t.upper()][0]

    # Hanya gunakan BTC dan GLD untuk H1
    h1_assets = [a for a in asset_cols if a in ["BTC-USD", "GLD"]]

    log_ret = compute_log_returns(prices, h1_assets)

    rolling_corr = compute_rolling_correlation(
        log_ret,
        col_a=h1_assets[0],
        col_b=h1_assets[1],
        window=params["rolling_window"],
    )

    vix_aligned = prices[vix_col].reindex(log_ret.index)

    result = evaluate_hypothesis(
        rolling_corr=rolling_corr,
        vix_values=vix_aligned,
        vix_threshold=params["vix_panic_threshold"],
        corr_threshold=params["correlation_threshold"],
    )

    return log_ret, rolling_corr, result
