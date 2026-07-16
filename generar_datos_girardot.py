import pandas as pd
import numpy as np
import os

def crear_excel_simulado():
    print("🌍 Generando universo geoespacial de medidores para Girardot...")
    
    np.random.seed(42) # Estabilidad de datos
    n_registros = 50
    
    # 1. Coordenadas reales dentro de la caja geográfica de Girardot
    latitudes = np.random.uniform(4.295, 4.315, n_registros)
    longitudes = np.random.uniform(-74.815, -74.795, n_registros)
    
    # 2. Casos de negocio y anomalías simuladas
    ids = list(range(1001, 1001 + n_registros))
    
    # Valores base por defecto (Comportamiento Normal)
    lec_abr = np.random.randint(100, 500, n_registros)
    lec_may = lec_abr + np.random.randint(10, 25, n_registros)
    lec_jun = lec_may + np.random.randint(10, 25, n_registros)
    consumo_fac = lec_jun - lec_may
    
    observaciones = ["LECTURA NORMAL"] * n_registros
    estratos = np.random.choice(["1 - BAJO BAJO", "2 - BAJO", "3 - MEDIO BAJO", "4 - MEDIO"], n_registros)
    estados = ["CON SERVICIO"] * n_registros
    fechas_inst = np.random.choice(["2016-05-20", "2018-11-14", "2022-01-10", "2025-03-15"], n_registros)

    # Inyección forzada de Anomalías de Campo para validar tus alertas:
    # Caso A: Fraude Potencial / Lectura Negativa (ID 1005)
    lec_jun[4] = lec_may[4] - 15  
    consumo_fac[4] = 10
    
    # Caso B: Medidor Frenado / Consumo cero sospechoso (ID 1012)
    lec_abr[11] = 320
    lec_may[11] = 320
    lec_jun[11] = 320
    consumo_fac[11] = 0
    
    # Caso C: Alto Consumo / Fuga invisible en Estrato Bajo (ID 1025)
    estratos[24] = "1 - BAJO BAJO"
    lec_jun[24] = lec_may[24] + 85  # Consumo real 85m3
    consumo_fac[24] = 85
    
    # Caso D: Cambio de Medidor Exitoso (ID 1030)
    lec_may[29] = 980
    lec_jun[29] = 12  # Vuelta a cero
    consumo_fac[29] = 12
    observaciones[29] = "MEDIDOR CAMBIADO"

    # 3. Construcción del DataFrame comercial
    datos = {
        "SUSCRIPTOR": ids,
        "LEC ABRIL 2026": lec_abr,
        "LEC MAYO 2026": lec_may,
        "LEC JUNIO 2026": lec_jun,
        "CONSUMO": consumo_fac,
        "ANOMALIA": observaciones,
        "NIVEL": estratos,
        "CONDICION": estados,
        "FECHA_MEDIDOR": fechas_inst,
        "LATITUD": latitudes,
        "LONGITUD": longitudes
    }
    
    df = pd.DataFrame(datos)
    
    # Guardar en la raíz
    ruta_salida = "datos_facturacion_campo.xlsx"
    df.to_excel(ruta_salida, index=False)
    print(f"✨ Archivo '{ruta_salida}' generado con éxito con {n_registros} medidores.")

if __name__ == "__main__":
    crear_excel_simulado()
