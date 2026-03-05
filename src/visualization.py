"""
Visualization Module v2.0
==========================
Grafik untuk semua hipotesis:
- H1: Rolling Correlation + VIX Overlay, Price Overlay, Scatter
- H2: Dual Rolling Correlation (Regime Shift)
- H3: Event Study CAR
- Beta Stress: Conditional Beta Bar Chart
"""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns

from src.analysis import (
    RegimeShiftResult,
    EventStudyResults,
    BetaStressResult,
)

logger = logging.getLogger("quant_project.visualization")

# --- Style Global ---
sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams.update({
    "figure.figsize": (14, 6),
    "figure.dpi": 150,
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})


# =========================================================
# H1 Charts
# =========================================================

def plot_rolling_correlation(
    rolling_corr: pd.Series,
    vix: pd.Series,
    vix_threshold: float,
    output_path: Path,
) -> None:
    """H1: Rolling correlation BTC-GLD dengan VIX panic zone overlay."""
    fig, ax1 = plt.subplots(figsize=(16, 7))

    ax1.plot(rolling_corr.index, rolling_corr.values,
             color="#2196F3", linewidth=1.2, label="30-Day Rolling Corr (BTC vs GLD)")
    ax1.axhline(y=0, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax1.axhline(y=0.5, color="#FF5722", linestyle="--", linewidth=0.8, alpha=0.6, label="Threshold (0.5)")
    ax1.set_ylabel("Rolling Correlation", color="#2196F3")
    ax1.set_ylim(-1, 1)
    ax1.tick_params(axis="y", labelcolor="#2196F3")

    aligned_vix = vix.reindex(rolling_corr.index).ffill()
    panic_mask = aligned_vix > vix_threshold
    if panic_mask.any():
        ax1.fill_between(
            rolling_corr.index, -1, 1,
            where=panic_mask, alpha=0.15, color="#F44336",
            label=f"VIX > {vix_threshold} (Panic Zone)",
        )

    ax2 = ax1.twinx()
    ax2.plot(aligned_vix.index, aligned_vix.values,
             color="#FF9800", linewidth=0.8, alpha=0.5, label="VIX Index")
    ax2.set_ylabel("VIX", color="#FF9800")
    ax2.tick_params(axis="y", labelcolor="#FF9800")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

    ax1.set_title("H1: Rolling Correlation (BTC vs GLD) dengan VIX Overlay")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Chart disimpan: %s", output_path)


def plot_vix_overlay(
    prices: pd.DataFrame,
    vix_col: str,
    vix_threshold: float,
    output_path: Path,
) -> None:
    """H1: Harga BTC & GLD dengan VIX panic zone."""
    fig, (ax_btc, ax_gld) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)

    # BTC
    ax_btc.plot(prices.index, prices["BTC-USD"], color="#F7931A", linewidth=1.2, label="BTC-USD")
    panic_mask = prices[vix_col] > vix_threshold
    ax_btc.fill_between(prices.index, prices["BTC-USD"].min(), prices["BTC-USD"].max(),
                        where=panic_mask, alpha=0.15, color="#F44336", label="VIX Panic Zone")
    ax_btc.set_ylabel("Price (USD)")
    ax_btc.legend(loc="upper left")
    ax_btc.set_title("Harga Aset dengan VIX Panic Zone Overlay")

    # GLD
    ax_gld.plot(prices.index, prices["GLD"], color="#FFD700", linewidth=1.2, label="GLD")
    ax_gld.fill_between(prices.index, prices["GLD"].min(), prices["GLD"].max(),
                        where=panic_mask, alpha=0.15, color="#F44336", label="VIX Panic Zone")
    ax_gld.set_ylabel("Price (USD)")
    ax_gld.legend(loc="upper left")

    ax_gld.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Chart disimpan: %s", output_path)


def plot_scatter_panic_vs_normal(
    log_returns: pd.DataFrame,
    vix: pd.Series,
    vix_threshold: float,
    output_path: Path,
) -> None:
    """H1: Scatter plot log returns BTC vs GLD, warna berdasarkan regime."""
    aligned = log_returns[["BTC-USD", "GLD"]].copy()
    aligned["VIX"] = vix.reindex(aligned.index)
    aligned = aligned.dropna()
    aligned["Regime"] = np.where(aligned["VIX"] > vix_threshold, "Panic (VIX > 30)", "Normal")

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = {"Normal": "#2196F3", "Panic (VIX > 30)": "#F44336"}

    for regime, color in colors.items():
        mask = aligned["Regime"] == regime
        ax.scatter(
            aligned.loc[mask, "BTC-USD"],
            aligned.loc[mask, "GLD"],
            c=color, alpha=0.4, s=15, label=regime, edgecolors="none",
        )

    ax.axhline(0, color="gray", linewidth=0.5)
    ax.axvline(0, color="gray", linewidth=0.5)
    ax.set_xlabel("Log Return BTC-USD")
    ax.set_ylabel("Log Return GLD")
    ax.set_title("H1: Scatter Plot Log Returns BTC vs GLD (Normal vs Panic)")
    ax.legend()
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Chart disimpan: %s", output_path)


