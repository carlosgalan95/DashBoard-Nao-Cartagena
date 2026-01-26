import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(
    page_title="Análisis de Inversión Hotelera",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyectamos CSS para replicar el estilo 'Slate/Indigo' de Tailwind
st.markdown("""
<style>
    /* Fondo general */
    .stApp {
        background-color: #f8fafc; /* slate-50 */
        font-family: 'sans-serif';
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #0f172a; /* slate-900 */
    }
    
    /* KPI Cards personalizadas */
    .kpi-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .kpi-title {
        font-size: 0.875rem;
        color: #64748b; /* slate-500 */
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a; /* slate-900 */
        margin-top: 0.5rem;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }
    
    /* Ajustes sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Botones y sliders */
    div.stSlider > div[data-baseweb="slider"] > div > div {
        background-color: #4f46e5 !important; /* indigo-600 */
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CONSTANTES Y LÓGICA FINANCIERA (Replicando utils/finance) ---
INITIAL_INVESTMENT = 1500000000  # Ejemplo: 1.5B COP

# Generamos datos históricos simulados (ya que no tenemos el archivo ./constants)
def get_historical_data():
    dates = pd.date_range(start='2021-01-01', end='2025-12-31', freq='M')
    # Simulamos una curva de crecimiento con estacionalidad
    base_revenue = 15000000 # 15M base mensual
    trend = np.linspace(0, 10000000, len(dates)) # Crecimiento lineal
    seasonality = np.sin(np.linspace(0, 8*np.pi, len(dates))) * 5000000 # Estacionalidad
    values = base_revenue + trend + seasonality + np.random.normal(0, 1000000, len(dates))
    
    df = pd.DataFrame({'date': dates, 'value': values})
    df['year'] = df['date'].dt.year
    return df

# Función de proyección
def generate_projections(ipc_rate, growth_factor, years_to_project, last_real_monthly_avg):
    future_dates = pd.date_range(start='2026-01-01', periods=years_to_project*12, freq='M')
    
   # Función de proyección
def generate_projections(ipc_rate, growth_factor, years_to_project, last_real_monthly_avg):
    future_dates = pd.date_range(start='2026-01-01', periods=years_to_project*12, freq='M')
    
    # Factores mensuales
    monthly_ipc = (1 + ipc_rate/100)**(1/12) - 1
    monthly_growth = (1 + growth_factor/100)**(1/12) - 1
    
    projections = []
    current_val = last_real_monthly_avg
    
    for date in future_dates:
        # Base de crecimiento
        current_val = current_val * (1 + monthly_ipc + monthly_growth)
        
        # Añadimos estacionalidad
        season_factor = np.sin((date.month / 12) * 2 * np.pi) * 0.15 # +/- 15% estacionalidad
        
        base_proj = current_val * (1 + season_factor)
        
        projections.append({
            'date': date,
            'year': date.year,
            'pessimistic': base_proj * 0.85, # Escenarios
            'moderate': base_proj,
            'optimistic': base_proj * 1.20
        })
        
    return pd.DataFrame(projections)

# Formateadores
def format_currency(val):
    return f"${val:,.0f}"

def format_percent(val):
    return f"{val*100:.2f}%"

# --- 3. ESTADO Y CONTROLADORES ---

# Cargar datos históricos
df_history = get_historical_data()
last_year_total = df_history[df_history['year'] == 2025]['value'].sum()
last_monthly_avg = df_history[df_history['year'] == 2025]['value'].mean()

# --- SIDEBAR (Panel de Control) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3009/3009489.png", width=50) # Icono Hotel Dummy
    st.title("Panel de Control")
    st.caption("Ajuste de variables macroeconómicas")
    
    st.divider()
    
    ipc_rate = st.slider("IPC Anual Esperado (%)", 0.0, 15.0, 4.5, 0.1, help="Ajuste de inflación para tarifas")
    growth_factor = st.slider("Crecimiento Orgánico (%)", -5.0, 10.0, 2.0, 0.5, help="Mejora en ocupación")
    years_to_project = st.slider("Años de Proyección", 1, 25, 10, 1)
    
    st.divider()
    
    st.subheader("Visualización")
    col_view1, col_view2 = st.columns(2)
    view_mode = col_view1.radio("Unidad", ["$ COP", "% Rend"], index=0, label_visibility="collapsed")
    time_granularity = col_view2.radio("Frecuencia", ["Anual", "Mensual"], index=0, label_visibility="collapsed")

# --- CÁLCULOS PRINCIPALES ---
df_proj = generate_projections(ipc_rate, growth_factor, years_to_project, last_monthly_avg)

# Agregación según granularidad
if time_granularity == "Anual":
    # Agrupar historia
    chart_hist = df_history.groupby('year')['value'].sum().reset_index()
    chart_hist['date'] = chart_hist['year'].astype(str)
    
    # Agrupar proyección
    chart_proj = df_proj.groupby('year')[['pessimistic', 'moderate', 'optimistic']].sum().reset_index()
    chart_proj['date'] = chart_proj['year'].astype(str)
    
    div_factor = 1 # Para cálculos de ROI
else:
    chart_hist = df_history.copy()
    chart_proj = df_proj.copy()
    div_factor = 12

# KPIs calculados
avg_yield = last_year_total / INITIAL_INVESTMENT
cumulative_rev = df_proj['moderate'].sum()
cumulative_yield = cumulative_rev / INITIAL_INVESTMENT

# --- 4. INTERFAZ PRINCIPAL ---

# Header
c1, c2 = st.columns([3, 1])
with c1:
    st.title("Análisis de Inversión Hotelera")
    st.caption("Rentabilidad y Proyecciones Dinámicas (Portado a Python)")
with c2:
    st.metric(label="Inversión Inicial", value=format_currency(INITIAL_INVESTMENT))

st.markdown("---")

# Sección KPI (Grid layout)
k1, k2, k3, k4 = st.columns(4)

def kpi_card(col, title, value, subtitle):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)

kpi_card(k1, "Ingresos Reales (2025)", format_currency(last_year_total), "Cierre último año histórico")
kpi_card(k2, "Rendimiento Actual", format_percent(avg_yield), "ROI actual vs Inversión")
kpi_card(k3, f"Proyección Final ({2025 + years_to_project})", 
         format_currency(chart_proj.iloc[-1]['moderate']), "Escenario Moderado")
kpi_card(k4, f"Total Acumulado (2026+)", format_currency(cumulative_rev), 
         f"Rentabilidad: {format_percent(cumulative_yield)}")

st.markdown("---")

# --- GRÁFICOS (Plotly en lugar de Recharts) ---
st.subheader("Proyección de Rentabilidad")

# Preparar datos para Plotly
fig = go.Figure()

# 1. Datos Históricos (Línea sólida)
# Si es modo porcentaje, dividimos por inversión inicial
y_hist = chart_hist['value'] if view_mode == "$ COP" else chart_hist['value'] / INITIAL_INVESTMENT
fig.add_trace(go.Scatter(
    x=chart_hist['date'], y=y_hist,
    mode='lines', name='Real',
    line=dict(color='#4f46e5', width=4),
    fill='tozeroy', fillcolor='rgba(79, 70, 229, 0.1)'
))

# 2. Proyecciones
y_opt = chart_proj['optimistic'] if view_mode == "$ COP" else chart_proj['optimistic'] / INITIAL_INVESTMENT
y_mod = chart_proj['moderate'] if view_mode == "$ COP" else chart_proj['moderate'] / INITIAL_INVESTMENT
y_pes = chart_proj['pessimistic'] if view_mode == "$ COP" else chart_proj['pessimistic'] / INITIAL_INVESTMENT

# Pesimista (Línea punteada roja)
fig.add_trace(go.Scatter(
    x=chart_proj['date'], y=y_pes,
    mode='lines', name='Pesimista',
    line=dict(color='#ef4444', width=2, dash='dash')
))

# Moderado (Línea sólida verde)
fig.add_trace(go.Scatter(
    x=chart_proj['date'], y=y_mod,
    mode='lines', name='Moderado',
    line=dict(color='#10b981', width=3)
))

# Optimista (Línea + Área ambar)
fig.add_trace(go.Scatter(
    x=chart_proj['date'], y=y_opt,
    mode='lines', name='Optimista',
    line=dict(color='#f59e0b', width=2),
    fill='tonexty', fillcolor='rgba(245, 158, 11, 0.1)' # Relleno suave hacia la traza anterior
))

fig.update_layout(
    xaxis_title="Período",
    yaxis_title=view_mode,
    template="plotly_white",
    hovermode="x unified",
    margin=dict(l=20, r=20, t=20, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)



# --- TABLA DE DATOS ---
st.subheader("Tabla Detallada")

# Formatear el DataFrame para mostrar
display_df = chart_proj.copy()
display_df = display_df[['date', 'pessimistic', 'moderate', 'optimistic']]
display_df.columns = ['Período', 'Esc. Pesimista', 'Esc. Moderado', 'Esc. Optimista']

# Configuración de columnas para st.dataframe (Novedad de Streamlit)
column_config = {
    "Período": st.column_config.TextColumn("Período"),
    "Esc. Pesimista": st.column_config.NumberColumn(
        "Pesimista", format="$%d" if view_mode == "$ COP" else "%.2f%%"
    ),
    "Esc. Moderado": st.column_config.NumberColumn(
        "Moderado", format="$%d" if view_mode == "$ COP" else "%.2f%%"
    ),
    "Esc. Optimista": st.column_config.NumberColumn(
        "Optimista", format="$%d" if view_mode == "$ COP" else "%.2f%%"
    ),
}

# Si estamos en modo porcentaje, transformar datos antes de mostrar
if view_mode == "% Rend":
    cols = ['Esc. Pesimista', 'Esc. Moderado', 'Esc. Optimista']
    display_df[cols] = (display_df[cols] / INITIAL_INVESTMENT)

st.dataframe(
    display_df,
    column_config=column_config,
    use_container_width=True,
    hide_index=True,
    height=400
)

# Footer
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 12px; margin-top: 50px;">
    © 2025 Dashboard Hotelero (Versión Python/Streamlit). Datos de Alta Precisión.
</div>

""", unsafe_allow_html=True)

