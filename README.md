🌐 **Language / Bahasa**: [🇬🇧 English](README.md) | [🇮🇩 Bahasa Indonesia](README.id.md)

# Debunking the Digital Gold Myth 🪙
**Quantitative Analysis of Bitcoin Regime Shifts During the 2023–2026 Geopolitical Crisis**

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Dash](https://img.shields.io/badge/dash-2.14+-teal.svg)
![Plotly](https://img.shields.io/badge/plotly-5.18+-purple.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> **Data Analytics Competition & Quantitative Research Portfolio Project**<br>
> An empirical investigation employing *Event Study*, *Rolling Correlation*, and *VIX-Conditional Beta* methodologies to test the Bitcoin *safe haven* narrative.

---

## 📌 Table of Contents
1. [Abstract](#abstract)
2. [Why This Matters](#why-this-matters)
3. [Hypotheses & Methodology](#hypotheses--methodology)
4. [Key Findings](#key-findings)
5. [Quick Start (Dashboard)](#quick-start)
6. [Repository Structure](#repository-structure)

---

## 📖 Exploratory Abstract

This quantitative study investigates the **regime-shift hypothesis** in the cryptocurrency asset class, specifically testing whether Bitcoin (BTC) is undergoing a fundamental transition from a high-risk speculative instrument (*risk-on proxy*) to a macroeconomic store of value (*safe haven*). The observation period is concentrated on the high-intensity geopolitical escalation window of 2023–2026, encompassing exogenous shocks such as the outbreak of the Israel-Hamas conflict, the Iran-Israel military strikes, and the partial restriction of the Strait of Hormuz maritime corridor.

Through the application of a tripartite industry-standard quantitative framework — comprising an **Event Study (OLS Market Model)** design, **Multi-Asset Rolling Correlation** computation, and **VIX-Conditional Beta** decomposition — we conclude that Bitcoin currently defies clean classification as either a pure *risk-on* or *safe haven* asset. The data empirically reveal a structure of **incremental, intermittent transition**: corrective correlation spikes toward gold instruments (GLD) are detected during global market panic phases, and persistently positive abnormal return accumulation is observed around the most recent events, accompanied by market beta coefficients that have not yet fully subdued (*Beta > 1.0*). The "Digital Gold" narrative is therefore not an established market axiom, but rather a **dynamic hypothesis actively being validated by global institutions amid geopolitical shocks.**

---

## 🏛️ Why This Research Matters

### 1. Paradigm Shift and Market Depth
With market capitalization breaching the psychological threshold of **$1.3 trillion** and the strategic catalyst of spot ETF product approvals by major market makers (e.g., BlackRock, Fidelity), Bitcoin has transcended the phase of "fringe retail speculation." The asset is now substantially embedded within global portfolio layers, demanding a far more rigorous and quantified approach to risk profiling.

### 2. Performance Anomalies Under Deflationary Shocks
Classical finance literature predicts that when the CBOE VIX fear index spikes and triggers asset liquidation, Bitcoin — with its historically elevated volatility metrics and market beta — should depreciate sharply (*flight-to-liquidity*). However, empirical observations over the 2023–2026 period identify a structural anomaly:

| Event | Date | Traditional Finance Assumption | Observed Market Reality |
|--------------------|-------------------|------------------------------|--------------------------------------|
| Israel-Hamas Conflict Escalation | Oct 2023 | Sharp depreciation (*risk-off selloff*) | Momentary decline ➜ Structural rally +12% / 30 Days |
| Iran-Israel Airstrike | Apr 2024 | Sharp depreciation | -7% decline ➜ Full recovery within 48 Hours |
| Partial Strait of Hormuz Restriction | Feb 2026 | Sharp depreciation | Correction to $63K ➜ Strong rebound above $72K |
| Declaration of Ayatollah Khamenei's Death | Feb 2026 | Sharp depreciation | -4.5% decline ➜ Massive rebound through $68K |

### 3. Strategic Implications (Macro Decision-Making)
This analysis translates the narrative polemic into empirical propositions for three key decision-making constituencies:
*   **Portfolio Managers & CIOs**: Quantitatively justifies the urgency of incorporating Bitcoin allocations into multi-asset hedging strategies.
*   **Quantitative Risk Analysts**: Informs the redesign of dynamic risk models for instruments with shifting correlation profiles.
*   **Policy Makers**: Provides primary evidence for the *flight-to-crypto* thesis during periods of acute global risk sentiment.

---

## 🧪 Methodology Architecture and Model Specifications

This project formulates three statistical testing pillars to holistically dissect the anatomy of instrument performance:

### I. Event Study Methodology (Abnormal Return Measurement)
The Event Study framework is applied to isolate the causal effect of high-impact geopolitical events from routine market movements. The Market Model is specified via OLS regression:

$$AR_{i,t} = R_{i,t} - (\hat{\alpha}_i + \hat{\beta}_i \cdot R_{m,t})$$
$$CAR_{i} = \sum_{t=T_1}^{T_2} AR_{i,t}$$

*   **Estimation Window**: $t \in [-125, -6]$ trading days prior to the event, used to calibrate the clean expected-return profile (insulated from any event-contamination effects). The market proxy ($R_m$) is the SPY ETF.
*   **Event Window**: $\pm5$ trading sessions pre- and post-event. Statistical significance is evaluated via a two-tailed *Student's t-test*.

### II. Multi-Asset Rolling Correlation Decomposition
Designed to capture transient *crossover dynamics* in time-series correlation structure:

$$\rho_{window}(BTC, X)_t = \frac{\text{Covariance}(R_{BTC}, R_X)_{t-w:t}}{\sigma_{BTC} \cdot \sigma_X}$$

*   $X_{1}$ (*Risk-On* Proxy): Invesco QQQ Trust (U.S. Technology Sector Aggregate).
*   $X_{2}$ (*Safe-Haven* Proxy): SPDR Gold Shares (GLD).
*   The rolling window ($w$) is set to 30 trading days to eliminate microstructure noise. A regime-shift confirmation signal is validated when $\rho(BTC, GLD) > \rho(BTC, QQQ)$.

### III. VIX-Conditional Beta Stress Testing
Disaggregation of the instrument's systematic sensitivity ($Beta$) conditioned on the degree of broad-market implied volatility (CBOE VIX index):

$$R_{BTC,t} = \alpha_k + \beta_k \cdot R_{SPY,t} + \epsilon_t \quad \Big| \quad \text{VIX}_{t-1} \in \text{Regime } k$$
*Regime sequence (k)* is distributed asymmetrically: *Low* (0–15), *Normal* (15–25), *Elevated* (25–30), and the extreme market-freeze instance *Panic* ($>30$). The governing hypothesis holds that if Bitcoin is transitioning toward a shock-resistant asset, the numerical trajectory will be characterized by a deterministic decline in beta as the VIX enters the crisis quadrant (*Panic*).

---

## 📊 Comprehensive Findings Synthesis

Aggregating the mathematical model outputs yields the following synthesis matrix:

| Analytical Sub-Model | Quantitative Finding | Market Interpretation |
| :--- | :--- | :--- |
| **Model H1** (*Extreme Stress Correlation*) | Structural correlation doubling (Baseline 0.12 ➜ Stress Phase 0.24) | The functional relationship with deflationary instruments exhibits a solid parabolic trend, though the conclusive threshold (>0.5) has not yet been reached in absolute terms. |
| **Model H2** (*Correlative Regime Acceleration*) | **69 crossover phases** identified. Mean BTC-QQQ correlation recorded high at 0.36, while BTC-GLD remains subdued at 0.13. | The transition is characteristically intermittent and opportunistic rather than a permanent structural shift. |
| **Model H3** (*Market Model & AR Systematization*) | $CAR_{Khamenei} = +7.46\%$ and $CAR_{Israel\text{-}H} = +5.85\%$ | Capital injection anomalies (appreciation anomalies) are empirically confirmed following pro-risk sentiment reallocation during the most recent calendar period of the mid-century. |
| **VIX Beta Model** | $\beta_{\text{Low}} = 0.70$ contrasted against a peak of $\beta_{\text{Norm}} = 1.30$ | The beta parameter does not collapse in the crisis regime ($\beta_{Panic} > 1.0$), precluding macro-immunity, classifying the asset as an adaptive super-volatile instrument. |

> **Scientific Data Final Conclusion:** The Bitcoin ecosystem currently occupies a **Mid-scale Incremental Transition** position. Deterministic momentum has not yet released the asset from the gravitational anchor of the *Growth/Risk-On Asset* classification, but has injected embryonic defensive-response characteristics. The market's greatest experiment regarding the 'Engineered Gold' finds that hybrid properties (*compartmental Safe-haven* characteristics) strengthen significantly as the 2026 study horizon approaches.

---

## 🚀 Installation & Quick Start

The analysis and presentation system is packaged for straightforward local reproduction.

1. **Clone the Repository via VCS:**
```bash
git clone https://github.com/raindragon14/Regime-Shift.git
cd Regime-Shift
```

2. **Create an Isolated Environment & Install Dependencies (Python 3.9+):**
```bash
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

3. **Launch the Visual Interface (Dashboard Presentation):**
```bash
python dashboard.py
```
*Navigate your browser to the local host at: `http://127.0.0.1:8051`. (The graphical interface is powered by the Dash-React architecture.)*

---

## 📂 Repository Structure

The codebase architecture separates backend calculation logic from the GUI presentation layer:

```text
.
├── src/                      # Analytical infrastructure module extensions
│   ├── analysis.py           # Core computation logic (OLS Event Study pipeline & Beta matrix)
│   ├── data_fetcher.py       # Historical data API interface (yfinance + Retry Hooks System)
│   ├── config.py             # Global runtime parameter registry
│   ├── visualization.py      # Offline canvas-based visual architecture (Plotly Graph Ops)
│   └── utils.py              # Data matrix micro-utility operations
├── config.yaml               # Parameter calibration, event pivot points, & asset node macro registry
├── dashboard.py              # Main Front-End GUI Presentation Rendering Module
├── main.py                   # Independent CLI console (back-testing dry-run model pipeline executor)
├── requirements.txt          # Python ecosystem dependency library manifest
├── LICENSE                   # MIT Open-Source License documentation
├── README.md                 # Primary documentation (English) — this file
└── README.id.md              # Comprehensive Scientific Research Report Manuscript (Bahasa Indonesia)
```

---
*This documentation manuscript and codebase have been meticulously designed and engineered for advanced exhibition and professional-grade **Quantitative Research Portfolio Evaluation** competitions.*
