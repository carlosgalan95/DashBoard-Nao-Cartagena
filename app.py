import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Análisis de Inversión Hotelera",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ESTILOS CSS AVANZADOS (THEME OVERRIDE) ---
# Esto fuerza el look "Clean White" similar a tu React App
st.markdown("""
<style>
    /* Forzar modo claro en la app */
    [data-testid="stAppViewContainer"] {
        background-color: #f8fafc; /* Slate-50 */
    }
    
    /* Sidebar blanca */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Textos generales */
    h1, h2, h3, p, div, label, span {
        color: #0f172a !important; /* Slate-900 */
        font-family: 'Inter', sans-serif;
    }
    
    /* TARJETAS PERSONALIZADAS (CSS para imitar tus cards de React) */
    .custom-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .custom-card:hover {
        border-color: #6366f1; /* Indigo-500 hover */
    }
    .card-title {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b; /* Slate-500 */
        margin-bottom: 8px;
    }
    .card-value {
        font-size: 24px;
        font-weight: 800;
        color: #1e293b; /* Slate-800 */
        margin: 0;
    }
    .card-subtitle {
        font-size: 11px;
        color: #94a3b8; /* Slate-400 */
        margin-top: 4px;
        font-weight: 500;
    }
    .trend-up {
        color: #10b981;
        font-size: 10px;
        font-weight: bold;
        background: #ecfdf5;
        padding: 2px 6px;
        border-radius: 999px;
        float: right;
    }
    
    /* Ajustes de Sliders para que sean Indigo */
    div.stSlider > div[data-baseweb="slider"] > div > div {
        background-color: #4f46e5 !important;
    }
    div.stSlider > div[data-baseweb="slider"] > div > div[role="slider"] {
        background-color: #4f46e5 !important;
        box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE NEGOCIO (Igual que antes) ---
INITIAL_INVESTMENT = 11739010000 

def get_historical_data():
    dates = pd.date_range(start='2021-01-01', end='2025-12-31', freq='M')
    base_revenue = 120000000 # Escala ajustada a tu imagen (millones)
    trend = np.linspace(0, 50000000, len(dates))
    seasonality = np.sin(np.linspace(0, 8*np.pi, len(dates))) * 30000000
    values = base_revenue + trend + seasonality + np.random.normal(0, 5000000, len(dates))
    df = pd.DataFrame({'date': dates, 'value': values})
    df['year'] = df['date'].dt.year
    return df

def generate_projections(ipc_rate, growth_factor, years_to_project, last_real_monthly_avg):
    future_dates = pd.date_range(start='2026-01-01', periods=years_to_project*12, freq='M')
    monthly_ipc = (1 + ipc_rate/100)**(1/12) - 1
    monthly_growth = (1 + growth_factor/100)**(1/12) - 1
    
    projections = []
    current_val = last_real_monthly_avg
    
    for date in future_dates:
        current_val = current_val * (1 + monthly_ipc + monthly_growth)
        season_factor = np.sin((date.month / 12) * 2 * np.pi) * 0.15
        base_proj = current_val * (1 + season_factor)
        
        projections.append({
            'date': date,
            'year': date.year,
            'pessimistic': base_proj * 0.85,
            'moderate': base_proj,
            'optimistic': base_proj * 1.20
        })
    return pd.DataFrame(projections)

def format_currency(val):
    return f"$ {val:,.0f}"

def format_percent(val):
    return f"{val*100:.2f}%"

# Datos
df_history = get_historical_data()
last_year_total = df_history[df_history['year'] == 2025]['value'].sum()
last_monthly_avg = df_history[df_history['year'] == 2025]['value'].mean()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='color:#4f46e5!important;'>⚙️ PANEL DE CONTROL</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    ipc_rate = st.slider("IPC Anual Esperado", 0.0, 15.0, 4.5, 0.1)
    st.caption("Ajuste de inflación para tarifas y costos del hotel.")
    
    growth_factor = st.slider("Crecimiento Orgánico", -5.0, 10.0, 0.0, 0.5)
    st.caption("Factor de mejora en ocupación y eficiencia.")
    
    years_to_project = st.slider("Años de Proyección", 1, 15, 5, 1)
    
    st.markdown("---")
    col_v1, col_v2 = st.columns(2)
    view_mode = col_v1.radio("MONEDA", ["$ COP", "% Rend"], label_visibility="collapsed")
    time_granularity = col_v2.radio("FRECUENCIA", ["Anual", "Mensual"], index=1, label_visibility="collapsed")

# Cálculos
df_proj = generate_projections(ipc_rate, growth_factor, years_to_project, last_monthly_avg)
avg_yield = last_year_total / INITIAL_INVESTMENT
cumulative_rev = df_proj['moderate'].sum()
cumulative_yield = cumulative_rev / INITIAL_INVESTMENT

if time_granularity == "Anual":
    chart_hist = df_history.groupby('year')['value'].sum().reset_index()
    chart_hist['date'] = chart_hist['year'].astype(str)
    chart_proj = df_proj.groupby('year')[['pessimistic', 'moderate', 'optimistic']].sum().reset_index()
    chart_proj['date'] = chart_proj['year'].astype(str)
else:
    chart_hist = df_history.copy()
    chart_proj = df_proj.copy()

# --- 5. INTERFAZ PRINCIPAL ---

# Header
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px;">
        <div style="background:#4f46e5; padding:8px; border-radius:8px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M5 21V7l8-4 8 4v14"/><path d="M5 7a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2"/><rect x="9" y="9" width="6" height="6" rx="1"/></svg>
        </div>
        <div>
            <h2 style="margin:0; font-size:20px; font-weight:700;">Análisis de Inversión Hotelera</h2>
            <p style="margin:0; font-size:12px; color:#64748b;">Rentabilidad y Proyecciones Dinámicas</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown(f"""
    <div style="text-align:right;">
        <div style="font-size:10px; font-weight:bold; color:#94a3b8; text-transform:uppercase;">Inversión Inicial</div>
        <div style="font-size:16px; font-weight:bold; color:#4f46e5;">{format_currency(INITIAL_INVESTMENT)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- TARJETAS PERSONALIZADAS (HTML) ---
# Usamos columnas de Streamlit pero inyectamos HTML dentro para el diseño de tarjetas
c1, c2, c3, c4 = st.columns(4)

def render_html_card(col, title, value, subtitle, trend=None):
    trend_html = f'<span class="trend-up">↑ {trend}</span>' if trend else ''
    html = f"""
    <div class="custom-card">
        <div class="card-title">{title} {trend_html}</div>
        <div class="card-value">{value}</div>
        <div class="card-subtitle">{subtitle}</div>
    </div>
    """
    col.markdown(html, unsafe_allow_html=True)

render_html_card(c1, "INGRESOS REALES (2025)", format_currency(last_year_total), "Cierre último año histórico", "Al alza")
render_html_card(c2, "RENDIMIENTO ACTUAL", format_percent(avg_yield), "ROI actual vs Inversión")
render_html_card(c3, f"PROYECCIÓN FINAL ({2025+years_to_project})", format_currency(chart_proj.iloc[-1]['moderate']), "Escenario
