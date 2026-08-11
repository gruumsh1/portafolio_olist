import pandas as pd
import streamlit as st
import plotly.express as px  # Nueva librería para gráficos interactivos

st.set_page_config(page_title="Dashboard Logístico Olist", layout="wide")

@st.cache_data 
def cargar_y_limpiar_datos():
    orders = pd.read_csv('olist_orders_dataset.csv')
    items = pd.read_csv('olist_order_items_dataset.csv')
    reviews = pd.read_csv('olist_order_reviews_dataset.csv')
    
    fechas = [
        'order_purchase_timestamp', 
        'order_approved_at', 
        'order_delivered_carrier_date', 
        'order_delivered_customer_date', 
        'order_estimated_delivery_date'
    ]
    for col in fechas:
        orders[col] = pd.to_datetime(orders[col])
        
    sellers = pd.read_csv('olist_sellers_dataset.csv')
    df_merged = pd.merge(orders, items, on='order_id', how='inner')
    df_merged = pd.merge(df_merged, sellers[['seller_id', 'seller_state']], on='seller_id', how='inner')
    df_merged = pd.merge(df_merged, reviews[['order_id', 'review_score']], on='order_id', how='left')
    df_final = df_merged[df_merged['order_status'] == 'delivered'].copy()
    
    # --- CÁLCULO DE MÉTRICAS OPERATIVAS ---
    # 1. Días reales de envío (Fecha de entrega - Fecha de compra)
    df_final['dias_envio_real'] = (df_final['order_delivered_customer_date'] - df_final['order_purchase_timestamp']).dt.days
    
    # 2. Desviación logística (Días reales - Días estimados por el e-commerce)
    # Valores positivos implican retraso; valores negativos implican entregas anticipadas.
    df_final['desviacion_dias'] = (df_final['order_delivered_customer_date'] - df_final['order_estimated_delivery_date']).dt.days
    
    # 3. Clasificación booleana / categórica de la entrega
    df_final['estado_entrega'] = df_final['desviacion_dias'].apply(lambda x: 'Con Retraso' if x > 0 else 'A Tiempo')
    
    return df_final

# --- INTERFAZ Y NARRATIVA DE NEGOCIO ---
st.title("📦 Análisis de E-Commerce (Logística y Satisfacción)")
st.markdown("Evaluación del impacto del rendimiento de entrega en la experiencia del usuario final.")

with st.spinner("Procesando y uniendo registros..."):
    df = cargar_y_limpiar_datos()

# --- BARRA LATERAL PARA FILTROS (SIDEBAR) ---
st.sidebar.header("🎛️ Filtros de Análisis")

# 1. Filtro Geográfico por Estado del Vendedor (Cruzando datos lógicos)
# Primero cargamos rápido la tabla de vendedores para obtener los estados (UF)
@st.cache_data
def obtener_estados():
    vendedores = pd.read_csv('olist_sellers_dataset.csv')
    return sorted(vendedores['seller_state'].unique())

estados_disponibles = obtener_estados()
estados_seleccionados = st.sidebar.multiselect(
    "Selecciona los Estados del Vendedor:",
    options=estados_disponibles,
    default=estados_disponibles[:5] # Dejamos 5 por defecto para no saturar al inicio
)

# 2. Filtro por Año de Compra
df['ano_compra'] = df['order_purchase_timestamp'].dt.year
anos_disponibles = sorted(df['ano_compra'].unique())
anos_seleccionados = st.sidebar.multiselect(
    "Selecciona el Año de Compra:",
    options=anos_disponibles,
    default=anos_disponibles
)

# --- APLICACIÓN DE FILTROS A LA TABLA DE HECHOS ---
# Usamos operadores booleanos para filtrar el DataFrame principal en memoria
df_filtrado = df[
    (df['seller_state'].isin(estados_seleccionados)) & 
    (df['ano_compra'].isin(anos_seleccionados))
]

# --- BLOQUE DE KEY PERFORMANCE INDICATORS (KPIs) ---
# Cambiamos 'df' por 'df_filtrado' para que las métricas respondan a los filtros
col1, col2, col3, col4 = st.columns(4)

total_ordenes = df_filtrado['order_id'].nunique()
tiempo_promedio = df_filtrado['dias_envio_real'].mean()
satisfaccion_promedio = df_filtrado['review_score'].mean()

ordenes_retrasadas = df_filtrado[df_filtrado['estado_entrega'] == 'Con Retraso']['order_id'].nunique()
# Validación matemática para evitar división por cero si el filtro vacía el dataset
porcentaje_retraso = (ordenes_retrasadas / total_ordenes) * 100 if total_ordenes > 0 else 0

with col1:
    st.metric("Total Órdenes", f"{total_ordenes:,}")
with col2:
    st.metric("Tiempo de Entrega Promedio", f"{tiempo_promedio:.1f} días")
with col3:
    st.metric("Satisfacción Promedio", f"{satisfaccion_promedio:.2f} ⭐")
with col4:
    st.metric("Tasa de Retraso Operativo", f"{porcentaje_retraso:.1f}%", delta=f"{porcentaje_retraso:.1f}%", delta_color="inverse")

st.markdown("---")

# --- BLOQUE DE ANÁLISIS VISUAL ---
st.subheader("📊 Relación entre Logística y Calificación del Cliente (Datos Filtrados)")

col_izq, col_der = st.columns(2)

with col_izq:
    st.markdown("**Distribución de Satisfacción según Estado de Entrega**")
    if total_ordenes > 0:
        df_agrupado = df_filtrado.groupby('estado_entrega')['review_score'].mean().reset_index()
        fig_bar = px.bar(
            df_agrupado, 
            x='estado_entrega', 
            y='review_score',
            color='estado_entrega',
            color_discrete_map={'A Tiempo': '#2ecc71', 'Con Retraso': '#e74c3c'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")

with col_der:
    st.markdown("**¿Cuántos días de retraso tolera el cliente antes de castigar la calificación?**")
    df_retrasos = df_filtrado[(df_filtrado['desviacion_dias'] > 0) & (df_filtrado['desviacion_dias'] <= 30)]
    if not df_retrasos.empty:
        df_dias = df_retrasos.groupby('desviacion_dias')['review_score'].mean().reset_index()
        fig_line = px.line(
            df_dias, 
            x='desviacion_dias', 
            y='review_score',
            title="Tendencia de Satisfacción por Días de Retraso"
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No hay registros con retraso para este segmento.")