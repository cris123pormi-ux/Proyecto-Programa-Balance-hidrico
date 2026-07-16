import pandas as pd
import numpy as np

def calcular_indice_calor_anual(temperaturas_mensuales):
    """
    Calcula el índice de calor anual (I) requerido por Thornthwaite.
    temperaturas_mensuales: Lista o array con las 12 temperaturas medias del año.
    """
    # Evitar divisiones o valores negativos incoherentes en la fórmula exponencial
    temps = np.array(temperaturas_mensuales)
    temps = np.where(temps < 0, 0, temps)
    
    # Sumatoria de (t / 5)^1.514 para los 12 meses
    indice_i = np.sum((temps / 5.0) ** 1.514)
    return float(indice_i)

def calcular_etp_thornthwaite_mensual(temperatura_media, indice_calor_anual, correccion_luz=1.0):
    """
    Calcula la Evapotranspiración Potencial (ETP) sin corregir para un mes.
    correccion_luz: Factor de ajuste según la latitud de Girardot (~4.3° N) y duración del día.
    """
    if temperatura_media <= 0:
        return 0.0
        
    I = indice_calor_anual
    # Constante empírica 'a' del método de Thornthwaite
    a = (6.75e-7 * (I**3)) - (7.71e-5 * (I**2)) + (1.792e-2 * I) + 0.49239
    
    # Fórmula base para un mes estándar de 30 días y 12 horas de luz
    etp_base = 16.0 * ((10.0 * temperatura_media / I) ** a)
    
    # Retornar ETP ajustada por las condiciones climáticas del mes
    return round(etp_base * correccion_luz, 2)

def calcular_balance_hidrico_cuenca(df_clima, capacidad_almacenamiento=100.0):
    """
    Ejecuta el balance secuencial clásico del suelo.
    df_clima debe contener columnas: 'Precipitacion_mm' y 'Temperatura_C'
    """
    # 1. Obtener el índice de calor asumiendo la serie o un año típico de Girardot (~28°C promedio)
    if 'Temperatura_C' in df_clima.columns and len(df_clima) >= 12:
        I = calcular_indice_calor_anual(df_clima['Temperatura_C'].iloc[:12])
    else:
        # Valor de índice de calor típico calculado para el clima constante de Girardot
        I = 145.0 
        
    # 2. Calcular la ETP estimada si no viene calculada de la nube
    if 'ETP_mm' not in df_clima.columns:
        etp_calculada = []
        for _, fila in df_clima.iterrows():
            temp = fila.get('Temperatura_C', 28.0)
            etp_mes = calcular_etp_thornthwaite_mensual(temp, I)
            etp_calculada.append(etp_mes)
        df_clima['ETP_mm'] = etp_calculada

    # 3. Inicializar variables de balance de suelo
    almacenamiento = []
    alm_actual = capacidad_almacenamiento
    excesos = []
    deficits = []
    
    for idx, fila in df_clima.iterrows():
        p = fila['Precipitacion_mm']
        etp = fila['ETP_mm']
        balance_mes = p - etp
        
        if balance_mes >= 0:
            # Recarga del suelo
            alm_nuevo = min(capacidad_almacenamiento, alm_actual + balance_mes)
            exc = (alm_actual + balance_mes) - alm_nuevo
            defc = 0.0
        else:
            # Sequía / Consumo de reserva del suelo
            alm_nuevo = alm_actual * np.exp(balance_mes / capacidad_almacenamiento)
            exc = 0.0
            # El déficit es la demanda atmosférica que no pudo ser satisfecha
            etr = p + (alm_actual - alm_nuevo)
            defc = etp - etr
            
        almacenamiento.append(alm_nuevo)
        excesos.append(exc)
        deficits.append(defc)
        alm_actual = alm_nuevo
        
    df_resultado = df_clima.copy()
    df_resultado['Reserva_Suelo_mm'] = almacenamiento
    df_resultado['Exceso_Agua_mm'] = excesos
    df_resultado['Deficit_Agua_mm'] = deficits
    
    return df_resultado
