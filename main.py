import lector_mongo
import generar_datos_girardot
import red_hidraulica
import pandas as pd

def simular_contingencia_en_la_red():
    print("🤖 Iniciando entorno de pruebas y simulación de fallas...")
    
    # 1. Creamos datos sintéticos para un nodo de Girardot (ej: Hub_Terminal_Transportes)
    nodo_prueba = "Hub_Terminal"
    print(f"Generando curva de demanda base de 24 horas para: {nodo_prueba}")
    df_consumo_normal = generar_datos_girardot.generar_patron_demanda_diaria(nodo_prueba)
    
    # 2. Inyectamos una fuga a las 2:00 PM (Hora 14) para ver qué pasa con la presión
    print("💥 Inyectando simulación de ruptura de tubería a las 14:00 horas...")
    df_con_fuga = generar_datos_girardot.simular_evento_fuga_girardot(df_consumo_normal, nodo_prueba, hora_fuga=14)
    
    # Imprimir las últimas horas para validar el incremento de caudal
    print(df_con_fuga[['timestamp', 'caudal_simulado_m3s', 'estado_sensor']].tail(12))
    
    # 3. Aquí pasarías este DataFrame con sobrecosto de caudal a tu red_hidraulica
    # para verificar analíticamente cuánta presión cae en los barrios aledaños de Girardot.
    print("✅ Datos de contingencia listos para el estrés del motor hidráulico.")

if __name__ == "__main__":
    simular_contingencia_en_la_red()