# =========================================================
# H2 Chart: Dual Rolling Correlation (Regime Shift)
# =========================================================

def plot_dual_rolling_correlation(
    regime_result: RegimeShiftResult,
    events_config: list[dict],
    output_path: Path,
) -> None:
    """
    H2: Dual rolling correlation — BTC vs QQQ (risk-on) dan BTC vs GLD (safe haven)
    dalam satu chart, dengan vertical lines untuk event geopolitik.
    """
    fig, ax = plt.subplots(figsize=(16, 8))

    # Plot kedua correlation
    corr_ro = regime_result.corr_risk_on.dropna()
    corr_sh = regime_result.corr_safe_haven.dropna()

    ax.plot(corr_ro.index, corr_ro.values,
            color="#E91E63", linewidth=1.5, alpha=0.85, label="BTC vs QQQ (Risk-On)")
    ax.plot(corr_sh.index, corr_sh.values,
            color="#4CAF50", linewidth=1.5, alpha=0.85, label="BTC vs GLD (Safe Haven)")

    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)

    # Highlight crossover zones (BTC-GLD > BTC-QQQ)
    combined = pd.DataFrame({
        "risk_on": corr_ro,
        "safe_haven": corr_sh,
    }).dropna()
    if not combined.empty:
        safe_dominant = combined["safe_haven"] > combined["risk_on"]
        ax.fill_between(
            combined.index, -1, 1,
            where=safe_dominant, alpha=0.08, color="#4CAF50",
            label="GLD Dominant Zone",
        )

    # Event vertical lines
    event_colors = ["#FF5722", "#9C27B0", "#00BCD4", "#FF9800"]
    for i, event in enumerate(events_config):
        evt_date = pd.Timestamp(event["date"])
        color = event_colors[i % len(event_colors)]
        ax.axvline(x=evt_date, color=color, linestyle=":", linewidth=1.5, alpha=0.8)
        ax.text(evt_date, 0.95, f"  {event['name']}", transform=ax.get_xaxis_transform(),
                fontsize=7.5, color=color, rotation=90, va="top", ha="left")

    ax.set_ylim(-1, 1)
    ax.set_ylabel("30-Day Rolling Correlation")
    ax.set_title("H2: Regime Shift — BTC Correlation with QQQ (Risk-On) vs GLD (Safe Haven)")
    ax.legend(loc="lower left", fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Chart disimpan: %s", output_path)


# =========================================================
# H3 Chart: Event Study CAR
# =========================================================

def plot_event_study(
    event_results: EventStudyResults,
    output_path: Path,
) -> None:
    """
    H3: Chart Cumulative Abnormal Return (CAR) per event, dengan
    subplot per event menunjukkan daily AR dan cumulative AR.
    """
    n_events = len(event_results.events)
    if n_events == 0:
        logger.warning("Tidak ada event study results untuk diplot.")
        return

    fig, axes = plt.subplots(n_events, 1, figsize=(14, 4 * n_events), sharex=False)
    if n_events == 1:
        axes = [axes]

    colors_bar = {"pos": "#4CAF50", "neg": "#F44336"}

    for i, event in enumerate(event_results.events):
        ax = axes[i]
        ar = event.abnormal_returns

        # Bar chart untuk daily AR
        bar_colors = [colors_bar["pos"] if v >= 0 else colors_bar["neg"] for v in ar.values]
        x_labels = [d.strftime("%m-%d") for d in ar.index]
        x_pos = range(len(ar))

        ax.bar(x_pos, ar.values * 100, color=bar_colors, alpha=0.7, label="Daily AR (%)")

        # Cumulative AR line
        car_line = ar.cumsum() * 100
        ax_twin = ax.twinx()
        ax_twin.plot(x_pos, car_line.values, color="#2196F3", linewidth=2,
                     marker="o", markersize=4, label="CAR (%)")
        ax_twin.set_ylabel("CAR (%)", color="#2196F3")
        ax_twin.tick_params(axis="y", labelcolor="#2196F3")

        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels, rotation=45, fontsize=8)
        ax.set_ylabel("Abnormal Return (%)")
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.5)

        # Title with significance
        sig_text = "SIGNIFICANT" if event.is_significant else "not significant"
        ax.set_title(
            f"{event.name} ({event.date}) | CAR: {event.car*100:.2f}% | "
            f"t={event.t_stat:.2f}, p={event.p_value:.4f} [{sig_text}]",
            fontsize=11,
        )

        # Combined legend
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax_twin.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)

    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Chart disimpan: %s", output_path)


