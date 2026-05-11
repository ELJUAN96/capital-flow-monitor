"""
╔══════════════════════════════════════════════════════════════════╗
║          CAPITAL FLOW MONITOR — Senior Quant Dashboard           ║
║          Asset Rotation: Safety → Growth → Speculation           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Capital Flow Monitor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS — Dark Terminal Aesthetic ───────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;700;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: #080c14;
    color: #c9d1e0;
  }
  
  .stApp { background-color: #080c14; }
  
  .main-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 50%, #ff6b6b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
  }
  
  .subtitle {
    font-size: 0.75rem;
    color: #4a5568;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
  }
  
  .metric-card {
    background: linear-gradient(135deg, #0d1420 0%, #111827 100%);
    border: 1px solid #1e2d40;
    border-left: 3px solid #00d4ff;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
  }
  
  .metric-card.safety { border-left-color: #4ade80; }
  .metric-card.growth { border-left-color: #60a5fa; }
  .metric-card.speculation { border-left-color: #f472b6; }
  .metric-card.ai-chain { border-left-color: #fbbf24; }
  
  .metric-label {
    font-size: 0.65rem;
    color: #4a5568;
    letter-spacing: 0.15em;
    text-transform: uppercase;
  }
  
  .metric-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
  }
  
  .metric-delta.positive { color: #4ade80; }
  .metric-delta.negative { color: #f87171; }
  
  .section-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    border-bottom: 1px solid #1e2d40;
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem 0;
  }
  
  .zscore-alert {
    background: rgba(251, 191, 36, 0.08);
    border: 1px solid rgba(251, 191, 36, 0.3);
    border-radius: 4px;
    padding: 0.4rem 0.8rem;
    font-size: 0.72rem;
    color: #fbbf24;
    margin: 0.2rem 0;
  }
  
  .zscore-normal {
    background: rgba(74, 222, 128, 0.05);
    border: 1px solid rgba(74, 222, 128, 0.1);
    border-radius: 4px;
    padding: 0.4rem 0.8rem;
    font-size: 0.72rem;
    color: #6b7280;
    margin: 0.2rem 0;
  }
  
  .stSelectbox > div > div {
    background-color: #0d1420 !important;
    border: 1px solid #1e2d40 !important;
    color: #c9d1e0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
  }
  
  .stSidebar { background-color: #0a0f1a !important; }
  .stSidebar .stSelectbox label { color: #94a3b8 !important; font-size: 0.75rem !important; }
  
  div[data-testid="stMetric"] {
    background: #0d1420;
    border: 1px solid #1e2d40;
    border-radius: 6px;
    padding: 0.8rem;
  }
  
  .stTabs [data-baseweb="tab-list"] {
    background-color: #0d1420;
    border-bottom: 1px solid #1e2d40;
  }
  
  .stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #4a5568;
    letter-spacing: 0.1em;
  }
  
  .stTabs [aria-selected="true"] {
    color: #00d4ff !important;
    border-bottom: 2px solid #00d4ff !important;
  }
  
  .signal-badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }
  
  .badge-institutional { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
  .badge-normal { background: rgba(74,222,128,0.08); color: #4ade80; border: 1px solid rgba(74,222,128,0.2); }
  
  /* Plotly chart backgrounds */
  .js-plotly-plot { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ──────────────────────────────────────────────────────────────────
SECTORS = {
    "🛡️ Seguridad": {
        "tickers": ["GLD", "TLT", "BIL"],
        "color": "#4ade80",
        "css_class": "safety",
        "labels": {"GLD": "Oro", "TLT": "Bonos 20Y", "BIL": "Cash/T-Bills"},
    },
    "📈 Crecimiento": {
        "tickers": ["SPY", "QQQ", "XLE"],
        "color": "#60a5fa",
        "css_class": "growth",
        "labels": {"SPY": "S&P 500", "QQQ": "Nasdaq", "XLE": "Energía"},
    },
    "🎲 Especulación": {
        "tickers": ["IWM", "BTC-USD", "ARKK"],
        "color": "#f472b6",
        "css_class": "speculation",
        "labels": {"IWM": "Small Caps", "BTC-USD": "Bitcoin", "ARKK": "Innovación"},
    },
}

AI_CHAIN = {
    "MSFT": "Software",
    "NVDA": "Chips",
    "VRT": "Infraestructura",
    "CCJ": "Energía Nuclear",
}

ALL_TICKERS = (
    ["GLD", "TLT", "BIL", "SPY", "QQQ", "XLE", "IWM", "BTC-USD", "ARKK"]
    + list(AI_CHAIN.keys())
)

TIMEFRAME_MAP = {
    "1D": ("1d", "5m"),
    "5D": ("5d", "30m"),
    "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
}


# ─── DATA LAYER ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_price_history(tickers: list, period: str, interval: str) -> dict[str, pd.DataFrame]:
    """Fetch OHLCV history for a list of tickers."""
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(
                ticker, period=period, interval=interval,
                progress=False, auto_adjust=True
            )
            if df is not None and not df.empty:
                df.index = pd.to_datetime(df.index)
                data[ticker] = df
        except Exception as e:
            st.warning(f"⚠️ No se pudo obtener datos para {ticker}: {e}")
    return data


@st.cache_data(ttl=300, show_spinner=False)
def fetch_snapshot(tickers: list) -> pd.DataFrame:
    """Fetch current snapshot: price, daily return, market cap, volume."""
    rows = []
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info
            hist = yf.download(ticker, period="5d", interval="1d", progress=False, auto_adjust=True)

            # Normalize Close/Volume columns — yfinance may return MultiIndex DataFrame
            close_col = hist["Close"].squeeze() if not hist.empty else pd.Series(dtype=float)
            vol_col   = hist["Volume"].squeeze() if not hist.empty else pd.Series(dtype=float)

            # Current price
            try:
                current_price = float(info.last_price)
            except Exception:
                current_price = float(close_col.iloc[-1]) if not close_col.empty else np.nan

            # Daily return
            if len(close_col) >= 2:
                prev_close = float(close_col.iloc[-2])
                daily_return = (current_price - prev_close) / prev_close * 100
            else:
                daily_return = np.nan

            # Market cap (shares * price, fallback to reported market cap)
            try:
                shares = info.shares
                market_cap = float(shares) * current_price if shares and not np.isnan(float(shares)) else np.nan
            except Exception:
                market_cap = np.nan

            if pd.isna(market_cap):
                try:
                    full_info = t.info
                    market_cap = full_info.get("marketCap", np.nan)
                except Exception:
                    market_cap = np.nan

            # Volume stats (20-day z-score)
            volume = float(vol_col.iloc[-1]) if not vol_col.empty else np.nan
            vol_20d = vol_col.tail(21).iloc[:-1] if len(vol_col) >= 21 else vol_col
            vol_mean = float(vol_20d.mean()) if not vol_20d.empty else np.nan
            vol_std  = float(vol_20d.std())  if not vol_20d.empty else np.nan
            z_score  = (volume - vol_mean) / vol_std if vol_std and vol_std > 0 else 0.0

            rows.append({
                "ticker": ticker,
                "price": current_price,
                "daily_return": daily_return,
                "market_cap": market_cap,
                "volume": volume,
                "vol_mean_20d": vol_mean,
                "vol_std_20d": vol_std,
                "z_score_volume": z_score,
            })
        except Exception as e:
            st.warning(f"⚠️ Error en snapshot para {ticker}: {e}")
            rows.append({
                "ticker": ticker, "price": np.nan, "daily_return": np.nan,
                "market_cap": np.nan, "volume": np.nan,
                "vol_mean_20d": np.nan, "vol_std_20d": np.nan, "z_score_volume": np.nan,
            })
    return pd.DataFrame(rows).set_index("ticker")


def get_sector_label(ticker: str) -> str:
    for sector, meta in SECTORS.items():
        if ticker in meta["tickers"]:
            return sector
    if ticker in AI_CHAIN:
        return "🤖 Cadena IA"
    return "Otro"


def get_sector_color(ticker: str) -> str:
    for sector, meta in SECTORS.items():
        if ticker in meta["tickers"]:
            return meta["color"]
    if ticker in AI_CHAIN:
        return "#fbbf24"
    return "#6b7280"


def compute_relative_strength(price_history: dict, base: str = "SPY") -> pd.DataFrame:
    """RS = price_asset / price_SPY, normalized to 100 at start."""
    if base not in price_history:
        return pd.DataFrame()
    spy = price_history[base]["Close"].squeeze()
    rs_dict = {}
    for ticker, df in price_history.items():
        if ticker == base:
            continue
        prices = df["Close"].squeeze()
        aligned = prices.reindex(spy.index, method="ffill").dropna()
        spy_aligned = spy.reindex(aligned.index).dropna()
        common = aligned.index.intersection(spy_aligned.index)
        if len(common) < 2:
            continue
        rs = aligned[common] / spy_aligned[common]
        rs_norm = rs / rs.iloc[0] * 100
        rs_dict[ticker] = rs_norm
    return pd.DataFrame(rs_dict)


# ─── CHART BUILDERS ─────────────────────────────────────────────────────────────
def build_treemap(snapshot: pd.DataFrame) -> go.Figure:
    """Treemap: size = market cap, color = daily return."""
    df = snapshot.copy().reset_index()
    df = df.dropna(subset=["market_cap"])

    labels, parents, values, colors, text = [], [], [], [], []
    
    # Root
    labels.append("Capital Flow Monitor")
    parents.append("")
    values.append(0)
    colors.append(0)
    text.append("")

    for sector_name, meta in SECTORS.items():
        labels.append(sector_name)
        parents.append("Capital Flow Monitor")
        sector_rows = df[df["ticker"].isin(meta["tickers"])]
        sector_cap = sector_rows["market_cap"].sum()
        values.append(sector_cap)
        avg_ret = sector_rows["daily_return"].mean()
        colors.append(avg_ret if not np.isnan(avg_ret) else 0)
        text.append(f"{avg_ret:+.2f}%" if not np.isnan(avg_ret) else "")

        for _, row in sector_rows.iterrows():
            label = meta["labels"].get(row["ticker"], row["ticker"])
            labels.append(f"{row['ticker']}<br>{label}")
            parents.append(sector_name)
            cap = row["market_cap"] if not np.isnan(row["market_cap"]) else 1e9
            values.append(cap)
            ret = row["daily_return"] if not np.isnan(row["daily_return"]) else 0
            colors.append(ret)
            price_str = f"${row['price']:,.2f}" if not np.isnan(row["price"]) else "N/A"
            text.append(f"{ret:+.2f}%<br>{price_str}")

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        customdata=text,
        text=text,
        textinfo="label+text",
        marker=dict(
            colors=colors,
            colorscale=[
                [0.0, "#7f1d1d"],
                [0.3, "#991b1b"],
                [0.48, "#1e2d40"],
                [0.52, "#1e2d40"],
                [0.7, "#14532d"],
                [1.0, "#166534"],
            ],
            cmid=0,
            cmin=-3,
            cmax=3,

        ),
        hovertemplate="<b>%{label}</b><br>Market Cap: $%{value:,.0f}<br>%{customdata}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#080c14",
        paper_bgcolor="#080c14",
        font=dict(color="#94a3b8", family="JetBrains Mono"),
        height=460,
        margin=dict(t=10, l=5, r=5, b=5),
    )
    return fig


def build_relative_strength(rs_df: pd.DataFrame, selected_tickers: list = None) -> go.Figure:
    """Multi-line RS chart vs SPY (indexed to 100)."""
    if rs_df.empty:
        return go.Figure()

    fig = go.Figure()
    tickers_to_plot = selected_tickers if selected_tickers else rs_df.columns.tolist()

    for ticker in tickers_to_plot:
        if ticker not in rs_df.columns:
            continue
        series = rs_df[ticker].dropna()
        if series.empty:
            continue

        color = get_sector_color(ticker)
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            name=ticker,
            mode="lines",
            line=dict(color=color, width=1.5),
            hovertemplate=f"<b>{ticker}</b><br>RS: %{{y:.1f}}<extra></extra>",
        ))

    # Baseline at 100 (= SPY performance)
    fig.add_hline(y=100, line_dash="dash", line_color="#1e2d40", line_width=1)

    fig.update_layout(
        plot_bgcolor="#080c14",
        paper_bgcolor="#080c14",
        font=dict(color="#94a3b8", family="JetBrains Mono"),
        height=380,
        margin=dict(t=10, l=10, r=10, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            font=dict(size=10, color="#94a3b8"),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(showgrid=True, gridcolor="#131c2b", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#131c2b", zeroline=False, title="RS vs SPY (Base=100)"),
    )
    return fig


def build_cross_ratio_chart(price_history: dict, pairs: list) -> go.Figure:
    """Ratio charts: GLD/SPY, TLT/SPY, BTC-USD/SPY, etc."""
    n = len(pairs)
    if n == 0:
        return go.Figure()

    fig = make_subplots(
        rows=n, cols=1,
        shared_xaxes=True,
        subplot_titles=[f"{a} / {b}" for a, b in pairs],
        vertical_spacing=0.06,
    )

    for i, (a, b) in enumerate(pairs, 1):
        if a not in price_history or b not in price_history:
            continue
        pa = price_history[a]["Close"].squeeze()
        pb = price_history[b]["Close"].squeeze()
        aligned_a = pa.reindex(pb.index, method="ffill").dropna()
        aligned_b = pb.reindex(aligned_a.index).dropna()
        common = aligned_a.index.intersection(aligned_b.index)
        if len(common) < 2:
            continue
        ratio = aligned_a[common] / aligned_b[common]
        ratio_norm = ratio / ratio.iloc[0] * 100

        # Color based on trend
        color = "#f472b6" if ratio_norm.iloc[-1] < ratio_norm.iloc[0] else "#4ade80"

        fig.add_trace(go.Scatter(
            x=ratio_norm.index,
            y=ratio_norm.values,
            name=f"{a}/{b}",
            mode="lines",
            line=dict(color=color, width=1.8),
            fill="tozeroy",
            fillcolor=f"rgba{tuple(list(bytes.fromhex(color[1:])) + [20])}",
            hovertemplate=f"<b>{a}/{b}</b>: %{{y:.1f}}<extra></extra>",
        ), row=i, col=1)

        fig.update_yaxes(
            showgrid=True, gridcolor="#131c2b",
            tickfont=dict(size=9, color="#4a5568"),
            row=i, col=1,
        )

    fig.update_layout(
        plot_bgcolor="#080c14",
        paper_bgcolor="#080c14",
        font=dict(color="#94a3b8", family="JetBrains Mono"),
        height=80 + 140 * n,
        margin=dict(t=30, l=10, r=10, b=10),
        showlegend=False,
    )
    for ann in fig.layout.annotations:
        ann.font.size = 10
        ann.font.color = "#94a3b8"

    return fig


def build_ai_chain_chart(price_history: dict) -> go.Figure:
    """Performance chart for the AI supply chain."""
    fig = go.Figure()
    colors = {"MSFT": "#60a5fa", "NVDA": "#a78bfa", "VRT": "#34d399", "CCJ": "#fbbf24"}

    for ticker, label in AI_CHAIN.items():
        if ticker not in price_history:
            continue
        df = price_history[ticker]
        prices = df["Close"].squeeze().dropna()
        if prices.empty:
            continue
        norm = prices / prices.iloc[0] * 100
        fig.add_trace(go.Scatter(
            x=norm.index, y=norm.values,
            name=f"{ticker} ({label})",
            mode="lines",
            line=dict(color=colors.get(ticker, "#fff"), width=2),
            hovertemplate=f"<b>{ticker}</b><br>Idx: %{{y:.1f}}<extra></extra>",
        ))

    fig.add_hline(y=100, line_dash="dot", line_color="#1e2d40", line_width=1)
    fig.update_layout(
        plot_bgcolor="#080c14",
        paper_bgcolor="#080c14",
        font=dict(color="#94a3b8", family="JetBrains Mono"),
        height=360,
        margin=dict(t=10, l=10, r=10, b=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=10, color="#94a3b8"),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(showgrid=True, gridcolor="#131c2b"),
        yaxis=dict(showgrid=True, gridcolor="#131c2b", title="Performance (Base=100)"),
    )
    return fig


def build_volume_zscore_bar(snapshot: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of volume Z-scores."""
    df = snapshot.copy().reset_index()
    df = df.dropna(subset=["z_score_volume"]).sort_values("z_score_volume")

    colors = [
        "#f87171" if z < -2 else
        "#fbbf24" if z > 2 else
        "#60a5fa" if z > 1 else
        "#374151"
        for z in df["z_score_volume"]
    ]

    fig = go.Figure(go.Bar(
        x=df["z_score_volume"],
        y=df["ticker"],
        orientation="h",
        marker_color=colors,
        hovertemplate="<b>%{y}</b><br>Z-Score: %{x:.2f}<extra></extra>",
    ))

    # 2σ reference lines
    fig.add_vline(x=2, line_dash="dash", line_color="#fbbf24", line_width=1,
                  annotation_text="2σ", annotation_font_size=9, annotation_font_color="#fbbf24")
    fig.add_vline(x=-2, line_dash="dash", line_color="#fbbf24", line_width=1)
    fig.add_vline(x=0, line_color="#1e2d40", line_width=1)

    fig.update_layout(
        plot_bgcolor="#080c14",
        paper_bgcolor="#080c14",
        font=dict(color="#94a3b8", family="JetBrains Mono"),
        height=380,
        margin=dict(t=10, l=10, r=40, b=10),
        xaxis=dict(title="Z-Score Volumen (20D)", showgrid=True, gridcolor="#131c2b"),
        yaxis=dict(showgrid=False),
    )
    return fig


# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="main-title">⚡ CFM</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Capital Flow Monitor</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="font-size:0.7rem;color:#4a5568;letter-spacing:0.1em;text-transform:uppercase;">Marco Temporal</p>', unsafe_allow_html=True)
    timeframe = st.selectbox("", list(TIMEFRAME_MAP.keys()), index=0, label_visibility="collapsed")
    period, interval = TIMEFRAME_MAP[timeframe]

    st.markdown("---")
    st.markdown('<p style="font-size:0.7rem;color:#4a5568;letter-spacing:0.1em;text-transform:uppercase;">Ratios a Monitorear</p>', unsafe_allow_html=True)
    available_pairs = [
        ("GLD", "SPY"), ("TLT", "SPY"), ("BTC-USD", "SPY"),
        ("IWM", "SPY"), ("GLD", "TLT"), ("QQQ", "SPY"),
    ]
    selected_pairs_str = st.multiselect(
        "",
        [f"{a}/{b}" for a, b in available_pairs],
        default=["GLD/SPY", "TLT/SPY", "BTC-USD/SPY"],
        label_visibility="collapsed",
    )
    selected_pairs = [tuple(s.split("/")) for s in selected_pairs_str]

    st.markdown("---")
    refresh = st.button("⟳ Actualizar Datos", use_container_width=True)
    if refresh:
        st.cache_data.clear()
        st.rerun()

    st.markdown("""
    <div style="position:fixed;bottom:1rem;font-size:0.6rem;color:#1e2d40;letter-spacing:0.05em;">
        Data: yfinance (15min delay)<br>
        Refresh TTL: 5 min
    </div>
    """, unsafe_allow_html=True)


