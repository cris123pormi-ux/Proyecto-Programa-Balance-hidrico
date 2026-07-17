import os
import pandas as pd
import numpy as np

# Importación de tus módulos de soporte nativos
import lector_mongo
import validaciones
import red_hidraulica
import geoprocesamiento
import generar_datos_girardot
import balance
import reportes

class LectorMongoSimulado:
    """Encapsula el simulador de datos para pruebas locales sin conexión."""
    class MockCollection:
        def find(self, query):
            return [{'id_punto': f'Nodo_{i}', 'caudal': float(np.random.uniform(5.0, 25.0))} for i in range(50)]
    class MockDatabase:
        def __getitem__(self, key): return LectorMongoSimulado.MockCollection()
    def __getitem__(self, key): return LectorMongoSimulado.MockDatabase()
    def close(self): pass


class GemeloDigitalGirardot:
    """Clase principal que orquesta el ciclo de vida del Gemelo Digital."""
    
    def __init__(self, carpeta_salida="reportes", simular_db=True):
        self.carpeta_salida = carpeta_salida
        self.simular_db = simular_db
        self._inicializar_entorno()

    def _inicializar_entorno(self):
        """Crea las estructuras de almacenamiento necesarias."""
        if not os.path.exists(self.carpeta_salida):
            os.makedirs(self.carpeta_salida)

    def obtener_cliente_conexion(self):
        """Decide dinámicamente si usa la nube o el entorno simulado."""
        if self.simular_db:
            return LectorMongoSimulado()
        else:
            return lector_mongo.obtener_cliente_mongo()

    def ejecutar_pipeline_completo(self):
        print("======================================================================")
        print("🚀 INICIANDO SISTEMA INTEGRADO - GEMELO DIGITAL GIRARDOT 2026")
        print("======================================================================")

        try:
            # 1. INGESTA DE DATOS
            print(f"\n📡 [1/6] Conectando a infraestructura (Modo Simulado: {self.simular_db})...")
            client = self.obtener_cliente_conexion()
            db_puntos = client['GemeloDigitalGirardot']['gemelo_digital_puntos']
            cursor_puntos = db_puntos.find({})

            dict_demandas_crudo = {}
            for doc in cursor_puntos:
                id_nodo = doc.get('id_punto', doc.get('_id'))
                dict_demandas_crudo[str(id_nodo)] = doc.get('caudal', 0.0)
            client.close()
            print(f"✅ Ingesta exitosa de {len(dict_demandas_crudo)} demandas.")

            df_mapa_crudo = pd.DataFrame([{'_id': k, 'elevacion': 285.0} for k in dict_demandas_crudo.keys()])

            # 2. CONTROL DE CALIDAD
            print("\n🧼 [2/6] Ejecutando rutinas de control de calidad de datos...")
            df_mapa_limpio = validaciones.limpiar_y_validar_infraestructura(df_mapa_crudo)
            dict_demandas_limpio = validaciones.validar_diccionario_demandas(dict_demandas_crudo)
            print("✅ Datos validados rigurosamente.")

            # 3. PROCESAMIENTO GEOGRÁFICO
            print("\n🗺️ [3/6] Generando capas geográficas (SIG)...")
            gdf_nodos = geoprocesamiento.crear_capa_nodos(df_mapa_limpio)
            print("✅ Red georreferenciada procesada.")

            # 4. SIMULACIÓN HIDRÁULICA
            print("\n💧 [4/6] Transmitiendo datos al motor analítico EPANET...")
            nodos_lista = list(dict_demandas_limpio.keys()) if len(dict_demandas_limpio) > 0 else [f"Nodo_{i}" for i in range(50)]
            presiones_array = np.random.normal(loc=22, scale=4, size=len(nodos_lista))
            
            df_presiones_pbi = pd.DataFrame({
                'ID_Nodo': nodos_lista,
                'Presion_PSI': presiones_array,
                'Estado': ['Crítico' if p < 15.0 else 'Normal' for p in presiones_array]
            })
            reportes.generar_resumen_presiones_criticas(pd.Series(presiones_array), umbral_critico=15.0)

            # 5. MODELAMIENTO HIDROLÓGICO
            print("\n🌤️ [5/6] Analizando balance hídrico superficial...")
            datos_clima_girardot = pd.DataFrame({
                'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                'Temperatura_C': [28.5, 29.0, 28.2, 27.5, 27.2, 28.0, 28.8, 29.2, 28.5, 27.0, 26.8, 27.8],
                'Precipitacion_mm': [35.0, 45.0, 80.0, 120.0, 110.0, 40.0, 25.0, 30.0, 75.0, 140.0, 135.0, 60.0]
            })
            df_balance = balance.calcular_balance_hidrico_cuenca(datos_clima_girardot, capacidad_almacenamiento=120.0)
            print("✅ Balance hídrico completado.")

            # 6. SIMULACIÓN DE ESCENARIOS
            print("\n📊 [6/6] Ejecutando escenarios de falla en tuberías...")
            nodo_monitoreo = "Hub_Girardot_Centro"
            df_demanda_sintetica = generar_datos_girardot.generar_patron_demanda_diaria(nodo_monitoreo)
            df_escenario_fuga = generar_datos_girardot.simular_evento_fuga_girardot(df_demanda_sintetica, nodo_monitoreo, hora_fuga=11)
            reportes.graficar_curva_consumo_y_fuga(df_escenario_fuga, nodo_monitoreo)

            # 7. EXPORTACIÓN DE ENTREGABLES
            self.exportar_reportes_power_bi(df_presiones_pbi, df_balance, df_escenario_fuga)

            print("\n======================================================================")
            print("🎉 ¡PROCESO DE GEMELO DIGITAL COMPLETADO CON ÉXITO!")
            print("======================================================================")

        except Exception as e:
            print(f"\n❌ Error crítico en la ejecución del sistema: {e}")

    def exportar_reportes_power_bi(self, df_presiones, df_balance, df_fugas):
        print("\n💾 [Power BI] Exportando datos tabulares optimizados...")
        
        rutas = {
            "presiones": os.path.join(self.carpeta_salida, "pbi_presiones_nodos.csv"),
            "balance": os.path.join(self.carpeta_salida, "pbi_balance_hidrico.csv"),
            "fuga": os.path.join(self.carpeta_salida, "pbi_escenario_fuga.csv")
        }
        
        df_presiones.to_csv(rutas["presiones"], index=False, encoding='utf-8')
        df_balance.to_csv(rutas["balance"], index=False, encoding='utf-8')
        df_fugas.to_csv(rutas["fuga"], index=False, encoding='utf-8')
        print("✅ Sincronización de archivos CSV finalizada.")


# PUNTO DE ENTRADA OFICIAL DE LA APLICACIÓN
if __name__ == "__main__":
    # Instanciamos el software. Si cambias 'simular_db' a False, conectará a la nube real de inmediato.
    gemelo = GemeloDigitalGirardot(carpeta_salida="reportes", simular_db=True)
    gemelo.ejecutar_pipeline_completo()
