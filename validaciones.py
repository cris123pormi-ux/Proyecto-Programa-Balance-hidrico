import pandas as pd
import numpy as np

def limpiar_y_validar_infraestructura(df_mapa):
    """
    Verifica que el mapa hidráulico descargado contenga los campos requeridos
    y limpia valores nulos o formatos incorrectos.
    """
    if df_mapa.empty:
        print("⚠️ El DataFrame de infraestructura está vacío.")
        return df_mapa

    # 1. Asegurar que existan identificadores únicos
    if '_id' in df_mapa.columns:
        df_mapa['_id'] = df_mapa['_id'].astype(str)
    
    # 2. Convertir y limpiar campos numéricos críticos para EPANET
    campos_numericos = ['diametro', 'longitud', 'rugosidad', 'elevacion']
    for campo in campos_numericos:
        if campo in df_mapa.columns:
            # Reemplazar nulos o texto corrupto por valores por defecto realistas
            df_mapa[campo] = pd.to_numeric(df_mapa[campo], errors='coerce')
    
    # Valores de contingencia (Rellenar vacíos con ingeniería básica)
    valores_defecto = {
        'diametro': 0.15,   # 150mm / 6 pulgadas estándar
        'longitud': 100.0,  # 100 metros por tramo
        'rugosidad': 100.0, # Coeficiente Hazen-Williams estándar (PVC/Hierro)
        'elevacion': 289.0  # Elevación media aproximada de Girardot
    }
    df_mapa.fillna(value=valores_defecto, inplace=True)
    
    return df_mapa

def validar_diccionario_demandas(diccionario_demandas):
    """
    Asegura que los caudales de los nodos sean numéricos, positivos 
    y maneja excepciones de lecturas atípicas (fugas masivas o errores de sensor).
    """
    demandas_limpias = {}
    for nodo, caudal in diccionario_demandas.items():
        try:
            caudal_float = float(caudal)
            # Evitar caudales negativos incoherentes
            if caudal_float < 0:
                caudal_float = 0.0
            # Detectar consumos desproporcionados (ej. más de 500 L/s en un solo punto)
            if caudal_float > 0.5: 
                print(f"⚠️ Alerta metrológica: Caudal sospechoso en {nodo}: {caudal_float} m³/s")
            
            demandas_limpias[str(nodo)] = caudal_float
        except (ValueError, TypeError):
            demandas_limpias[str(nodo)] = 0.0 # Consumo cero si el dato está roto
            
    return demandas_limpias