# ─── MAIN LAYOUT ────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">Capital Flow Monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Detección de Rotación de Activos · Seguridad → Crecimiento → Especulación</div>', unsafe_allow_html=True)

# Load data
with st.spinner("Conectando a yfinance..."):
    snapshot = fetch_snapshot(ALL_TICKERS)
    price_history = fetch_price_history(ALL_TICKERS, period, interval)
    rs_df = compute_relative_strength(price_history, base="SPY")

# ─── KPI ROW ────────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

def format_kpi(ticker: str, label: str) -> tuple:
    row = snapshot.loc[ticker] if ticker in snapshot.index else None
    if row is None or pd.isna(row["price"]):
        return "N/A", "—"
    price = f"${row['price']:,.2f}" if row["price"] > 1 else f"${row['price']:.4f}"
    ret = row["daily_return"]
    delta = f"{ret:+.2f}%" if not pd.isna(ret) else "—"
    return price, delta

with col1:
    p, d = format_kpi("SPY", "S&P 500")
    st.metric("🇺🇸 SPY", p, d)
with col2:
    p, d = format_kpi("GLD", "Oro")
    st.metric("🥇 GLD", p, d)
with col3:
    p, d = format_kpi("TLT", "Bonos 20Y")
    st.metric("📄 TLT", p, d)