# =========================================================
# Beta Stress Chart: Conditional Beta Bar
# =========================================================

def plot_conditional_beta(
    beta_results: list[BetaStressResult],
    output_path: Path,
) -> None:
    """
    Conditional Beta BTC vs SPY di berbagai VIX regime.
    """
    if not beta_results:
        logger.warning("Tidak ada beta stress results untuk diplot.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    names = [f"{r.regime_name}\n(VIX {r.vix_range[0]}-{r.vix_range[1]})" for r in beta_results]
    betas = [r.beta for r in beta_results]
    n_obs = [r.n_observations for r in beta_results]

    # Color gradient: hijau (low beta) → merah (high beta)
    norm_betas = np.array(betas)
    colors = []
    for b in norm_betas:
        if b < 0.5:
            colors.append("#4CAF50")   # Green - defensive
        elif b < 1.0:
            colors.append("#FF9800")   # Orange - moderate
        elif b < 1.5:
            colors.append("#FF5722")   # Deep orange - aggressive
        else:
            colors.append("#F44336")   # Red - very aggressive

    bars = ax.bar(names, betas, color=colors, alpha=0.85, edgecolor="white", linewidth=1.5)

    # Add value labels
    for bar, beta, n in zip(bars, betas, n_obs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03,
                f"B={beta:.2f}\nn={n}", ha="center", fontsize=9)

    ax.axhline(y=1.0, color="#9E9E9E", linestyle="--", linewidth=1, label="Beta = 1 (Market)")
    ax.set_ylabel("Beta (BTC vs SPY)")
    ax.set_title("VIX-Conditional Beta: Sensitivitas BTC terhadap Pasar di Berbagai Regime")
    ax.legend(fontsize=9)
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Chart disimpan: %s", output_path)


# =========================================================
# Generate All Charts
# =========================================================

def generate_all_charts(
    prices: pd.DataFrame,
    log_returns: pd.DataFrame,
    rolling_corr: pd.Series,
    config: dict,
    output_dir: Path,
    regime_result: RegimeShiftResult = None,
    event_results: EventStudyResults = None,
    beta_results: list[BetaStressResult] = None,
) -> None:
    """Menghasilkan semua grafik sekaligus."""
    vix_col = [t for t in config["data"]["tickers"] if "VIX" in t.upper()][0]
    vix_threshold = config["analysis"]["vix_panic_threshold"]
    chart_names = config["output"]["charts"]

    logger.info("Mulai membuat grafik...")

    # --- H1 Charts ---
    plot_rolling_correlation(
        rolling_corr=rolling_corr,
        vix=prices[vix_col],
        vix_threshold=vix_threshold,
        output_path=output_dir / chart_names["rolling_correlation"],
    )
    plot_vix_overlay(
        prices=prices,
        vix_col=vix_col,
        vix_threshold=vix_threshold,
        output_path=output_dir / chart_names["vix_overlay"],
    )
    plot_scatter_panic_vs_normal(
        log_returns=log_returns,
        vix=prices[vix_col],
        vix_threshold=vix_threshold,
        output_path=output_dir / chart_names["scatter_regime"],
    )

    # --- H2 Chart ---
    if regime_result is not None:
        plot_dual_rolling_correlation(
            regime_result=regime_result,
            events_config=config.get("event_study", {}).get("events", []),
            output_path=output_dir / chart_names["dual_rolling_corr"],
        )

    # --- H3 Chart ---
    if event_results is not None:
        plot_event_study(
            event_results=event_results,
            output_path=output_dir / chart_names["event_study"],
        )

    # --- Beta Stress Chart ---
    if beta_results is not None:
        plot_conditional_beta(
            beta_results=beta_results,
            output_path=output_dir / chart_names["conditional_beta"],
        )

    logger.info("Semua grafik berhasil dibuat di: %s", output_dir)
