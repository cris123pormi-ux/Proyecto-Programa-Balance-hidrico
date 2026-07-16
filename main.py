import sys
import os
import pandas as pd

# Agregar la raíz del proyecto al PATH para evitar errores de importación
raiz = os.path.dirname(os.path.abspath(__file__))
if raiz not in sys.path:
    sys.path.insert(0, raiz)

from src.utilidades import cargar_configuracion, inicializar_logger
from src.lector_excel import cargar_y_mapear_excel_universal
from src.lector_mongo import cargar_datos_mongo_autoadaptable
from src.validaciones import limpiar_y_tipificar_datos_universales
from src.consumo import calcular_consumo_exacto_universal
from src.metrologia import aplicar_sinceramiento_metrologico
from src.balance import ejecutar_balance_hidrico_universal
from src.geoprocesamiento import integrar_gemelo_digital
from src.reportes import imprimir_consola_balance, exportar_universos, generar_mapa_interactivo_girardot

def ejecutar_pipeline():
    try:
        cfg = cargar_configuracion()
        log = inicializar_logger(cfg['rutas']['logs'])
    except Exception as e:
        print(f"❌ Error crítico inicializando configuraciones o logs: {e}", file=sys.stderr)
        sys.exit(1)

    log.info("🚀 Inicializando el sistema modular autoadaptable HydroAI-Pro Cloud...")
    print("\n🚀 Inicializando el sistema modular autoadaptable HydroAI-Pro Cloud...\n")
    
    try:
        # =====================================================================
        # 1. 🌐 Sincronización e Inteligencia Cloud (MongoDB Atlas)
        # =====================================================================
        
        # Diccionario semántico de campos esperados en los Hubs Logísticos
        mapa_campos_hubs = {
            'latitud': ['LATITUD', 'LAT', 'COORD_Y', 'Y'],
            'longitud': ['LONGITUD', 'LON', 'LNG', 'COORD_X', 'X'],
            'nombre': ['NOMBRE', 'HUB', 'CENTRO', 'DESCRIPCION']
        }
        
        df_hubs_cloud, hub_map = cargar_datos_mongo_autoadaptable(
            sinonimos_db=['GemeloDigitalGirardot', 'Gemelo', 'Girardot_Cloud'],
            sinonimos_col=['centros_logisticos_hubs', 'hubs', 'logistica', 'centros'],
            mapa_campos_esperados=mapa_campos_hubs
        )
        
        # Diccionario semántico de campos esperados en el Mapa Hidráulico
        mapa_campos_red = {
            'diametro': ['DIAMETRO', 'PULGADAS', 'DIAM', 'RED'],
            'material': ['MATERIAL', 'TIPO', 'PVC', 'HF', 'TUBERIA'],
            'estado': ['ESTADO', 'OPERACION', 'CONDICION']
        }
        
        df_mapa_cloud, red_map = cargar_datos_mongo_autoadaptable(
            sinonimos_db=['Mapa', 'Redes', 'Hidraulica'],
            sinonimos_col=['mapa hidraulico', 'red', 'tuberias', 'mapa'],
            mapa_campos_esperados=mapa_campos_red
        )

        # =====================================================================
        # 2. 📥 Ingesta Inteligente del Archivo de Facturación Local (.xlsm)
        # =====================================================================
        df, col_map = cargar_y_mapear_excel_universal(cfg['rutas']['archivo_entrada'])
        
        # 3. Limpieza de datos y resolución en cascada de meses ausentes
        df = limpiar_y_tipificar_datos_universales(df, col_map)
        
        # 4. Extracción segura de variables mapeadas para el núcleo analítico
        df["L_JUN"] = df[col_map["c_jun"]]
        df["L_MAY"] = df[col_map["c_may"]]
        df["L_ABR"] = df[col_map["c_abr"]]
        df["FACTURADO_MES"] = df[col_map["col_facturar"]]
        df["OBS_CAMPO"] = df[col_map["col_observacion"]].fillna("").astype(str).str.upper()
        
        # =====================================================================
        # 5. 🧮 Procesamiento de Ingeniería Hídrica y Metrología
        # =====================================================================
        df = calcular_consumo_exacto_universal(df, cfg['umbrales_metrologia']['limite_consumo_anomalo'])
        df = aplicar_sinceramiento_metrologico(
            df, col_map, 
            cfg['parametros_oficiales']['fecha_auditoria'], 
            cfg['umbrales_metrologia']['edad_limite_anos'], 
            cfg['umbrales_metrologia']['factor_subregistro_anual']
        )
        
        # =====================================================================
        # 6. 📐 Balance de Agua Nacional y Gemelo Digital de Girardot
        # =====================================================================
        df_norm, df_esp, indicadores = ejecutar_balance_hidrico_universal(
            df, col_map, 
            cfg['parametros_oficiales']['agua_producida_planta'], 
            cfg['parametros_oficiales']['consumo_tecnico_operativo']
        )
        
        # Inyectar la estructura del Gemelo Digital unificando datos locales y la nube
        df_gemelo = integrar_gemelo_digital(df_norm, col_map, log, ruta_pem=None)
        
        # =====================================================================
        # 7. 📊 Outputs y Mapas Interactivos Finales
        # =====================================================================
        imprimir_consola_balance(indicadores)
        exportar_universos(df_gemelo, df_esp, cfg['rutas']['carpeta_salida'])
        generar_mapa_interactivo_girardot(df_gemelo, col_map, cfg['rutas']['carpeta_salida'])
        
        log.info("🏁 Pipeline de auditoría hídrica autoadaptable finalizado con éxito absoluto.")
        print("\n🏁 Pipeline de auditoría hídrica autoadaptable finalizado con éxito absoluto.\n")
        
    except Exception as e:
        log.error("💥 Falla catastrófica no controlada en el motor modular de ejecución", exc_info=True)
        print(f"💥 Falla catastrófica en la ejecución: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_pipeline()
