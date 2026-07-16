import generar_datos_girardot
import reportes
import pandas as pd
import numpy as np

def flujo_con_generacion_de_reportes():
    print("🔄 Corriendo simulación interna de contingencia...")
    
    # 1. Obtenemos datos de prueba con una fuga simulada usando el módulo anterior
    nodo_test = "Hub_Girardot_Centro"
    df_base = generar_datos_girardot.generar_patron_demanda_diaria(nodo_test)
    df_fuga = generar_datos_girardot.simular_evento_fuga_girardot(df_base, nodo_test, hora_fuga=11)
    
    # 2. EJECUTAR EL GENERADOR DE REPORTES GRÁFICOS
    print("🎨 Generando componentes visuales del Gemelo Digital...")
    reportes.graficar_curva_consumo_y_fuga(df_fuga, nodo_test)
    
    # 3. Simular una serie ficticia de presiones de EPANET para probar el histograma
    # Simulamos 100 nodos con presiones aleatorias distribuidas normalmente alrededor de 22 mca
    presiones_simuladas = pd.Series(np.random.normal(loc=22, scale=5, size=100))
    reportes.generar_resumen_presiones_criticas(presiones_simuladas, umbral_critico=15.0)

if __name__ == "__main__":
    flujo_con_generacion_de_reportes()
