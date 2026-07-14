import pandas as pd
import numpy as np
import sys

nombre_archivo = r"C:\Users\christian.godoy\Desktop\Copia de CONSUMOS JUNIO-2026.xlsm"

# Parámetros fijos oficiales de control hídrico (Acuagyr)
AGUA_PRODUCIDA_PLANTA = 1500000 
CONSUMO_TECNICO_OPERATIVO = 12000  
FECHA_AUDITORIA = pd.to_datetime('2026-06-30')

try:
    print("⏳ Ejecutando auditoría de precisión absoluta con histórico y metrología...")
    
    # Leer el archivo optimizando tipos de datos iniciales
    df = pd.read_excel(nombre_archivo, sheet_name='Hoja1', header=0)
    df.columns = df.columns.astype(str).str.strip()
    
    # 1. Mapeo estricto y flexible de columnas
    c_jun = 'LEC JUNIO' if 'LEC JUNIO' in df.columns else 'Lectura Le'
    c_may = 'LEC MAYO' if 'LEC MAYO' in df.columns else 'Lectura An'
    c_abr = 'LEC ABRIL' if 'LEC ABRIL' in df.columns else 'Lectura Am'
    
    col_facturar = 'Consumo a Facturar' if 'Consumo a Facturar' in df.columns else 'Consumo'
    col_observacion = 'OBSERVACION JUNIO' if 'OBSERVACION JUNIO' in df.columns else 'Observacion'
    col_estrato = 'Estrato' if 'Estrato' in df.columns else 'ESTRATO'
    col_estado_tec = 'Estado Técnico' if 'Estado Técnico' in df.columns else 'Estado Tecnico'
    
    # Buscador flexible para la fecha de instalación
    opciones_fecha = [c for c in df.columns if 'INSTALACION' in c.upper() or 'FECHA_INST' in c.upper() or 'INSTALACI' in c.upper()]
    col_fecha_inst = opciones_fecha[0] if opciones_fecha else 'Fecha de instalacion del med'

    # 2. Conversión estricta a datos numéricos y limpieza de texto
    df['L_JUN'] = pd.to_numeric(df[c_jun], errors='coerce').fillna(0)
    df['L_MAY'] = pd.to_numeric(df[c_may], errors='coerce').fillna(0)
    df['L_ABR'] = pd.to_numeric(df[c_abr], errors='coerce').fillna(0)
    df['FACTURADO_MES'] = pd.to_numeric(df[col_facturar], errors='coerce').fillna(0)
    
    df['OBS_CAMPO'] = 'LECTURA NORMAL'
    if col_observacion in df.columns:
        df['OBS_CAMPO'] = df[col_observacion].fillna('LECTURA NORMAL').astype(str).str.strip().str.upper()
    
    # 3. Cálculo de la resta física directa de junio
    df['Consumo_Mes_Exacto'] = df['L_JUN'] - df['L_MAY']
    
    # 4. REGLA DE INGENIERÍA AVANZADA (Detección de Anomalías)
    medidor_cambiado = (df['L_MAY'] < df['L_ABR']) & (df['L_ABR'] > 300)
    acceso_impedido = df['OBS_CAMPO'].str.contains('CERRADO|IMPEDIDO|NO PERMITIO|OBSTRUIDO', case=False, na=False)
    
    condicion_anomalia = (df['Consumo_Mes_Exacto'] < 0) | (df['Consumo_Mes_Exacto'] > 300) | medidor_cambiado | acceso_impedido
    df.loc[condicion_anomalia, 'Consumo_Mes_Exacto'] = df.loc[condicion_anomalia, 'FACTURADO_MES']
    df.loc[df['Consumo_Mes_Exacto'] < 0, 'Consumo_Mes_Exacto'] = 0

    # 5. OPTIMIZACIÓN METROLÓGICA (Edad del Medidor)
    if col_fecha_inst in df.columns:
        df['Fecha_Instalacion_Limpia'] = pd.to_datetime(df[col_fecha_inst], errors='coerce')
        df['Edad_Medidor_Anos'] = (FECHA_AUDITORIA - df['Fecha_Instalacion_Limpia']).dt.days / 365.25
        df['Edad_Medidor_Anos'] = df['Edad_Medidor_Anos'].fillna(5.0).clip(lower=0)
    else:
        df['Edad_Medidor_Anos'] = 5.0
    
    df['Factor_Subregistro'] = np.where(df['Edad_Medidor_Anos'] > 5, (df['Edad_Medidor_Anos'] - 5) * 0.015, 0)
    df['Consumo_Sincerado_Metrologico'] = df['Consumo_Mes_Exacto'] * (1 + df['Factor_Subregistro'])

    # 6. SEGMENTACIÓN LIMITADA A COLUMNAS ESPECÍFICAS
    df['Estrato_Limpio'] = df[col_estrato].fillna('1').astype(str).str.strip().str.upper() if col_estrato in df.columns else '1'
    df['Estado_Tec_Limpio'] = df[col_estado_tec].fillna('NORMAL').astype(str).str.strip().str.upper() if col_estado_tec in df.columns else 'NORMAL'
    
    terminos_estrato = 'MUNICIPAL|NACIONAL|DEPARTAMENTAL|PILA|PUBLICA'
    filtro_estrato = df['Estrato_Limpio'].str.contains(terminos_estrato, case=False, na=False)
    
    terminos_estado = 'CONTROL|MED GRAL|GRAL|CASTIGO|CARTERA'
    filtro_estado = df['Estado_Tec_Limpio'].str.contains(terminos_estado, case=False, na=False)
    
    filtro_especiales = filtro_estrato | filtro_estado
    
    df_no_normales = df[filtro_especiales].copy()
    df_normales = df[~filtro_especiales].copy()

    # 7. Balance de Cierre Definitivo
    consumo_normales = df_normales['Consumo_Sincerado_Metrologico'].sum()
    consumo_especiales = df_no_normales['Consumo_Sincerado_Metrologico'].sum()
    
    volumen_total_contabilizado = consumo_normales + consumo_especiales + CONSUMO_TECNICO_OPERATIVO
    perdidas_reales_m3 = AGUA_PRODUCIDA_PLANTA - volumen_total_contabilizado
    ianc_preciso = (perdidas_reales_m3 / AGUA_PRODUCIDA_PLANTA) * 100

    # Controles de integridad de filas
    filtas_totales_excel = len(df)
    total_filas_procesadas = len(df_normales) + len(df_no_normales)

    print("\n" + "🏁" * 25)
    print("      BALANCE HÍDRICO GLOBAL DE PRECISIÓN SEMESTRAL")
    print("🏁" * 25)
    print(f"🏭 Volumen Inyectado por la Planta:      {AGUA_PRODUCIDA_PLANTA:,} m³")
    print(f"🏠 Consumo Neto Normales (Ajustado):     {consumo_normales:,.2f} m³")
    print(f"📍 Consumo Neto Otros Medidores:         {consumo_especiales:,.2f} m³")
    print(f"🛠️ Consumo Técnico Operativo (Lavados):   {CONSUMO_TECNICO_OPERATIVO:,} m³")
    print(f"📊 VOLUMEN TOTAL CONTABILIZADO REAL:     {volumen_total_contabilizado:,.2f} m³")
    print("-" * 50)
    print(f"🚨 PÉRDIDAS FÍSICAS REALES DE RED:       {perdidas_reales_m3:,.2f} m³")
    print(f"📈 ÍNDICE IANC DE PRECISIÓN OPTIMIZADO:  {ianc_preciso:.2f}%")
    print("=" * 50)
    print("🔍 VERIFICACIÓN DE INTEGRIDAD DE LA BASE DE DATOS:")
    print(f"• Cuentas en Universo Normal:            {len(df_normales):,} filas")
    print(f"• Cuentas en Universo Especial:          {len(df_no_normales):,} filas")
    print(f"• Total de filas conciliadas:            {total_filas_procesadas:,} filas")
    print(f"• Desfase o registros perdidos:          {filtas_totales_excel - total_filas_procesadas} filas")
    print("==================================================")

except Exception as e:
    print(f"❌ Error crítico en el procesamiento: {e}", file=sys.stderr)
