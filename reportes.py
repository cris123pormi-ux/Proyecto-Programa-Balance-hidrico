import matplotlib.pyplot as plt
import seaborn as sns
import os

def graficar_curva_consumo_y_fuga(df_datos, nombre_nodo, ruta_salida="reportes/"):
    """
    Genera una gráfica comparativa del consumo a lo largo de las 24 horas,
    resaltando visualmente si ocurrió una anomalía o fuga simulada.
    """
    if not os.path.exists(ruta_salida):
        os.makedirs(ruta_salida)
        
    plt.figure(figsize=(10, 5))
    sns.set_theme(style="whitegrid")
    
    # Filtrar datos del nodo específico
    df_nodo = df_datos[df_datos['id_punto'] == nombre_nodo]
    
    # Graficar la línea de consumo en metros cúbicos por segundo
    plt.plot(df_nodo['timestamp'], df_nodo['caudal_simulado_m3s'], 
             label='Caudal Registrado (m³/s)', color='royalblue', linewidth=2.5, marker='o')
    
    # Resaltar en rojo las horas donde el estado es de Alerta por Fuga
    df_fuga = df_nodo[df_nodo['estado_sensor'] == 'ALERTA_FUGA_SIMULADA']
    if not df_fuga.empty:
        plt.scatter(df_fuga['timestamp'], df_fuga['caudal_simulado_m3s'], 
                    color='crimson', s=100, zorder=5, label='Fuga / Anomalía Detectada')
        
    plt.title(f"Gemelo Digital Girardot - Monitoreo de Caudal: {nombre_nodo}", fontsize=14, fontweight='bold')
    plt.xlabel("Hora del Día", fontsize=12)
    plt.ylabel("Caudal (m³/s)", fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(loc="upper left")
    plt.tight_layout()
    
    # Guardar gráfica
    archivo_final = os.path.join(ruta_salida, f"reporte_caudal_{nombre_nodo}.png")
    plt.savefig(archivo_final, dpi=300)
    plt.close()
    print(f"📊 Gráfica de caudales guardada exitosamente en: {archivo_final}")

def generar_resumen_presiones_criticas(serie_presiones, umbral_critico=15.0, ruta_salida="reportes/"):
    """
    Analiza las presiones calculadas por EPANET y genera un histograma, 
    alertando si la presión cae por debajo del umbral mínimo regulado (en metros de columna de agua - mca).
    """
    if not os.path.exists(ruta_salida):
        os.makedirs(ruta_salida)
        
    plt.figure(figsize=(8, 4))
    
    # Crear un histograma de las presiones de toda la red urbana
    sns.histplot(serie_presiones, kde=True, color='seagreen', bins=15)
    
    # Línea roja indicando la presión mínima reglamentaria en Colombia
    plt.axvline(x=umbral_critico, color='red', linestyle='--', linewidth=2, 
                label=f'Presión Mínima Requerida ({umbral_critico} mca)')
    
    plt.title("Distribución de Presiones en la Red de Distribución de Girardot", fontsize=12, fontweight='bold')
    plt.xlabel("Presión (mca - Metros de Columna de Agua)", fontsize=10)
    plt.ylabel("Cantidad de Nodos", fontsize=10)
    plt.legend()
    plt.tight_layout()
    
    archivo_final = os.path.join(ruta_salida, "analisis_presiones_red.png")
    plt.savefig(archivo_final, dpi=300)
    plt.close()
    
    # Conteo analítico de fallas
    nodos_afectados = sum(serie_presiones < umbral_critico)
    print(f"📉 Alerta: {nodos_afectados} nodos presentan presiones por debajo del mínimo legal.")
    print(f"📊 Histograma de presiones guardado en: {archivo_final}")
