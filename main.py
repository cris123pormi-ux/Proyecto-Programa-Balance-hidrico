import lector_mongo
import validaciones
import red_hidraulica
import geoprocesamiento
import pandas as pd

def flujo_con_mapeo_geografico():
    print("🛰️ Descargando datos de Girardot desde MongoDB Atlas...")
    client = lector_mongo.obtener_cliente_mongo()
    df_mapa_crudo = pd.DataFrame(list(client['Mapa']['mapa hidraulico'].find({})))
    client.close()
    
    # 1. Limpieza técnica
    df_mapa_limpio = validaciones.limpiar_y_validar_infraestructura(df_mapa_crudo)
    
    # 2. PROCESAMIENTO GEOGRÁFICO
    print("🗺️ Construyendo capas espaciales para el Gemelo Digital...")
    gdf_nodos = geoprocesamiento.crear_capa_nodos(df_mapa_limpio)
    gdf_tuberias = geoprocesamiento.crear_capa_tuberias(df_mapa_limpio, gdf_nodos)
    
    print(f"📊 Capas GIS listas: {len(gdf_nodos)} nodos y {len(gdf_tuberias)} tuberías georreferenciadas.")
    
    # Aquí ya podrías exportar tus capas a formato GeoJSON o Shapefile para visualizarlas en un mapa web:
    # gdf_tuberias.to_file("tuberias_girardot.geojson", driver="GeoJSON")

if __name__ == "__main__":
    flujo_con_mapeo_geografico()
