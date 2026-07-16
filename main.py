"""
Proyecto: Gemelo Digital de Balance Hídrico - Girardot
Archivo: main.py
Descripción: Orquestador principal que integra la ingesta de datos desde MongoDB,
             limpieza de datos, procesamiento SIG, simulación hidráulica y reportes.
"""

import os
import pandas as pd
import numpy as np

# Importación de los módulos de la arquitectura del proyecto
import lector_mongo
import validaciones
import red_hidraulica
import geoprocesamiento
import generar_datos_girardot
import balance
import reportes

def ejecutar_gemelo_digital_completo():
    print("======================================================================")
    print("🚀 INICIANDO SISTEMA INTEGRADO - GEMELO DIGITAL GIRARDOT 2026")
    print("======================================================================")
    
    # Directorio para almacenar las salidas visuales
    carpeta_reportes = "reportes"
    if not os.path.exists(carpeta_reportes):
        os.makedirs(carpeta_reportes)

    try:
        # ==========================================
        # PASO 1: CONEXIÓN E INGESTA DESDE LA NUBE
        # ==========================================
        print("\n📡 [1/6] Conectando a MongoDB Atlas como 'render_user'...")
        client = lector_mongo.obtener_cliente_mongo()
        
        # Descarga de la infraestructura de red física de acueducto
        db_mapa = client['Mapa']['mapa hidraulico']
        df_mapa_crudo = pd.DataFrame(list(db_mapa.find({})))
        
        # Descarga de los puntos de monitoreo de caudal y consumo
        db_puntos = client['GemeloDigitalGirardot']['gemelo_digital_puntos']
        cursor_puntos = db_puntos.find({})
        
        dict_demandas_crudo = {}
        for doc in cursor_puntos:
            id_nodo = doc.get('id_punto', doc.get('_id'))
            dict_demandas_crudo[str(id_nodo)] = doc.get('caudal', 0.0)
            
        client.close()
        print(f"✅ Descarga exitosa: {len(df_mapa_crudo)} elementos de red y {len(dict_demandas_crudo)} demandas.")

        # ==========================================
        # PASO 2: CONTROL DE CALIDAD Y VALIDACIONES
        # ==========================================
        print("\n🧼 [2/6] Ejecutando rutinas de control de calidad de datos...")
        df_mapa_limpio = validaciones.limpiar_y_validar_infraestructura(df_mapa_crudo)
        dict_demandas_limpio = validaciones.validar_diccionario_demandas(dict_demandas_crudo)
        print("✅ Consistencia y tipos de datos validados correctamente.")

        # ==========================================
        # PASO 3: PROCESAMIENTO GEOGRÁFICO (SIG)
        # ==========================================
        print("\n🗺️ [3/6] Generando capas geográficas del Gemelo Digital...")
        gdf_nodos = geoprocesamiento.crear_capa_nodos(df_mapa_limpio)
        gdf_tuberias = geoprocesamiento.crear_capa_tuberias(df_mapa_limpio, gdf_nodos)
        
        if not gdf_nodos.empty and not gdf_tuberias.empty:
            print(f"✅ Red georreferenciada en EPSG:9377 ({len(gdf_nodos)} nodos, {len(gdf_tuberias)} líneas).")
            # Opcional: gdf_tuberias.to_file(os.path.join(carpeta_reportes, "red_acueducto.geojson"), driver="GeoJSON")

        # ==========================================
        # PASO 4: SIMULACIÓN HIDRÁULICA (EPANET / WNTR)
        # ==========================================
        print("\n💧 [4/6] Transmitiendo datos al motor analítico EPANET...")
        presiones, caudales = red_hidraulica.construir_y_simular_red_desde_mongo(df_mapa_limpio, dict_demandas_limpio)
        
        # En caso de no contar con la red completa en Mongo, se corre la prueba sintética
        if presiones is None:
            print("⚠️ Red incompleta en la nube. Corriendo análisis hidráulico con datos de contingencia...")
            presiones_simuladas = pd.Series(np.random.normal(loc=22, scale=4, size=50))
            reportes.generar_resumen_presiones_criticas(presiones_simuladas, umbral_critico=15.0)
        else:
            print("✅ Simulación hidráulica resuelta con éxito.")
            reportes.generar_resumen_presiones_criticas(presiones, umbral_critico=15.0)

        # ==========================================
        # PASO 5: MODELAMIENTO HIDROLÓGICO (BALANCE)
        # ==========================================
        print("\n🌤️ [5/6] Analizando balance hídrico de la cuenca superficial...")
        # Datos meteorológicos anuales consolidados para la región de Girardot
        datos_clima_girardot = pd.DataFrame({
            'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            'Temperatura_C': [28.5, 29.0, 28.2, 27.5, 27.2, 28.0, 28.8, 29.2, 28.5, 27.0, 26.8, 27.8],
            'Precipitacion_mm': [35.0, 45.0, 80.0, 120.0, 110.0, 40.0, 25.0, 30.0, 75.0, 140.0, 135.0, 60.0]
        })
        df_balance = balance.calcular_balance_hidrico_cuenca(datos_clima_girardot, capacidad_almacenamiento=120.0)
        print("✅ Balance secuencial de Thornthwaite finalizado.")

        # ==========================================
        # PASO 6: SIMULACIÓN DE ESCENARIOS Y REPORTES
        # ==========================================
        print("\n📊 [6/6] Ejecutando simulación de escenarios de falla y gráficos...")
        nodo_monitoreo = "Hub_Girardot_Centro"
        
        # Generar datos de simulación con falla por fuga de tubería
        df_demanda_sintetica = generar_datos_girardot.generar_patron_demanda_diaria(nodo_monitoreo)
        df_escenario_fuga = generar_datos_girardot.simular_evento_fuga_girardot(df_demanda_sintetica, nodo_monitoreo, hora_fuga=11)
        
        # Exportación de reportes gráficos finales
        reportes.graficar_curva_consumo_y_fuga(df_escenario_fuga, nodo_monitoreo)
        
        print("\n======================================================================")
        print("🎉 ¡PROCESO DE GEMELO DIGITAL COMPLETADO CON ÉXITO!")
        print(f"Los resultados gráficos se han almacenado en la carpeta: /'{carpeta_reportes}'")
        print("======================================================================")

    except Exception as e:
        print(f"\n❌ Error crítico durante la orquestación del programa: {e}")

if __name__ == "__main__":
    ejecutar_gemelo_digital_completo()
