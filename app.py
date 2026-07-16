import streamlit as st
import os
import pandas as pd
from src.utilidades import cargar_configuracion, inicializar_logger
from src.lector_excel import cargar_y_mapear_excel_universal
from src.validaciones import limpiar_y_tipificar_datos_universales
from src.consumo import calcular_consumo_exacto_universal
from src.metrologia import aplicar_sinceramiento_metrologico
from src.balance import ejecutar_balance_hidrico_universal
from src.geoprocesamiento import integrar_gemelo_digital
from src.reportes import generar_mapa_interactivo_girardot

st.set_page_config(page_title="HydroAI-Pro - Gemelo Digital", page_icon="🏭", layout="wide")

st.title("🏭 HydroAI-Pro v2026")
st.subheader("Plataforma de Control Hídrico y Gemelo Digital de Girardot")
st.markdown("---")

st.sidebar.header("⚙️ Parámetros de Operación")
agua_planta = st.sidebar.number_input("Volumen Inyectado Planta (m³)", value=1500000, step=10000)
consumo_operativo = st.sidebar.number_input("Consumo Técnico Operativo (m³)", value=12000, step=1000)
limite_anomalo = st.sidebar.number_input("Límite Consumo Anómalo (m³)", value=300, step=50)

cfg = cargar_configuracion()
log = inicializar_logger(cfg['rutas']['logs'])

st.info("📂 Sistema listo para leer el archivo del Escritorio y cruzar con **MongoDB Atlas**.")

if st.button("🚀 Ejecutar Auditoría Global e Integrar Gemelo Digital", type="primary"):
    with st.spinner("Procesando algoritmos y conectando a la nube geoespacial..."):
        try:
            df, col_map = cargar_y_mapear_excel_universal(cfg['rutas']['archivo_entrada'])
            df = limpiar_y_tipificar_datos_universales(df, col_map)
            df = calcular_consumo_exacto_universal(df, limite_anomalo)
            df = aplicar_sinceramiento_metrologico(df, col_map, cfg['parametros_oficiales']['fecha_auditoria'], cfg['umbrales_metrologia']['edad_limite_anos'], cfg['umbrales_metrologia']['factor_subregistro_anual'])
            df_norm, df_esp, ind = ejecutar_balance_hidrico_universal(df, col_map, agua_planta, consumo_operativo)
            df_gemelo = integrar_gemelo_digital(df_norm, col_map, log, ruta_pem=None)
            
            generar_mapa_interactivo_girardot(df_gemelo, col_map, cfg['rutas']['carpeta_salida'])
            
            st.success("🏁 ¡Auditoría analítica completada con éxito!")
            col1, col2, col3 = st.columns(3)
            col1.metric("📉 Índice IANC Optimizado", f"{ind['ianc']:.2f}%")
            col2.metric("🚨 Pérdidas Reales de Red", f"{ind['perdidas_reales_m3']:,.2f} m³")
            col3.metric("📊 Total Consumido Real", f"{ind['volumen_total_contabilizado']:,.2f} m³")
            
            st.markdown("### 🔍 Vista Previa del Universo Conciliado (Gemelo Digital)")
            columnas_visibles = [col_map['id_cuenta'], 'Consumo_Mes_Exacto', 'Edad_Medidor_Anos', 'Consumo_Sincerado_Metrologico']
            columnas_visibles += [c for c in ['LATITUD', 'LONGITUD', 'DIRECCION', 'MEDIDOR'] if c in df_gemelo.columns]
            st.dataframe(df_gemelo[df_gemelo.columns.intersection(columnas_visibles)].head(100), use_container_width=True)
            
            ruta_mapa = os.path.join(cfg['rutas']['carpeta_salida'], "gemelo_digital_mapa.html")
            st.info(f"🗺️ El mapa interactivo geoespacial ha sido actualizado en: `{ruta_mapa}`")
        except Exception as e:
            st.error(f"💥 Error en el pipeline web: {e}")
