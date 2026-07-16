import pandas as pd
import numpy as np

def aplicar_sinceramiento_metrologico(df, col_map, fecha_auditoria, edad_limite, factor_anual):
    col_fecha = col_map['col_fecha_inst']
    if col_fecha and col_fecha in df.columns:
        df['Fecha_Instalacion_Limpia'] = pd.to_datetime(df[col_fecha], errors='coerce')
        df['Edad_Medidor_Anos'] = (pd.to_datetime(fecha_auditoria) - df['Fecha_Instalacion_Limpia']).dt.days / 365.25
        df['Edad_Medidor_Anos'] = df['Edad_Medidor_Anos'].fillna(edad_limite).clip(lower=0)
    else:
        df['Edad_Medidor_Anos'] = edad_limite
    df['Factor_Subregistro'] = np.where(df['Edad_Medidor_Anos'] > edad_limite, (df['Edad_Medidor_Anos'] - edad_limite) * factor_anual, 0)
    df['Consumo_Sincerado_Metrologico'] = df['Consumo_Mes_Exacto'] * (1 + df['Factor_Subregistro'])
    return df
