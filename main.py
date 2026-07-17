import os
import sys
import json
import pandas as pd
import numpy as np

# AUTO-ENRUTADOR DE SEGURIDAD
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importación de los módulos analíticos reales de la arquitectura HydroAI-Pro
from src.lector_excel import cargar_y_mapear_excel_universal
from src.validaciones import limpiar_y_tipificar_datos_universales
from src.consumo import calcular_consumo_exacto_universal
from src.metrologia import aplicar_sinceramiento_metrologico
from src.balance import ejecutar_balance_hidrico_universal
from src.geoprocesamiento import integrar_gemelo_digital
from src.reportes import generar_mapa_interactivo_girardot
import src.lector_mongo as lector_mongo

class LectorMongoSimulado:
    """Encapsula el simulador de datos para pruebas locales sin conexión."""
    class MockCollection:
        def find(self, query):
            return [{
                '_id': f'Mock_ID_{i}',
                'type': 'Feature',
                'properties': {'id_nodo': f'Nodo_{i}', 'elevacion': 285.0, 'caudal': 12.5, 'barrio': 'Urb Brisas de Girardot'},
                'geometry': {'coordinates': [-74.805, 4.328]}
            } for i in range(50)]
    class MockDatabase:
        def __getitem__(self, key): return LectorMongoSimulado.MockCollection()
    def __getitem__(self, key): return LectorMongoSimulado.MockDatabase()
    def close(self): pass

class GemeloDigitalGirardot:
    """Clase principal que orquesta el ciclo de vida del Gemelo Digital en HydroAI-Pro."""
    
    def __init__(self, ruta_config="config.json"):
        self.ruta_config = ruta_config
        self.config = self._cargar_configuracion()
        self.carpeta_salida = self.config["rutas"]["carpeta_salida"]
        self.simular_db = self.config["MONGO_SETTINGS"]["MODO_SIMULADO"]
        self._inicializar_entorno()

    def _cargar_configuracion(self):
        """Lee el archivo de configuración externo config.json compatible con Streamlit."""
        if not os.path.exists(self.ruta_config):
            config_defecto = {
                "MONGO_SETTINGS": {
                    "USUARIO": "render_user",
                    "BD_NAME": "GemeloDigitalGirardot",
                    "COLECCION": "gemelo_digital_puntos",
                    "MODO_SIMULADO": False
                },
                "rutas": {
                    "archivo_entrada": "data/auditoria_ingreso.xlsx",
                    "carpeta_salida": "reportes",
                    "logs": "logs/auditoria.log"
                },
                "parametros_oficiales": {
                    "fecha_auditoria": "2026-01-01"
                },
                "umbrales_metrologia": {
                    "edad_limite_anos": 10,
                    "factor_subregistro_anual": 0.02
                }
            }
            with open(self.ruta_config, "w", encoding="utf-8") as f:
                json.dump(config_defecto, f, indent=4, ensure_ascii=False)
            return config_defecto
        
        with open(self.ruta_config, "r", encoding="utf-8") as f:
            return json.load(f)

    def _inicializar_entorno(self):
        """Crea las estructuras de almacenamiento necesarias en el sistema."""
        if not os.path.exists(self.carpeta_salida):
            os.makedirs(self.carpeta_salida)

    def obtener_cliente_conexion(self):
        """Decide dinámicamente si usa MongoDB Atlas real o el entorno simulado."""
        if self.simular_db:
            return LectorMongoSimulado()
        else:
            return lector_mongo.obtener_cliente_mongo(usuario="render_user", password="Girardot2026")

    def ejecutar_pipeline_completo(self, agua_planta=1500000, consumo_operativo=12000, limite_anomalo=300):
        print("======================================================================")
        print("🚀 INICIANDO BACKEND INTEGRADO - HYDROAI-PRO / GIRARDOT 2026")
        print("======================================================================")

        try:
            # 1. INGESTA Y CRUCE GEOJSON DESDE ATLAS
            print(f"\n📡 [1/5] Descargando infraestructura estructural (Modo Simulado: {self.simular_db})...")
            client = self.obtener_cliente_conexion()
            
            # Descarga del mapa físico
            cursor_mapa = client['Mapa']['mapa hidraulico'].find({})
            registros_mapa_hidraulico = []
            
            for doc in cursor_mapa:
                properties = doc.get('properties', {})
                geometry = doc.get('geometry', {})
                coordenadas = geometry.get('coordinates', [-74.805, 4.328])
                
                registros_mapa_hidraulico.append({
                    '_id': str(properties.get('id_nodo', doc.get('_id'))),
                    'elevacion': float(properties.get('elevacion', 285.0)),
                    'barrio': properties.get('barrio', 'Urb Brisas de Girardot'),
                    'longitud': float(coordenadas[0]) if len(coordenadas) > 0 else -74.805,
                    'latitud': float(coordenadas[1]) if len(coordenadas) > 1 else 4.328
                })
            client.close()
            print(f"✅ Ingesta exitosa: {len(registros_mapa_hidraulico)} nodos cargados desde la base de datos 'Mapa'.")

            # 2. PROCESAMIENTO DEL CORE COMERCIAL (EXCEL DE AUDITORÍA)
            print("\n📊 [2/5] Procesando registros comerciales de auditoría...")
            df, col_map = cargar_y_mapear_excel_universal(self.config['rutas']['archivo_entrada'])
            df = limpiar_y_tipificar_datos_universales(df, col_map)
            df = calcular_consumo_exacto_universal(df, limite_anomalo)
            
            # 3. SINCERAMIENTO METROLÓGICO (EDAD DE MEDIDORES)
            print("\n🧼 [3/5] Aplicando modelos analíticos de subregistro y desgaste...")
            df = aplicar_sinceramiento_metrologico(
                df, col_map, 
                self.config['parametros_oficiales']['fecha_auditoria'], 
                self.config['umbrales_metrologia']['edad_limite_anos'], 
                self.config['umbrales_metrologia']['factor_subregistro_anual']
            )

            # 4. BALANCE HÍDRICO GLOBAL E INTEGRACIÓN CON EL GEMELO DIGITAL
            print("\n💧 [4/5] Ejecutando balance hídrico y acoplamiento geoespacial...")
            df_norm, df_esp, ind = ejecutar_balance_hidrico_universal(df, col_map, agua_planta, consumo_operativo)
            
            # Cruce de la auditoría comercial con los datos físicos GeoJSON de Brisas de Girardot
            df_mapa_fisi = pd.DataFrame(registros_mapa_hidraulico)
            df_gemelo = pd.merge(df_norm, df_mapa_fisi, left_on=col_map['id_cuenta'], right_on='_id', how='left')

            # 5. GENERACIÓN DE REPORTES E INTERFACES VISUALES
            print("\n💾 [5/5] Exportando capas cartográficas y tabulares...")
            generar_mapa_interactivo_girardot(df_gemelo, col_map, self.carpeta_salida)
            
            # Exportación de conveniencia para Power BI
            df_gemelo.to_csv(os.path.join(self.carpeta_salida, "pbi_gemelo_digital.csv"), index=False, encoding='utf-8')
            
            print("\n======================================================================")
            print(f"🎉 ¡PIPELINE EXITOSO! IANC OPTIMIZADO: {ind['ianc']:.2f}%")
            print("======================================================================")

        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO EN EL BACKEND: {str(e)}")

if __name__ == "__main__":
    gemelo = GemeloDigitalGirardot()
    gemelo.ejecutar_pipeline_completo()
