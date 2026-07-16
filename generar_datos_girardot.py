import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generar_patron_demanda_diaria(id_punto, fecha_inicio="2026-07-16"):
    """
    Genera una serie de tiempo de 24 horas de consumo de agua (m3/s)
    para un nodo específico en Girardot, simulando la curva real de la ciudad.
    """
    # Patrón típico de consumo urbano:
    # Pico a las 7 AM (baño/desayuno), bajón a mediodía, pico menor a las 7 PM.
    horas = list(range(24))
    multiplicadores_base = [
        0.4, 0.3, 0.3, 0.4, 0.6, 0.8,  # Madrugada (0-5)
        1.2, 1.4, 1.3, 1.1, 1.0, 0.9,  # Mañana / Pico temprano (6-11)
        1.0, 1.1, 1.0, 0.9, 0.9, 1.0,  # Tarde (12-17)
        1.3, 1.2, 1.1, 0.9, 0.7, 0.5   # Noche / Pico nocturno (18-23)
    ]
    
    # Caudal medio base asignado a este nodo (por ejemplo, 0.010 m3/s o 10 Litros/segundo)
    caudal_medio = np.random.uniform(0.005, 0.025)
    
    registros = []
    fecha_base = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    
    for h in horas:
        timestamp = fecha_base + timedelta(hours=h)
        
        # Aplicar el multiplicador con un pequeño ruido aleatorio del 5% (variación del mundo real)
        ruido = np.random.normal(0, 0.05)
        caudal_simulado = caudal_medio * multiplicadores_base[h] * (1 + ruido)
        
        registros.append({
            "timestamp": timestamp,
            "id_punto": id_punto,
            "caudal_simulado_m3s": max(0.0, round(caudal_simulado, 5)),
            "estado_sensor": "SINTETICO"
        })
        
    return pd.DataFrame(registros)

def simular_evento_fuga_girardot(df_demandas, id_nodo_critico, hora_fuga=14):
    """
    Modifica la serie de tiempo para simular una ruptura de tubería o fuga masiva
    a partir de una hora determinada, inyectando una pérdida constante de caudal.
    """
    df_fuga = df_demandas.copy()
    
    # Simular una pérdida de 15 Litros por segundo (0.015 m3/s) debido a la ruptura
    magnitud_fuga = 0.015 
    
    for idx, fila in df_fuga.iterrows():
        if fila['id_punto'] == id_nodo_critico and fila['timestamp'].hour >= hora_fuga:
            df_fuga.at[idx, 'caudal_simulado_m3s'] += magnitud_fuga
            df_fuga.at[idx, 'estado_sensor'] = "ALERTA_FUGA_SIMULADA"
            
    return df_fuga
