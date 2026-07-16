import pandas as pd

def ejecutar_balance_hidrico_universal(df, col_map, agua_planta, consumo_operativo):
    col_estrato = col_map['col_estrato']
    col_estado_tec = col_map['col_estado_tec']
    df['Estrato_Limpio'] = df[col_estrato].fillna('1').astype(str).str.strip().str.slice(0, 1).str.upper() if col_estrato in df.columns else '1'
    df['Estado_Tec_Limpio'] = df[col_estado_tec].fillna('NORMAL').astype(str).str.strip().str.upper() if col_estado_tec in df.columns else 'NORMAL'
    
    filtro_estrato = df['Estrato_Limpio'].str.contains('MUNICIPAL|NACIONAL|DEPARTAMENTAL|PILA|PUBLICA|OFICIAL', case=False, na=False)
    filtro_estado = df['Estado_Tec_Limpio'].str.contains('CONTROL|MED GRAL|GRAL|CASTIGO|CARTERA', case=False, na=False)
    filtro_especiales = filtro_estrato | filtro_estado
    
    df_no_normales = df[filtro_especiales].copy()
    df_normales = df[~filtro_especiales].copy()
    
    consumo_normales = df_normales['Consumo_Sincerado_Metrologico'].sum()
    consumo_especiales = df_no_normales['Consumo_Sincerado_Metrologico'].sum()
    volumen_total_contabilizado = consumo_normales + consumo_especiales + consumo_operativo
    perdidas_reales_m3 = agua_planta - volumen_total_contabilizado
    
    indicadores = {
        'consumo_normales': consumo_normales, 'consumo_especiales': consumo_especiales,
        'volumen_total_contabilizado': volumen_total_contabilizado, 'perdidas_reales_m3': perdidas_reales_m3,
        'ianc': (perdidas_reales_m3 / agua_planta) * 100, 'filas_normales': len(df_normales),
        'filas_especiales': len(df_no_normales), 'total_filas_originales': len(df)
    }
    return df_normales, df_no_normales, indicadores
