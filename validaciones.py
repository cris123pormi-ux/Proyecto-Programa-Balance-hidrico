import pandas as pd
import numpy as np

def auditar_consistencia_campo(df, col_map):
    """
    Analiza anomalías físicas y operativas en los datos de medidores.
    Retorna el DataFrame con banderas de alerta.
    """
    df_alertas = df.copy()
    
    # Garantizar la existencia de las columnas mapeadas en las series de control
    obs_series = df_alertas[col_map["col_observacion"]].fillna("").astype(str).str.upper()
    estrato_series = df_alertas[col_map["col_estrato"]].fillna("").astype(str)
    estado_series = df_alertas[col_map["col_estado_tec"]].fillna("").astype(str).str.upper()

    # 1. Alerta: Fraude Potencial o Error de Digitación
    condicion_bajada = (df_alertas[col_map["c_jun"]] < df_alertas[col_map["c_may"]])
    condicion_no_cambio = ~obs_series.str.contains("CAMBIADO", na=False)
    df_alertas["ALERTA_LECTURA_NEGATIVA"] = condicion_bajada & condicion_no_cambio
    
    # 2. Alerta: Medidor Frenado / Consumo Cero sospechoso
    df_alertas["ALERTA_MEDIDOR_FRENADO"] = (
        (df_alertas[col_map["c_jun"]] == df_alertas[col_map["c_may"]]) & 
        (df_alertas[col_map["c_may"]] == df_alertas[col_map["c_abr"]]) &
        (estado_series == "CON SERVICIO")
    )
    
    # 3. Alerta: Alto Consumo / Fuga Invisible (Consumo > 60 m³ en estratos bajos)
    df_alertas["ALERTA_FUGA_SOSP_E1_E2"] = (
        df_alertas[col_map["col_facturar"]] > 60
    ) & estrato_series.str.contains("1|2", regex=True)

    return df_alertas


def limpiar_y_tipificar_datos_universales(df, col_map):
    """
    Punto de entrada oficial para el pipeline de HydroAI Pro.
    Limpia tipos de datos y estabiliza dinámicamente columnas históricas ausentes.
    """
    df_limpio = df.copy()
    
    # 🚨 DETECTOR DE CONTINGENCIA EN CASCADA COMPLETO
    # Escenario A: Si Junio es virtual (no debería pasar), se inicializa en 0
    if "VIRTUAL" in str(col_map["c_jun"]):
        df_limpio[col_map["c_jun"]] = 0

    # Escenario B: Si Mayo es virtual, se genera una columna real llena con los datos de Junio
    if "VIRTUAL" in str(col_map["c_may"]):
        print("ℹ️ Nota: No se detectó histórico de Mayo en el archivo. Estabilizando columna virtual...")
        df_limpio["COL_VIRTUAL_C_MAY"] = df_limpio[col_map["c_jun"]]
        col_map["c_may"] = "COL_VIRTUAL_C_MAY"

    # Escenario C: Si Abril es virtual, se genera una columna real llena con los datos de Mayo (ya estabilizado)
    if "VIRTUAL" in str(col_map["c_abr"]):
        print("ℹ️ Nota: No se detectó histórico de Abril en el archivo. Estabilizando columna virtual...")
        df_limpio["COL_VIRTUAL_C_ABR"] = df_limpio[col_map["c_may"]]
        col_map["c_abr"] = "COL_VIRTUAL_C_ABR"

    # Homologación y tipificación de columnas críticas a numéricas de forma segura
    columnas_numericas = ["c_jun", "c_may", "c_abr", "col_facturar"]
    for col in columnas_numericas:
        df_limpio[col_map[col]] = pd.to_numeric(df_limpio[col_map[col]], errors='coerce').fillna(0)
        
    # Limpieza de fechas si es necesario
    df_limpio[col_map["col_fecha_inst"]] = pd.to_datetime(df_limpio[col_map["col_fecha_inst"]], errors='coerce')
    
    # Inyección automática de la auditoría de campo hídrica
    df_resultado = auditar_consistencia_campo(df_limpio, col_map)
    
    return df_resultado
