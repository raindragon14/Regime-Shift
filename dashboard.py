"""
Quant Project v2.0 — Presentation Dashboard
=============================================
Scrollable narrative presentation untuk juri lomba.
Menyampaikan riset Regime Shift secara storytelling.

Jalankan: python dashboard.py
Buka   : http://127.0.0.1:8050
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc

from src.config import load_config, setup_logging
from src.data_fetcher import fetch_market_data
from src.analysis import (
    compute_log_returns,
    compute_rolling_correlation,
    run_full_analysis,
    run_regime_analysis,
    run_event_study,
    run_beta_stress_test,
)


# =========================================================
# Load Data & Run Analysis
# =========================================================
config = load_config()
logger = setup_logging(config)

prices = fetch_market_data(
    tickers=config["data"]["tickers"],
    start_date=config["data"]["start_date"],
    end_date=config["data"].get("end_date"),
)

log_returns, rolling_corr, h1_result = run_full_analysis(prices, config)
regime_result = run_regime_analysis(prices, config)
event_results = run_event_study(prices, config)
beta_results = run_beta_stress_test(prices, config)


# =========================================================
# Design Tokens
# =========================================================
C = {
    "bg":       "#0b0b0f",
    "surface":  "#13131a",
    "border":   "rgba(255,255,255,0.06)",
    "text":     "#e8e8ed",
    "dim":      "#6b6b80",
    "accent":   "#5b8af5",
    "gold":     "#d4a843",
    "green":    "#3ecf8e",
    "red":      "#ef5350",
    "btc":      "#f7931a",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.02)",
    font=dict(color=C["dim"], family="Inter, system-ui, sans-serif", size=12),
    margin=dict(l=50, r=30, t=40, b=40),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showgrid=True, zeroline=False),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1a1a24", font_size=12),
)


# =========================================================
# Charts
# =========================================================

def chart_price_overview():
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.03)

    fig.add_trace(go.Scatter(
        x=prices.index, y=prices["BTC-USD"], name="BTC-USD",
        line=dict(color=C["btc"], width=1.5),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=prices.index, y=prices["GLD"], name="Gold (GLD)",
        line=dict(color=C["gold"], width=1.5), visible="legendonly",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=prices.index, y=prices["^VIX"], name="VIX",
        line=dict(color=C["red"], width=1), fill="tozeroy",
        fillcolor="rgba(239,83,80,0.06)",
    ), row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="rgba(239,83,80,0.4)",
                  annotation_text="Panic (30)", row=2, col=1,
                  annotation_font=dict(color=C["dim"], size=10))

    for event in config.get("event_study", {}).get("events", []):
        fig.add_vline(x=pd.Timestamp(event["date"]),
                      line_dash="dot", line_color="rgba(255,255,255,0.12)", line_width=1)

    fig.update_layout(**CHART_LAYOUT, height=420, showlegend=True,
                      legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"))
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1, gridcolor="rgba(255,255,255,0.04)")
    fig.update_yaxes(title_text="VIX", row=2, col=1, gridcolor="rgba(255,255,255,0.04)")
    return fig


def chart_regime_shift():
    all_assets = list(set(["BTC-USD", "QQQ", "GLD"]))
    lr = compute_log_returns(prices, all_assets)
    corr_qqq = compute_rolling_correlation(lr, "BTC-USD", "QQQ", 30)
    corr_gld = compute_rolling_correlation(lr, "BTC-USD", "GLD", 30)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=corr_qqq.index, y=corr_qqq.values, name="BTC vs QQQ (Risk-On)",
        line=dict(color="#e91e63", width=1.8),
    ))
    fig.add_trace(go.Scatter(
        x=corr_gld.index, y=corr_gld.values, name="BTC vs GLD (Safe Haven)",
        line=dict(color=C["green"], width=1.8),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.1)")

    for event in config.get("event_study", {}).get("events", []):
        evt_date = pd.Timestamp(event["date"])
        fig.add_vline(x=evt_date, line_dash="dot",
                      line_color="rgba(255,255,255,0.15)", line_width=1)
        fig.add_annotation(x=evt_date, y=0.92, yref="paper",
                           text=event["name"], showarrow=False,
                           font=dict(size=8, color=C["dim"]),
                           textangle=-90, xanchor="left")

    fig.update_layout(**CHART_LAYOUT, height=400, showlegend=True,
                      legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"),
                      yaxis=dict(title="Rolling Correlation (30d)", range=[-1, 1],
                                 gridcolor="rgba(255,255,255,0.04)"))
    return fig


def chart_event_study():
    if not event_results.events:
        return go.Figure()
    names = [e.name for e in event_results.events]
    cars = [e.car * 100 for e in event_results.events]
    colors = [C["green"] if c > 0 else C["red"] for c in cars]

    fig = go.Figure(go.Bar(
        x=names, y=cars, marker_color=colors,
        text=[f"{c:+.1f}%" for c in cars], textposition="outside",
        textfont=dict(size=14, color=C["text"]),
    ))
    fig.add_hline(y=0, line_color="rgba(255,255,255,0.1)")
    fig.update_layout(**CHART_LAYOUT, height=350, showlegend=False,
                      yaxis=dict(title="Cumulative Abnormal Return (%)",
                                 gridcolor="rgba(255,255,255,0.04)"))
    return fig


def chart_beta():
    if not beta_results:
        return go.Figure()
    names = [f"{r.regime_name}\n(VIX {r.vix_range[0]}-{r.vix_range[1]})" for r in beta_results]
    betas = [r.beta for r in beta_results]
    colors = [C["green"] if b < 0.8 else (C["gold"] if b < 1.2 else C["red"]) for b in betas]

    fig = go.Figure(go.Bar(
        x=names, y=betas, marker_color=colors,
        text=[f"{b:.2f}" for b in betas], textposition="outside",
        textfont=dict(size=14, color=C["text"]),
    ))
    fig.add_hline(y=1.0, line_dash="dash", line_color="rgba(255,255,255,0.2)",
                  annotation_text="Market (1.0)",
                  annotation_font=dict(color=C["dim"], size=10))
    fig.update_layout(**CHART_LAYOUT, height=350, showlegend=False,
                      yaxis=dict(title="Beta (BTC vs SPY)",
                                 range=[0, max(betas) * 1.35],
                                 gridcolor="rgba(255,255,255,0.04)"))
    return fig


# =========================================================
# Layout Helpers
# =========================================================

def section(children, bg=C["bg"], padv="80px"):
    return html.Section(children, className="fade-section", style={
        "backgroundColor": bg, "padding": f"{padv} 0",
        "maxWidth": "760px", "margin": "0 auto",
        "paddingLeft": "32px", "paddingRight": "32px",
    })


def section_label(text, color=C["accent"]):
    return html.Div(text, style={
        "fontSize": "11px", "fontWeight": "600",
        "letterSpacing": "3.5px", "textTransform": "uppercase",
        "color": color, "marginBottom": "20px",
        "fontFamily": "Inter, system-ui, sans-serif",
    })


def section_title(text):
    return html.H2(text, style={
        "fontSize": "34px", "fontWeight": "400",
        "fontFamily": "'DM Serif Display', Georgia, serif",
        "color": C["text"], "lineHeight": "1.25",
        "marginBottom": "28px", "marginTop": "0",
        "letterSpacing": "-0.3px",
    })


def paragraph(text):
    return html.P(text, style={
        "fontSize": "15.5px", "lineHeight": "1.9",
        "color": C["dim"], "marginBottom": "20px",
        "maxWidth": "640px",
        "fontWeight": "400",
        "letterSpacing": "0.1px",
    })


def divider():
    return html.Hr(style={
        "border": "none",
        "borderTop": f"1px solid {C['border']}",
        "margin": "0",
    })


def stat_row(items):
    """Row of stat numbers."""
    return html.Div([
        html.Div([
            html.Div(val, style={
                "fontSize": "38px", "fontWeight": "400",
                "fontFamily": "'DM Serif Display', Georgia, serif",
                "color": color, "lineHeight": "1",
                "fontVariantNumeric": "tabular-nums",
            }),
            html.Div(label, style={
                "fontSize": "12px", "color": C["dim"],
                "marginTop": "10px", "letterSpacing": "0.5px",
                "textTransform": "uppercase", "fontWeight": "500",
            }),
        ], style={"textAlign": "center", "flex": "1", "padding": "24px 0"})
        for val, label, color in items
    ], style={
        "display": "flex", "gap": "0",
        "borderTop": f"1px solid {C['border']}",
        "borderBottom": f"1px solid {C['border']}",
        "margin": "44px 0",
    })


def chart_container(figure):
    return html.Div([
        dcc.Graph(figure=figure, config={
            "displayModeBar": False, "scrollZoom": False,
        }),
    ], style={
        "backgroundColor": C["surface"],
        "borderRadius": "14px",
        "border": f"1px solid {C['border']}",
        "padding": "12px 8px", "marginTop": "36px", "marginBottom": "36px",
    })


def event_table():
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Event", style={"textAlign": "left", "padding": "14px 16px",
                                    "color": C["dim"], "fontSize": "11px",
                                    "letterSpacing": "1px", "textTransform": "uppercase",
                                    "fontWeight": "600"}),
            html.Th("Tanggal", style={"padding": "14px 16px", "color": C["dim"],
                                      "fontSize": "11px", "letterSpacing": "1px",
                                      "fontWeight": "600"}),
            html.Th("CAR", style={"padding": "14px 16px", "color": C["dim"],
                                  "fontSize": "11px", "letterSpacing": "1px",
                                  "fontWeight": "600"}),
            html.Th("Signifikansi", style={"padding": "14px 16px", "color": C["dim"],
                                           "fontSize": "11px", "letterSpacing": "1px",
                                           "fontWeight": "600"}),
        ], style={"borderBottom": f"1px solid {C['border']}"})),
        html.Tbody([
            html.Tr([
                html.Td(e.name, style={"padding": "14px 16px", "fontWeight": "500",
                                       "color": C["text"], "fontSize": "14px"}),
                html.Td(e.date, style={"padding": "14px 16px", "color": C["dim"],
                                       "fontSize": "14px"}),
                html.Td(f"{e.car*100:+.2f}%", style={
                    "padding": "14px 16px", "fontWeight": "600", "fontSize": "14px",
                    "color": C["green"] if e.car > 0 else C["red"],
                }),
                html.Td(f"p={e.p_value:.3f}", style={
                    "padding": "14px 16px", "fontSize": "14px",
                    "color": C["dim"],
                }),
            ], style={"borderBottom": f"1px solid {C['border']}"})
            for e in event_results.events
        ]),
    ], style={
        "width": "100%", "borderCollapse": "collapse",
        "backgroundColor": C["surface"],
        "borderRadius": "12px", "overflow": "hidden",
        "border": f"1px solid {C['border']}",
        "marginTop": "24px",
    })


def finding_card(number, title, body, accent=C["accent"]):
    return html.Div([
        html.Div([
            html.Span(f"0{number}", style={
                "fontSize": "52px", "fontWeight": "400",
                "fontFamily": "'DM Serif Display', Georgia, serif",
                "color": accent, "opacity": "0.1",
                "position": "absolute", "top": "-12px", "left": "0",
            }),
            html.H3(title, style={
                "fontSize": "17px", "fontWeight": "600",
                "color": C["text"], "marginBottom": "10px",
                "marginTop": "0", "position": "relative",
                "paddingLeft": "44px",
                "letterSpacing": "0.2px",
            }),
        ], style={"position": "relative"}),
        html.P(body, style={
            "fontSize": "14.5px", "lineHeight": "1.8",
            "color": C["dim"], "margin": "0",
        }),
    ], style={
        "borderLeft": f"2px solid {accent}",
        "paddingLeft": "24px", "marginBottom": "44px",
    })


# =========================================================
# App Layout
# =========================================================
app = Dash(
    __name__,
    title="Regime Shift Analysis",
    update_title=None,
)

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body {
            background: #0b0b0f;
            color: #e8e8ed;
            font-family: Inter, system-ui, -apple-system, sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
        ::selection { background: rgba(91,138,245,0.3); }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.12); }

        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(24px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .fade-section {
            animation: fadeUp 0.6s ease-out both;
        }

        blockquote { border: none; }
        table { border-spacing: 0; }
    </style>
</head>
<body>
    {%app_entry%}
    <footer> {%config%} {%scripts%} {%renderer%} </footer>
</body>
</html>
'''

app.layout = html.Div([

    # ── HERO ──────────────────────────────────────────────
    html.Div([
        html.Div([
            section_label("QUANTITATIVE RESEARCH", C["accent"]),
            html.H1("Membongkar Mitos Emas Digital", style={
                "fontSize": "52px", "fontWeight": "400",
                "fontFamily": "'DM Serif Display', Georgia, serif",
                "color": C["text"], "lineHeight": "1.15",
                "marginBottom": "24px",
                "maxWidth": "600px",
                "letterSpacing": "-0.5px",
            }),
            html.P(
                "Investigasi empiris terhadap hipotesis regime shift pada Bitcoin: "
                "Eksplorasi transisi arsitektur identitas dari rasio proxy risk-on "
                "menuju instrumen safe haven selama guncangan makro-geopolitik 2023–2026.",
                style={
                    "fontSize": "17px", "lineHeight": "1.75",
                    "color": C["dim"], "maxWidth": "520px",
                    "fontWeight": "400",
                },
            ),
        ], style={
            "maxWidth": "760px", "margin": "0 auto",
            "padding": "160px 32px 100px",
        }),
    ]),

    divider(),

    # ── LATAR BELAKANG ────────────────────────────────────
    section([
        section_label("KONTEKS PASAR"),
        section_title("Dinamika Kapitalisasi Ekstrem & Penetrasi Institusional"),
        paragraph(
            "Menginjak rentang kapitalisasi $1.3 triliun serta persetujuan alokasi ETF spot "
            "oleh institusi perbankan tier-1 (BlackRock, Fidelity), Bitcoin telah melampaui fase "
            "spekulasi ritel pinggiran. Keberadaannya kini tertanam di dalam portofolio global "
            "yang menuntut kuantifikasi manajemen risiko tingkat lanjut."
        ),
        paragraph(
            "Selama fluktuasi indeks ketakutan (VIX) era 2023–2026 yang diwarnai "
            "konflik geopolitik eskalatif — termasuk sengketa Israel-Hamas hingga penutupan Selat Hormuz — "
            "terdapat serangkaian anomali return: likuidasi aset (^VIX > 30) justru memicu "
            "agregasi ketahanan struktural dan sentimen akumulasi pada Bitcoin."
        ),
        stat_row([
            ("$1.3T", "Market Cap BTC", C["btc"]),
            ("4", "Intensitas Event", C["red"]),
            (f"{len(prices):,}", "Siklus Historis Data", C["accent"]),
        ]),
        paragraph(
            "Deviasi perilaku ini menantang paradigma tradisional. Evaluasi empiris ini "
            "dibutuhkan oleh para pengambil keputusan (CIOs, kuant, dan manajer risiko) "
            "untuk merekalibrasi proporsi hedging portofolio mereka menghadapi volatilitas militer."
        ),
    ]),

    divider(),

    # ── ANOMALI ───────────────────────────────────────────
    section([
        section_label("ANOMALI KLINIS"),
        section_title("Deviasi Terhadap Literatur Keuangan Klasik"),
        paragraph(
            "Berdasarkan postulat pasar tradisional, tekanan ekuilibrium massal ("
            "flight-to-liquidity) selayaknya mendepresiasi instrumen dengan beta > 1.0 "
            "secara simetris. Namun, pembacaan pasar menolak konsensus tersebut:"
        ),
        event_table(),
        paragraph(
            "Tren divergensi ini menggarisbawahi diskursus pokok: "
            "Apakah kejanggalan return ini merupakan signifikasi matematis pergeseran aset, "
            "atau keributan acak mikrostruktur pasar yang dipoles sebagai narasi Emas Digital?"
        ),
    ]),

    divider(),

    # ── DATA OVERVIEW ─────────────────────────────────────
    section([
        section_label("INFRASTRUKTUR DATA"),
        section_title("Trajektori Historis: Multivariat Aset & VIX"),
        paragraph(
            "Korpus panel mengutilisasi data historis berfrekuensi harian bagi konstelasi "
            "5 instrumen makro utama—proksi kapitalisasi QQQ, referensi index SPY, "
            "agregasi safe-haven GLD, aset kripto BTC-USD, dan implied volatility indikator ^VIX."
        ),
        chart_container(chart_price_overview()),
    ]),

    divider(),

    # ── METODOLOGI ────────────────────────────────────────
    section([
        section_label("KERANGKA KERJA (*FRAMEWORK*)"),
        section_title("Tripilar Konstruksi Metodologi Kuantitatif"),
        paragraph(
            "Observasi menghindari inferensi subjektif dan seluruhnya tersentralisasi "
            "pada pengujian algoritmik-statistik standar industri (*Hedge Fund & Investment Desk*)."
        ),

        finding_card(1,
            "Regresi OLS: Event Study Model",
            "Menerapkan Model Pasar (Market Model) untuk menceraikan trajektori expected return dari polusi pasar luas. "
            "Membedah simpangan abnormal return pasca-kejadian lewat window estimasi 120-hari bersignifikansi statistik (T-Test).",
            C["accent"],
        ),
        finding_card(2,
            "Crossover Multi-Asset Rolling Correlation",
            "Mengekstraksi fluktuasi transien matriks kovarians (30-hari rolling Pearson) "
            "untuk membaca pergeseran momentum korelasi absolut aset BTC versus ekuivalensi (QQQ & GLD).",
            C["green"],
        ),
        finding_card(3,
            "Dekomposisi Asymmetric VIX-Conditional Beta",
            "Memecah parameter kepekaan market (Beta) terhadap matriks disparitas rezim VIX (Normal hingga Panic). "
            "Kejatuhan parameter struktural (Beta disaggregation) merupakan proxy utama tendensi defensif sebuah instrumen.",
            C["gold"],
        ),
    ]),

    divider(),

    # ── TEMUAN 1: REGIME SHIFT ────────────────────────────
    section([
        section_label("EKSTRAKSI I", C["green"]),
        section_title("Deteksi Crossover: Evolusi Sifat Matriks Korelasi"),
        paragraph(
            "Profil korelasi dinamik merender visibilitas persinggungan antara dua proksi ekstrem: "
            "QQQ (distribusi Risk-On, merah) dan GLD (distribusi Hedging, hijau). Dominansi kuadran hijau "
            "menggambarkan peniruan profil Emas oleh Bitcoin."
        ),
        stat_row([
            ("0.36", "Avg Matrix BTC-QQQ", "#e91e63"),
            ("0.13", "Avg Matrix BTC-GLD", C["green"]),
            ("69", "Insidensi Crossover", C["accent"]),
        ]),
        chart_container(chart_regime_shift()),
        paragraph(
            "Identifikasi 69 lompatan fluktuatif sepanjang sampel (*micro-regime instances*) mengukuhkan tesis: "
            "Tipe pergeseran bersifat spasial intermiten, menolak asumsi adopsi permanen. "
            "BTC mengalami konversi ke 'emas sintetik' murni saat indeks guncangan menembus batas kritis asimetrinya."
        ),
    ]),

    divider(),

    # ── TEMUAN 2: EVENT STUDY ─────────────────────────────
    section([
        section_label("EKSTRAKSI II", C["green"]),
        section_title("Isolasi Event Market: Deviasi Abnormal Return"),
        paragraph(
            "Pabrikasi Model Regresi (OLS) secara empiris memvalidasi keberadaan 'return residual' absolut tak terjelaskan ("
            "Abnormal Return) selama masa observasi krisis militer tegang. Inflow kapital eksis secara numerik."
        ),
        chart_container(chart_event_study()),
        paragraph(
            f"Fase geopolitik terminal — Konflik Hormuz ({event_results.events[-1].date}) — "
            f"mempresentasikan nilai deviasi kumulatif (CAR) absolut sebesar {event_results.events[-1].car*100:+.1f}%. "
            "Kesenjangan performa komparatif terhadap krisis tahun 2024 menyiratkan adaptasi evolusionaris pasar "
            "terhadap proposisi utilitas 'Digital Gold'."
        ),
    ]),

    divider(),

    # ── TEMUAN 3: BETA STRESS ─────────────────────────────
    section([
        section_label("EKSTRAKSI III", C["green"]),
        section_title("Conditional Beta: Sensitivitas Kuadran Ekstrem"),
        paragraph(
            "Disagregasi elastisitas Beta sebagai kompas untuk memvalidasi asimetri kerentanan pasar. "
            "Penyusutan nilai (kembali mendekati nol) mencerminkan desinkronisasi BTC tehadap tekanan jual SPY."
        ),
        chart_container(chart_beta()),
        paragraph(
            f"Di bawah kondisi ekuilibrium sentimen (VIX 0–15), koefisien tertahan di {beta_results[0].beta:.2f}. "
            f"Namun lonjakan hingga {beta_results[1].beta:.2f} di ambang batas Normal VIX menegaskan bahwa instrumen "
            "masih menyerap polusi turbulensi portofolio secara agresif. Penurunan di fase panik (<1.20) "
            "sedang bertumbuh perlahan namun belum menyiratkan imunitas mutlak."
        ),
    ]),

    divider(),

    # ── KESIMPULAN ────────────────────────────────────────
    section([
        section_label("SINTESIS AKHIR", C["gold"]),
        section_title("Konklusi Empiris: Transisi Bertahap Skala Menengah"),
        html.Blockquote([
            html.P(
                "Eksosistem makro Bitcoin sedang bertumpu pada poros 'Transisi Bertahap'. "
                "Cetak biru korelatif membongkar fakta bahwa klaim 'Emas Digital' bukan sebuah oase absolut, "
                "tapi lebih mengarah pada rekayasa respons utilitas deflasioner yang kompartmental "
                "dan tervalidasi sangat nyata menembus rentang krisis militer abad ke-21.",
                style={
                    "fontSize": "21px", "lineHeight": "1.7",
                    "fontFamily": "'DM Serif Display', Georgia, serif",
                    "color": C["text"], "fontStyle": "italic",
                    "fontWeight": "400",
                },
            ),
        ], style={
            "borderLeft": f"3px solid {C['gold']}",
            "paddingLeft": "28px", "margin": "40px 0",
        }),

        finding_card(1,
            "Korelasi BTC-GLD meningkat saat kepanikan",
            f"Rata-rata korelasi naik dari {h1_result.avg_corr_normal:.3f} (normal) "
            f"ke {h1_result.avg_corr_panic:.3f} (panic) — meningkat, tapi belum melampaui 0.5.",
            C["accent"],
        ),
        finding_card(2,
            "Abnormal return positif di event terbaru",
            f"CAR {event_results.events[-1].car*100:+.1f}% di event 2026 vs "
            f"CAR {event_results.events[1].car*100:+.1f}% di event 2024. "
            "Tren menunjukkan pergeseran bertahap.",
            C["green"],
        ),
        finding_card(3,
            "Beta BTC masih > 1 saat panic",
            f"Beta {[b for b in beta_results if b.regime_name == 'panic'][0].beta:.2f} "
            "saat VIX > 30 — BTC tetap lebih volatile dari pasar saat krisis, "
            "mengindikasikan transisi belum selesai.",
            C["red"],
        ),
    ], padv="100px"),

    # ── FOOTER ────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div("Quant Project v2.0 — Regime Shift Analysis", style={
                "fontSize": "12px", "color": C["dim"],
                "letterSpacing": "0.5px",
            }),
            html.Div(
                f"Data: {prices.index[0].strftime('%b %Y')} — {prices.index[-1].strftime('%b %Y')} · "
                f"Source: Yahoo Finance · Python · Dash · Plotly",
                style={"fontSize": "11px", "color": "rgba(255,255,255,0.12)", "marginTop": "8px"},
            ),
        ], style={
            "maxWidth": "760px", "margin": "0 auto",
            "padding": "60px 32px", "textAlign": "center",
        }),
    ], style={"borderTop": f"1px solid {C['border']}"}),

], style={"backgroundColor": C["bg"]})


# =========================================================
# Run
# =========================================================
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  QUANT PROJECT — Presentation Dashboard")
    print("  Buka: http://127.0.0.1:8051")
    print("=" * 50 + "\n")
    app.run(debug=False, port=8051)
