# Membongkar Mitos Emas Digital 🪙
**Analisis Kuantitatif Regime Shift Bitcoin Selama Krisis Geopolitik 2023–2026**

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Dash](https://img.shields.io/badge/dash-2.14+-teal.svg)
![Plotly](https://img.shields.io/badge/plotly-5.18+-purple.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> **Proyek Kompetisi Data Analisis & Portofolio Quantitative Research**<br>
> Sebuah investigasi empiris menggunakan *Event Study*, *Rolling Correlation*, dan *VIX-Conditional Beta* untuk menguji narasi *safe haven* Bitcoin.

---

## 📌 Daftar Isi
1. [Abstract](#abstract)
2. [Mengapa Ini Penting?](#mengapa-ini-penting)
3. [Hipotesis & Metodologi](#hipotesis--metodologi)
4. [Temuan Utama](#temuan-utama)
5. [Quick Start (Dashboard)](#quick-start)
6. [Struktur Repositori](#struktur-repositori)

---

## 📖 Abstrak Eksploratori

Penelitian kuantitatif ini menginvestigasi **hipotesis pergeseran rezim** pada kelas aset kripto, secara spesifik menguji apakah Bitcoin (BTC) sedang mengalami transisi fundamental dari aset spekulatif berisiko tinggi (*risk-on proxy*) menjadi aset pelindung nilai makroekonomi (*safe haven*). Fokus waktu observasi difokuskan pada periode eskalasi geopolitik tingkat tinggi 2023–2026, yang mencakup guncangan eksternal seperti pecahnya konflik Israel-Hamas, serangan militer Iran-Israel, hingga pengetatan jalur maritim Selat Hormuz.

Melalui penerapan tripartit *framework* kuantitatif standar industri, meliputi rancangan **Event Study (Model Pasar OLS)**, komputasi **Multi-Asset Rolling Correlation**, dan dekomposisi **VIX-Conditional Beta** kami menyimpulkan bahwa Bitcoin saat ini tidak terklasifikasi sebagai murni aset *risk-on* maupun *safe haven*. Data secara empiris mengungkap struktur **transisi bertahap yang intermiten**: terdeteksi lonjakan korelasi korektif terhadap instrumen emas (GLD) pada fase kepanikan pasar global, serta akumulasi *abnormal return* yang persisten positif pada *event* paling mutakhir, diiringi koefisien beta pasar yang belum tertundukkan sepenuhnya (*Beta > 1.0*). Narasi "Emas Digital" oleh karena itu bukanlah sebuah aksioma pasar yang mapan, melainkan suatu **hipotesis dinamis yang sedang divalidasi oleh institusi global di tengah guncangan geopolitik.**

---

## 🏛️ Mengapa Kajian Ini Berdampak Signifikan?

### 1. Pergeseran Paradigma dan Kedalaman Pasar
Dengan penetrasi kapitalisasi pasar yang menembus batas psikologis **$1.3 triliun** serta katalis strategis berupa persetujuan produk ETF *spot* oleh *market makers* raksasa (mis. BlackRock, Fidelity), Bitcoin telah melampaui fase "spekulasi ritel pinggiran". Aset ini kini tertanam secara substansial pada lapisan portofolio global, yang menuntut pendekatan evaluasi risiko (*risk profiling*) yang jauh lebih terkuantifikasi.

### 2. Anomali Kinerja Terhadap Guncangan Deflasioner
Berdasarkan literatur keuangan klasik, pada saat terjadi lonjakan indeks ketakutan pasar (CBOE VIX) yang memicu likuidasi aset, Bitcoin dengan metrik volatilitas historis dan *market beta* yang dominan tinggi diasumsikan akan terdepresiasi tajam (*flight-to-liquidity*). Namun, observasi empiris periode 2023–2026 mengidentifikasi anomali struktural:

| Kejadian (*Event*) | Tanggal Kejadian | Asumsi Keuangan Tradisional | Realitas Kinerja (*Market Reality*) |
|--------------------|-------------------|------------------------------|--------------------------------------|
| Eskalasi Definitif Israel-Hamas | Okt 2023 | Depresiasi tajam (*risk-off selloff*) | Penurunan sesaat ➜ Reli struktural +12% / 30 Hari |
| Serangan Udara Iran-Israel | Apr 2024 | Depresiasi tajam | Penurunan -7% ➜ Pemulihan total (*recovery*) dalam 48 Jam |
| Restriksi Parsial Selat Hormuz | Feb 2026 | Depresiasi tajam | Koreksi ke $63K ➜ Terpantul kuat melampaui $72K |
| Deklarasi Wafatnya Ayatollah Khamenei | Feb 2026 | Depresiasi tajam | Penurunan -4.5% ➜ Rebound masif menembus $68K |

### 3. Eksekusi Strategis (Implikasi Makro)
Analisis ini mendudukkan polemik naratif menjadi proposisi empiris untuk tiga pilar utama pengambil keputusan:
*   **Portfolio Managers & CIOs**: Menjustifikasi secara kuantitatif urgensi alokasi Bitcoin pada *hedging* portofolio *multi-asset*.
*   **Quantitative Risk Analysts**: Mendesain ulang permodelan risiko dinamis untuk *instrument* dengan profil korelasi yang bergeser.
*   **Policy Makers**: Menyediakan bukti primer terkait tesis pelarian-ke-kripto (*flight-to-crypto*) kala sentimen global berdarah.

---

## 🧪 Arsitektur Metodologi dan Spesifikasi Model

Proyek ini merumuskan tiga landasan pengujian statistik untuk secara holistik membedah anatomik dari kinerja instrumen:

### I. Metodologi Event Study (Pengukuran Abnormal Return)
Studi kejadian (*Event Study*) diterapkan guna menceraikan (*isolate*) efek peristiwa geopolitik mematikan dari pergerakan pasar reguler. Model Pasar (*Market Model*) diformulasikan via Regresi OLS:

$$AR_{i,t} = R_{i,t} - (\hat{\alpha}_i + \hat{\beta}_i \cdot R_{m,t})$$
$$CAR_{i} = \sum_{t=T_1}^{T_2} AR_{i,t}$$

*   **Jendela Estimasi (*Estimation Window*)**: $t \in [-125, -6]$ hari sebelum insiden, untuk mengkalibrasi profil return ekspektasian murni (bebas polusi dari imbas internal dari peristiwa). Indeks pengukur proksi pasar ($R_m$) dikonstitusikan oleh instrumen SPY ETF.
*   **Jendela Kejadian (*Event Window*)**: $\pm5$ siklus perdagangan bursa pasca dan pra insiden. Parameter diuji kebermaknaannya secara statistik via *student t-test*.

### II. Dekomposisi Multi-Asset Rolling Correlation
Bertujuan merekam fluktuasi transien (*crossover identitas*) dalam dinamika korelasi *time-series*:

$$\rho_{window}(BTC, X)_t = \frac{\text{Covariance}(R_{BTC}, R_X)_{t-w:t}}{\sigma_{BTC} \cdot \sigma_X}$$

*   $X_{1}$ (Proksi *Risk-On*): Invesco QQQ Trust (Agregat sektor Teknologi AS).
*   $X_{2}$ (Proksi *Safe-Haven*): SPDR Gold Shares (GLD).
*   Interval waktu observasi (*rolling window* $w$) ditetapkan selama 30-hari perdagangan guna meniadakan derau mikrostruktur pasar (*microstructure noise*). Sinyal pengkonfirmasi pergeseran rezim tervalidasi bila $\rho(BTC, GLD) > \rho(BTC, QQQ)$.

### III. Pengujian Stres VIX-Conditional Beta
Pemecahan (*disaggregation*) kepekaan sistemik instrumen ($Beta$) yang disandarkan pada derajat volatilitas pasar luas yang tersirat (*implied volatility* via indeks VIX CBOE):

$$R_{BTC,t} = \alpha_k + \beta_k \cdot R_{SPY,t} + \epsilon_t \quad \Big| \quad \text{VIX}_{t-1} \in \text{Regime } k$$
*Rangkaian Rezim (k)* didistribusikan secara tidak simetris (Asymmetric regimes): *Low* (0-15), *Normal* (15-25), *Elevated* (25-30), dan instansi ekstrem pembekuan pasar *Panic* ($>30$). Hipotesis yang menaungi pendirian bahwa jika Bitcoin beralih ke rupa aset anti guncangan, perwujudan trajektori numerik akan diwarnai oleh kejatuhan deterministik nilai beta-nya sejalan dengan masuknya VIX memasuki kuadran krisis (*Panic*).

---

## 📊 Sintesis Penemuan Komprehensif

Melalui agregasi keluaran program matematis, diperoleh tabulasi matriks sintesis:

| Pendekatan (*Sub-Model Analitik*) | Temuan Kuantitatif | Interpretasi Klinis (*Market Interpretation*) |
| :--- | :--- | :--- |
| **Model H1** (*Korelasi Stres Ekstrem*) | Penggandaan korelasi struktural (Baseline 0.12 ➜ Fase Stres 0.24) | Hubungan fungsional terhadap instrumen deflasioner memuat tren parabolik yang solid, selagi batas konklusif threshold (>0.5) belum tercapai absolut. |
| **Model H2** (*Akselerasi Rezim Korelatif*) | Diidentifikasi **69 fase crossover**. Rata-rata BTC-QQQ tercatat tinggi di 0.36, sedangkan BTC-GLD di anjungan bawah (0.13) | Sifat karakteristik transisi lebih bersifat spasial intermiten (fluktuasi oportunitis) bukan pergerakan struktural permanen. |
| **Model H3** (*Sistemasi Market Model & AR*) | Perolehan $CAR_{Khamenei} = +7.46\%$, dan $CAR_{Israel-H} = +5.85\%$ | Injeksi kapital (anomali apresiasi) terbukti eksis menyusul penataan ulang alokasi sentimen pro-risiko dalam masa kalendering terbaru pertengahan abad ini. |
| **Model VIX Beta** | $\beta_{\text{Low}} = 0.70$ bersanding kontras memuncak ke posisi $\beta_{\text{Norm}} = 1.30$ | Parameter Beta tersensor tidak anjlok pada rezim krisis ($\beta_{Panic} > 1.0$) meniadakan kepastian imunitas makro, aset tergolong aset super-volatil adaptif. |

> **Konklusi Final Data Ilmiah:** Ekosistem Bitcoin saat ini menduduki sebuah tumpuan **Transisi Bertahap Skala Menengah (*Mid-scale Incremental Transition*)**. Pergerakan deterministik belum melepaskan aset dari jangkar gravitasional *Growth/Risk-On Asset*, melainkan menyuntikkan embrio respons defensif. Eksperimentasi pasar terbesar perihal 'Emas Ciptaan' melahirkan penemuan bahwa karakteristik hibrida ($Safe-haven$ kompartmental) menguat siginifikan menyongsong akhir analisis studi tahun 2026.

---

## 🚀 Instalasi & Quick Start

Sistem arsitektur analisis dan presentasi ini dikemas ringkas untuk reproduksi lokal.

1. **Unduh Repositori via VCS (Version Control):**
```bash
git clone https://github.com/USERNAME/quant-regime-shift-btc.git
cd quant-regime-shift-btc
```

2. **Inisiasi Lingkungan Terisolasi & Instalasi Dependensi (Python 3.9+):**
```bash
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

3. **Mengeksekusi Antarmuka Visual (Presentasi Dashboard):**
```bash
python dashboard.py
```
*Navigasikan peramban (browser) anda menuju lokal *host* transmisi di: `http://127.0.0.1:8051`. (Tatap muka grafis dioperasikan oleh arsitektur Dash-React)*

---

## 📂 Struktur Repositori Terpadu (*Repository Directory*)

Penyusunan basis kode (Codebase architecture) dipisahkan antara logika abstraksi (*backend calculation*) dan tata letak visibilitas panel GUI:

```text
.
├── src/                      # Ekstensi Modul Infrastruktur Analitik
│   ├── analysis.py           # Core computation logic (Rangkaian OLS Event Study & Beta matrix)
│   ├── data_fetcher.py       # Interfacing API transmisi historis (yfinance + Retry Hooks System)
│   ├── config.py             # Global Registry parameter inisialisasi runtime
│   ├── visualization.py      # Pembentukan arsitektur visual Offline berbasis kanvas (Plotly Graph Ops)
│   └── utils.py              # Operasional mikro utilitas matriks data
├── config.yaml               # Penataan kalibrasi parameter, titik pivot events, & registri makro simpul aset
├── dashboard.py              # Modul utama Front-End Rendering Presentasi GUI
├── main.py                   # Konsol CLI independen (eksekutor pipeline model back-testing dry run)
├── requirements.txt          # Library manifest dependensi ekosistem Python
├── LICENSE                   # Dokumentasi Open-Source Lisensi MIT
└── README.md                 # Manuskrip Komprehensif Laporan Riset Ilmiah (File ini)
```

---
*Manuskrip dokumentasi dan basis kode ini dirancang dan direkayasa secara teliti untuk kebutuhan paparan eksibisi tingkat lanjut dan persaingan ajang **Portfolio Evaluasi Quantitative Research** kelas profesional.*