with col4:
    p, d = format_kpi("BTC-USD", "Bitcoin")
    st.metric("₿ BTC", p, d)
with col5:
    p, d = format_kpi("NVDA", "NVIDIA")
    st.metric("🖥️ NVDA", p, d)

st.markdown("<br>", unsafe_allow_html=True)

# ─── TABS ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️  TREEMAP · MARKET CAP",
    "📊  FUERZA RELATIVA",
    "⚖️  RATIOS CRUZADOS",
    "🤖  CADENA IA",
])

with tab1:
    st.markdown('<div class="section-header">Distribución de Flujos — Tamaño = Market Cap · Color = Retorno Diario</div>', unsafe_allow_html=True)
    
    # Z-score alerts
    alert_cols = st.columns(3)
    for sector_name, meta in SECTORS.items():
        with alert_cols[list(SECTORS.keys()).index(sector_name)]:
            st.markdown(f'<p style="font-size:0.7rem;color:{meta["color"]};letter-spacing:0.1em;">{sector_name}</p>', unsafe_allow_html=True)
            for ticker in meta["tickers"]:
                if ticker not in snapshot.index:
                    continue
                row = snapshot.loc[ticker]
                z = row["z_score_volume"]
                label = meta["labels"].get(ticker, ticker)
                if not pd.isna(z) and abs(z) > 2:
                    st.markdown(f'<div class="zscore-alert">⚡ {ticker} ({label}) Z={z:.1f}σ — FLUJO INSTITUCIONAL</div>', unsafe_allow_html=True)
                else:
                    z_str = f"{z:.1f}σ" if not pd.isna(z) else "N/A"
                    st.markdown(f'<div class="zscore-normal">· {ticker} ({label}) Z={z_str}</div>', unsafe_allow_html=True)

    st.plotly_chart(build_treemap(snapshot), use_container_width=True, config={"displayModeBar": False})

    # Sector summary table
    st.markdown('<div class="section-header">Resumen por Sector</div>', unsafe_allow_html=True)
    summary_data = []
    for sector_name, meta in SECTORS.items():
        sector_snap = snapshot.reindex(meta["tickers"]).dropna(subset=["daily_return"])
        avg_ret = sector_snap["daily_return"].mean()
        total_cap = sector_snap["market_cap"].sum()
        best = sector_snap["daily_return"].idxmax() if not sector_snap.empty else "—"
        worst = sector_snap["daily_return"].idxmin() if not sector_snap.empty else "—"
        summary_data.append({
            "Sector": sector_name,
            "Retorno Promedio": f"{avg_ret:+.2f}%" if not pd.isna(avg_ret) else "N/A",
            "Market Cap Total": f"${total_cap/1e12:.2f}T" if total_cap > 1e12 else f"${total_cap/1e9:.0f}B",
            "Mejor": best,
            "Peor": worst,
        })
    st.dataframe(
        pd.DataFrame(summary_data).set_index("Sector"),
        use_container_width=True,
        hide_index=False,
    )


