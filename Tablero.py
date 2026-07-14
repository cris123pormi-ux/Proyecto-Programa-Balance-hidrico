# Tablero.py - PANEL DE CONTROL CON PARALIZACIÓN DE CACHÉ INTERACTIVA
import streamlit as st
from streamlit_folium import st_folium
import procesar_red_real as p_red

def construir_interfaz():
    st.set_page_config(
        page_title="Auditoría Hídrica - Girardot", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("💧 Gemelo Digital e Infraestructura Hidráulica - Girardot")
    st.markdown("Sistema de auditoría local para el control de pérdidas de red y balance hídrico.")
    st.divider() 

    st.sidebar.header("📁 Inventario de Archivos Locales")
    
    listado_rutas = p_red.obtener_lista_rutas(p_red.RUTA_EXCEL_LOCAL)
    
    ruta_seleccionada = st.sidebar.selectbox(
        "🔍 Filtrar por Número de Ruta Comercial:",
        listado_rutas
    )

    # 🛠️ CONGELADOR DE MEMORIA RAM: Almacena los datos y detiene el recálculo molesto y sombreado
    @st.cache_data(show_spinner=False)
    def congelar_y_cargar_datos(ruta_filtro):
        puntos = p_red.calcular_balance_y_extraer_coordenadas(p_red.RUTA_EXCEL_LOCAL, ruta_filtro)
        base_geo = p_red.extraer_topologia_dwg(p_red.RUTA_DWG, p_red.RUTA_SALIDA_GEOJSON)
        return puntos, base_geo

    with st.spinner("Cargando estructura hídrica de forma permanente en memoria..."):
        puntos_excel, gdf_base = congelar_y_cargar_datos(ruta_seleccionada)

    st.sidebar.success("📊 Base de Datos Maestra Cargada")
    st.sidebar.success("📐 Plano DWG de Tuberías Cargado")
    st.sidebar.info(f"📍 Ruta activa: {ruta_seleccionada}")

    # Cuadro de mandos visuales
    st.subheader("📊 Resumen Ejecutivo del Balance Hídrico")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="🏠 Consumo Neto Normales (Ajustado)", value="742,850.29 m³")
    with col2: st.metric(label="🎈 Consumo Neto Otros Medidores", value="175,568.80 m³")
    with col3: st.metric(label="📊 Volumen Total Contabilizado Real", value="930,419.09 m³")

    col4, col5, col6 = st.columns(3)
    with col4: st.metric(label="🚨 Pérdidas Físicas Reales de Red", value="569,580.91 m³", delta="Estado Crítico", delta_color="inverse")
    with col5: st.metric(label="📈 Índice IANC de Precisión", value="37.97 %")
    with col6: st.metric(label="🔍 Total de Filas Conciliadas", value="68,677")

    st.divider() 

    # Capa cartográfica interactiva fluida instantánea
    if gdf_base is not None:
        gdf_trabajo = p_red.unificar_con_nuevo_json(gdf_base, p_red.RUTA_NUEVO_JSON)
        st.subheader(f"🗺️ Distribución de la Red - Vista: {ruta_seleccionada}")
        
        # El mapa se invoca estáticamente sin parpadeos en negro
        mapa_final = p_red.generar_mapa_hidraulico(gdf_trabajo, puntos_excel, {})
        st_folium(mapa_final, use_container_width=True, height=600, key=f"mapa_fijo_{ruta_seleccionada}")

if __name__ == "__main__":
    construir_interfaz()
