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

# --- 2. ESTILOS CSS (FORZANDO MODO CLARO Y TARJETAS) ---
st.markdown("""
<style>
    /* Forzar fondo blanco general */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Sidebar blanca */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Textos oscuros para contraste */
    h1, h2, h3, p, div, label, span, li {
        color: #0f172a !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* DISEÑO DE TARJETAS (CARDS) */
    .custom-card {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b !important;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-value {
        font-size: 28px;
        font-weight: 800;
        color: #1e293b !important;
        margin-top: 4px;
        margin-bottom: 4px;
    }
    .card-subtitle {
        font-size: 12px;
        color: #94a3b8 !important;
        font-weight: 500;
    }
    .trend-badge {
        background-color: #dcfce7;
        color: #166534 !important;
        font-size: 10px;
        padding: 2px 8px;
        border-radius: 9999px;
        font-weight: 700;
    }
    
    /* Ajustes visuales de controles */
    div.stSlider > div[data-baseweb="slider"] > div > div {
        background-color: #4f46e5 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA (Datos Simulados) ---
INITIAL_INVESTMENT = 11739010000 

def get_historical_data():
    dates = pd.date_range(start='2021-01-01', end='2025-12-31', freq='M')
    base_revenue = 120000000 
    trend = np.linspace(0, 50000000, len(dates))
    seasonality = np.sin(np.linspace(0, 8*np.pi, len(dates))) * 30000000
    values = base_revenue + trend + seasonality + np.random.normal(0, 5000000, len(dates))
    df = pd.DataFrame({'date': dates, 'value': values})
    df['year'] = df['date'].dt.year
    return df

def generate_projections(ipc_rate, growth_factor, years_to_project, last_real_monthly_avg):
    future_dates = pd.date_range(start='2026-01-0