with tab2:
    st.markdown('<div class="section-header">Fuerza Relativa vs SPY — Base 100 al inicio del período</div>', unsafe_allow_html=True)
    
    # Ticker selector
    available_for_rs = [t for t in ALL_TICKERS if t != "SPY" and t in rs_df.columns]
    selected_rs = st.multiselect(
        "Selecciona activos:",
        available_for_rs,
        default=["GLD", "TLT", "BTC-USD", "IWM", "QQQ", "ARKK"],
        key="rs_selector"
    )

    if not rs_df.empty and selected_rs:
        st.plotly_chart(build_relative_strength(rs_df, selected_rs), use_container_width=True, config={"displayModeBar": False})

        # RS ranking table
        st.markdown('<div class="section-header">Ranking RS actual — Outperformers vs Underperformers</div>', unsafe_allow_html=True)
        rs_latest = {}
        for ticker in selected_rs:
            if ticker in rs_df.columns:
                series = rs_df[ticker].dropna()
                if not series.empty:
                    rs_latest[ticker] = series.iloc[-1]

        if rs_latest:
            rs_series = pd.Series(rs_latest).sort_values(ascending=False)
            rank_data = pd.DataFrame({
                "Ticker": rs_series.index,
                "RS vs SPY": [f"{v:.1f}" for v in rs_series.values],
                "Status": ["🟢 Outperforming" if v > 100 else "🔴 Underperforming" for v in rs_series.values],
                "Sector": [get_sector_label(t) for t in rs_series.index],
            })
            st.dataframe(rank_data.set_index("Ticker"), use_container_width=True)
    else:
        st.info("Selecciona activos para ver la fuerza relativa.")


