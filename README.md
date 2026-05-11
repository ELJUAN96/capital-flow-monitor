# ⚡ Capital Flow Monitor

Dashboard de monitoreo de rotación de flujos de capital entre sectores:
**Seguridad → Crecimiento → Especulación**

---

## Setup

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Correr la app

```bash
streamlit run app.py
```

---

## Arquitectura

### Universo de Activos

| Sector | Ticker | Activo |
|--------|--------|--------|
| 🛡️ Seguridad | GLD | Oro |
| 🛡️ Seguridad | TLT | Bonos 20Y |
| 🛡️ Seguridad | BIL | Cash/T-Bills |
| 📈 Crecimiento | SPY | S&P 500 |
| 📈 Crecimiento | QQQ | Nasdaq |
| 📈 Crecimiento | XLE | Energía |
| 🎲 Especulación | IWM | Small Caps |
| 🎲 Especulación | BTC-USD | Bitcoin |
| 🎲 Especulación | ARKK | Innovación |
| 🤖 Cadena IA | MSFT | Software |
| 🤖 Cadena IA | NVDA | Chips |
| 🤖 Cadena IA | VRT | Infraestructura |
| 🤖 Cadena IA | CCJ | Energía Nuclear |

### Módulos

#### `fetch_snapshot()`
- Obtiene precio actual via `yf.Ticker.fast_info`
- Calcula Market Cap real: `sharesOutstanding × currentPrice`
- Calcula Z-Score de volumen sobre media móvil 20D

#### `fetch_price_history()`
- Descarga OHLCV histórico para el período seleccionado
- Cache TTL = 5 minutos

#### `compute_relative_strength()`
- RS = precio_activo / precio_SPY
- Normalizado a 100 en el inicio del período
- Permite ver quién outperforma/underperforma al mercado

### Visualizaciones

1. **Treemap** — Market Cap como tamaño, retorno diario como color (verde=sube, rojo=baja)
2. **Fuerza Relativa** — Multi-línea vs SPY, base 100
3. **Ratios Cruzados** — GLD/SPY, TLT/SPY, BTC/SPY, etc. para detectar risk-on/risk-off
4. **Cadena IA** — MSFT, NVDA, VRT, CCJ indexados juntos
5. **Z-Score Volumen** — Barras horizontales con alertas a ±2σ

### Interpretación de Ratios

| Ratio | Subiendo significa... |
|-------|----------------------|
| GLD/SPY | Fuga a refugio — **Risk OFF** |
| TLT/SPY | Rotación a bonos — miedo recesión |
| BTC/SPY | Apetito especulativo extremo — **Risk ON** |
| IWM/SPY | Confianza en economía doméstica EE.UU. |
| GLD/TLT | Inflación > deflación |
| QQQ/SPY | Liderazgo growth/tech |

---

## Marco Temporal

| Opción | Período | Intervalo |
|--------|---------|-----------|
| 1D | 1 día | 5 min |
| 5D | 5 días | 30 min |
| 1M | 1 mes | 1 día |
| 3M | 3 meses | 1 día |

---

*Data via yfinance (15 min delay en versión gratuita). NOT FINANCIAL ADVICE.*
