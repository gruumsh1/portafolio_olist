import pandas as pd
import streamlit as st
import plotly.express as px  # Nueva librería para gráficos interactivos

st.set_page_config(page_title="Dashboard Logístico Olist", layout="wide")

@st.cache_data 
def cargar_y_limpiar_datos():
    # Cargar los CSV base
    orders = pd.read_csv('olist_orders_dataset.csv')
    items = pd.read_csv('olist_order_items_dataset.csv')
    reviews = pd.read_csv('olist_order_reviews_dataset.csv')
    sellers = pd.read_csv('olist_sellers_dataset.csv')
    
    # 1. CARGAR LA TABLA DE PRODUCTOS (Nueva)
    productos = pd.read_csv('olist_products_dataset.csv')
    
    fechas = [
        'order_purchase_timestamp', 
        'order_approved_at', 
        'order_delivered_carrier_date', 
        'order_delivered_customer_date', 
        'order_estimated_delivery_date'
    ]
    for col in fechas:
        orders[col] = pd.to_datetime(orders[col])
        
    # 2. UNIONES DE CONJUNTOS (Agregamos productos al flujo)
    df_merged = pd.merge(orders, items, on='order_id', how='inner')
    df_merged = pd.merge(df_merged, sellers[['seller_id', 'seller_state']], on='seller_id', how='inner')
    
    # Cruzamos con productos para traer 'product_weight_g'
    df_merged = pd.merge(df_merged, productos[['product_id', 'product_weight_g']], on='product_id', how='inner')
    
    df_merged = pd.merge(df_merged, reviews[['order_id', 'review_score']], on='order_id', how='left')
    df_final = df_merged[df_merged['order_status'] == 'delivered'].copy()
    
    # --- CÁLCULO DE MÉTRICAS OPERATIVAS ---
    df_final['dias_envio_real'] = (df_final['order_delivered_customer_date'] - df_final['order_purchase_timestamp']).dt.days
    df_final['desviacion_dias'] = (df_final['order_delivered_customer_date'] - df_final['order_estimated_delivery_date']).dt.days
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


from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

st.markdown("---")
st.subheader("🔮 Módulo de Ciencia de Datos: Predicción de Retrasos en Envíos")
st.markdown("Utilizando un modelo matemático de **Regresión Logística** entrenado con los datos históricos de peso de la plataforma.")

if 'product_weight_g' in df.columns:
    # Limpiamos filas con nulos en las columnas que usará el modelo
    df_ml = df[['product_weight_g', 'estado_entrega']].dropna().copy()
    
    # Variable objetivo binaria: 1 = Retraso, 0 = A Tiempo
    df_ml['target'] = df_ml['estado_entrega'].apply(lambda x: 1 if x == 'Con Retraso' else 0)
    
    # Tomamos una muestra balanceada/óptima para agilizar el entrenamiento en el servidor web
    df_sample = df_ml.sample(n=30000, random_state=42) if df_ml.shape[0] > 30000 else df_ml
    
    X = df_sample[['product_weight_g']]
    y = df_sample['target']
    
    # División del espacio muestral (70% Entrenamiento, 30% Prueba)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Ajuste del modelo matemático
    modelo = LogisticRegression()
    modelo.fit(X_train, y_train)
    
    # --- Interfaz del Simulador en Vivo ---
    st.markdown("### Simulador de Riesgo Operativo")
    st.markdown("Modifica el peso del artículo para recalcular la probabilidad de fallo logístico basada en el modelo entrenado:")
    
    peso_input = st.slider("Peso del paquete en gramos (g):", min_value=50, max_value=25000, value=1200, step=50)
    
    # Predicción probabilística real
    probabilidad = modelo.predict_proba([[peso_input]])[0][1]
    
    st.metric(label="Probabilidad Real de Retraso Estimada", value=f"{probabilidad * 100:.2f}%")
    
    if probabilidad > 0.15: # Umbral basado en la distribución del dataset
        st.error("⚠️ Alerta de Distribución: El peso del producto incrementa significativamente la probabilidad de retraso en la entrega corporativa.")
    else:
        st.success("✅ Logística Segura: El peso del paquete se encuentra dentro de los márgenes óptimos de cumplimiento de tiempos.")