with tab3:
    st.markdown('<div class="section-header">Ratios Cruzados — Flight to Safety vs Risk-On</div>', unsafe_allow_html=True)

    if not selected_pairs:
        st.info("Selecciona al menos un ratio en el panel izquierdo.")
    else:
        # Interpretation hints
        hints = {
            "GLD/SPY": "📈 Subiendo → Dinero huyendo a refugio / Riesgo OFF",
            "TLT/SPY": "📈 Subiendo → Rotación a bonos / Miedo de recesión",
            "BTC-USD/SPY": "📈 Subiendo → Apetito especulativo / Riesgo ON extremo",
            "IWM/SPY": "📈 Subiendo → Confianza en economía doméstica EE.UU.",
            "GLD/TLT": "📈 Subiendo → Inflación sobre deflación",
            "QQQ/SPY": "📈 Subiendo → Liderazgo growth/tech / Riesgo ON",
        }
        for pair_str in selected_pairs_str:
            hint = hints.get(pair_str, "")
            if hint:
                st.markdown(f'<div class="zscore-alert" style="margin-bottom:0.3rem;">{pair_str} — {hint}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(
            build_cross_ratio_chart(price_history, selected_pairs),
            use_container_width=True,
            config={"displayModeBar": False}
        )


with tab4:
    st.markdown('<div class="section-header">Cadena Simbiótica de IA — Performance Indexada</div>', unsafe_allow_html=True)
    
    ai_col1, ai_col2 = st.columns([3, 1])
    with ai_col1:
        st.plotly_chart(build_ai_chain_chart(price_history), use_container_width=True, config={"displayModeBar": False})
    
    with ai_col2:
        st.markdown('<p style="font-size:0.7rem;color:#fbbf24;letter-spacing:0.1em;text-transform:uppercase;">Snapshots IA</p>', unsafe_allow_html=True)
        for ticker, label in AI_CHAIN.items():
            if ticker not in snapshot.index:
                continue
            row = snapshot.loc[ticker]
            ret = row["daily_return"]
            ret_str = f"{ret:+.2f}%" if not pd.isna(ret) else "N/A"
            price_str = f"${row['price']:,.2f}" if not pd.isna(row["price"]) else "N/A"
            color = "#4ade80" if not pd.isna(ret) and ret >= 0 else "#f87171"
            st.markdown(f"""
            <div class="metric-card ai-chain">
                <div class="metric-label">{ticker} · {label}</div>
                <div class="metric-value">{price_str}</div>
                <div class="metric-delta {'positive' if not pd.isna(ret) and ret >= 0 else 'negative'}">{ret_str}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Volume Z-score for full universe
    st.markdown('<div class="section-header">Z-Score de Volumen — Señales de Flujo Institucional (Universo Completo)</div>', unsafe_allow_html=True)
    st.plotly_chart(build_volume_zscore_bar(snapshot), use_container_width=True, config={"displayModeBar": False})

    # Alert table
    institutional_signals = snapshot[snapshot["z_score_volume"].abs() > 2].copy()
    if not institutional_signals.empty:
        st.markdown('<div class="section-header">🚨 Señales Activas — Volumen > 2σ</div>', unsafe_allow_html=True)
        sig_display = institutional_signals.reset_index()[["ticker", "price", "daily_return", "z_score_volume", "volume", "vol_mean_20d"]].copy()
        sig_display.columns = ["Ticker", "Precio", "Retorno%", "Z-Score Vol", "Volumen", "Vol Avg 20D"]
        sig_display["Retorno%"] = sig_display["Retorno%"].apply(lambda x: f"{x:+.2f}%" if not pd.isna(x) else "N/A")
        sig_display["Z-Score Vol"] = sig_display["Z-Score Vol"].apply(lambda x: f"{x:.2f}σ")
        sig_display["Volumen"] = sig_display["Volumen"].apply(lambda x: f"{x:,.0f}" if not pd.isna(x) else "N/A")
        sig_display["Vol Avg 20D"] = sig_display["Vol Avg 20D"].apply(lambda x: f"{x:,.0f}" if not pd.isna(x) else "N/A")
        st.dataframe(sig_display.set_index("Ticker"), use_container_width=True)
    else:
        st.info("No hay señales de volumen institucional en este momento (|Z| < 2σ para todos los activos).")

# ─── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;font-size:0.65rem;color:#1e2d40;letter-spacing:0.1em;padding:0.5rem 0;">
    CAPITAL FLOW MONITOR · Data via yfinance (15min delay) · NOT FINANCIAL ADVICE
</div>
""", unsafe_allow_html=True)
