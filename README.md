# 📦 Análisis Analítico e Inferencial de E-Commerce (Logística y Satisfacción)

Este proyecto desarrolla una aplicación web interactiva de Inteligencia de Negocios (BI) y analítica avanzada utilizando **Python, Streamlit y Plotly**, corriendo sobre un entorno optimizado en Linux. El objetivo es transformar datos crudos transaccionales en *insights* accionables para la optimización de cadenas de suministro y retención de clientes.

## 🎯 Objetivos del Negocio
* **Evaluación del Rendimiento Logístico:** Medir el impacto real de los tiempos de entrega frente a las promesas de la plataforma.
* **Análisis de Satisfacción:** Identificar la tasa de tolerancia del consumidor ante retrasos en la distribución antes de castigar la calificación del servicio.
* **Segmentación Geográfica:** Permitir a los tomadores de decisiones filtrar el comportamiento de la cadena de suministro por estado y temporalidad.

## 📊 Arquitectura del Modelo de Datos (Enfoque Relacional)
A partir de los datos crudos del *Olist Brazilian E-Commerce Dataset*, se estructuró un **Modelo Dimensional (Esquema en Estrella)** para optimizar el procesamiento en memoria:
* **Tabla de Hechos (Fact Table):** Fusión de registros de órdenes y artículos entregados, actuando como el núcleo de las métricas cuantitativas.
* **Tablas de Dimensión (Dimension Tables):** Catálogos lógicos de Vendedores (`seller_state`) y Calificaciones (`review_score`).

## 🧮 Fundamentos Matemáticos y Estadísticos Aplicados
Para evitar las métricas superficiales (como promedios simples sesgados por valores atípicos), el análisis incorpora rigor analítico:
* **Control de Variación:** Cálculo de desviaciones temporales absolutas ($Días\ Reales - Días\ Estimados$) para aislar anomalías operativas.
* **Análisis Estadístico del Consumidor:** Modelado de la curva de decaimiento de la satisfacción para identificar el punto de inflexión donde la lealtad del cliente se quiebra debido a fallas logísticas.

## 🛠️ Tecnologías Utilizadas
* **Sistema Operativo:** Entorno Linux (Parrot OS / KDE Plasma)
* **Lenguaje:** Python 3.x
* **Librerías Clave:** * `pandas` (Operaciones de conjuntos, limpieza y *data wrangling* vectorizado).
  * `streamlit` (Estructuración de la aplicación reactiva en la capa de presentación).
  * `plotly.express` (Gráficos interactivos interactuando con el estado del DataFrame).

## 🚀 Cómo Ejecutar el Proyecto Localmente

1. Clona este repositorio:
   ```bash
   git clone [https://github.com/TU_USUARIO/portafolio_olist.git](https://github.com/gruumsh1/portafolio_olist.git)
   cd portafolio_olist
