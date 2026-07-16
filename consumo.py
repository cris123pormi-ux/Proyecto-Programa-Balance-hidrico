import pandas as pd

def calcular_consumo_exacto_universal(df, limite_anomalo):
    df['Consumo_Mes_Exacto'] = df['L_JUN'] - df['L_MAY']
    medidor_cambiado = (df['Consumo_Mes_Exacto'] < 0) & (df['L_MAY'] < df['L_ABR'])
    acceso_impedido = df['OBS_CAMPO'].str.contains('CERRADO|IMPEDIDO|NO PERMITIO|OBSTRUIDO', case=False, na=False)
    medidor_danado = df['OBS_CAMPO'].str.contains('DESTRUIDO|DANADO|ROTO|TRABADO|PARADO|FRENADO', case=False, na=False)
    condicion_anomalia = (df['Consumo_Mes_Exacto'] < 0) | (df['Consumo_Mes_Exacto'] > limite_anomalo) | medidor_cambiado | acceso_impedido | medidor_danado
    df.loc[condicion_anomalia, 'Consumo_Mes_Exacto'] = df.loc[condicion_anomalia, 'FACTURADO_MES']
    df['Consumo_Mes_Exacto'] = df['Consumo_Mes_Exacto'].clip(lower=0)
    return df
