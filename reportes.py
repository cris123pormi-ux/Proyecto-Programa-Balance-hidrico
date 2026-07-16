import os
import folium
import pandas as pd
from folium.plugins import MarkerCluster

def imprimir_consola_balance(ind):
    total = ind['filas_normales'] + ind['filas_especiales']
    print("\n" + "🏁" * 25 + "\n      BALANCE HÍDRICO GLOBAL DE PRECISIÓN (HydroAI-Pro 2026)\n" + "🏁" * 25)
    print(f"🏠 Consumo Neto Normales (Ajustado):     {ind['consumo_normales']:,.2f} m³")
    print(f"📍 Consumo Neto Otros Medidores:         {ind['consumo_especiales']:,.2f} m³")
    print(f"📊 VOLUMEN TOTAL CONTABILIZADO REAL:     {ind['volumen_total_contabilizado']:,.2f} m³")
    print("-" * 50)
    print(f"🚨 PÉRDIDAS FÍSICAS REALES DE RED:       {ind['perdidas_reales_m3']:,.2f} m³")
    print(f"📈 ÍNDICE IANC DE PRECISIÓN OPTIMIZADO:  {ind['ianc']:.2f}%\n" + "=" * 50)

def exportar_universos(df_norm, df_esp, ruta_salida):
    os.makedirs(ruta_salida, exist_ok=True)
    df_norm.to_csv(os.path.join(ruta_salida, "universo_normales.csv"), index=False, encoding='utf-8-sig')
    df_esp.to_csv(os.path.join(ruta_salida, "universo_especiales.csv"), index=False, encoding='utf-8-sig')

def generar_mapa_interactivo_girardot(df_gemelo, col_map, ruta_salida):
    col_lat = [c for c in df_gemelo.columns if 'LAT' in c.upper() or 'Y' in c.upper()]
    col_lon = [c for c in df_gemelo.columns if 'LON' in c.upper() or 'X' in c.upper()]
    if not col_lat or not col_lon: return
    col_lat = col_lat[0]
    col_lon = col_lon[0]
    
    df_mapa = df_gemelo.dropna(subset=[col_lat, col_lon]).copy()
    df_mapa[col_lat] = pd.to_numeric(df_mapa[col_lat], errors='coerce')
    df_mapa[col_lon] = pd.to_numeric(df_mapa[col_lon], errors='coerce')
    df_mapa = df_mapa.dropna(subset=[col_lat, col_lon])
    
    mapa = folium.Map(location=[4.3050, -74.8014], zoom_start=14)
    cluster = MarkerCluster().add_to(mapa)
    
    for _, fila in df_mapa.head(2000).iterrows():
        obs = str(fila['OBS_CAMPO'])
        color = "orange" if "CERRADO" in obs else ("purple" if "DESTRUIDO" in obs else ("darkred" if fila['Factor_Subregistro'] > 0 else "blue"))
        popup_text = f"Contrato: {fila[col_map['id_cuenta']]}<br>Consumo: {fila['Consumo_Sincerado_Metrologico']:.1f} m³"
        folium.Marker(location=[fila[col_lat], fila[col_lon]], popup=popup_text, icon=folium.Icon(color=color)).add_to(cluster)
        
    os.makedirs(ruta_salida, exist_ok=True)
    mapa.save(os.path.join(ruta_salida, "gemelo_digital_mapa.html"))
