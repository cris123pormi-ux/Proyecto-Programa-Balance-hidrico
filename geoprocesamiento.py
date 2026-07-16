import geopandas as gpd
from shapely.geometry import Point, LineString
import pandas as pd

def crear_capa_nodos(df_mapa):
    """
    Toma los puntos de infraestructura del mapa hidráulico y los convierte
    en una capa geoespacial (GeoDataFrame) de nodos.
    """
    # Suponiendo que tus documentos de MongoDB guardan la ubicación como 'latitud' y 'longitud'
    # o dentro de un objeto GeoJSON de tipo 'coordenadas'
    if 'longitud' not in df_mapa.columns or 'latitud' not in df_mapa.columns:
        print("⚠️ No se encontraron columnas explícitas de latitud/longitud en el mapa.")
        return gpd.GeoDataFrame()
    
    # 1. Crear geometrías de tipo Punto usando Shapely
    geometria = [Point(xy) for xy in zip(df_mapa['longitud'], df_mapa['latitud'])]
    
    # 2. Construir el GeoDataFrame asignando el sistema de coordenadas WGS84 (EPSG:4326)
    gdf_nodos = gpd.GeoDataFrame(df_mapa, geometry=geometria, crs="EPSG:4326")
    
    # 3. Proyectar a coordenadas métricas de Colombia (Origen Nacional EPSG:9377) 
    # Esto es crucial para poder calcular distancias y radios en metros exactos en Girardot
    gdf_nodos = gdf_nodos.to_crs(epsg=9377)
    
    return gdf_nodos

def crear_capa_tuberias(df_mapa, gdf_nodos):
    """
    Construye las líneas de las tuberías conectando geométricamente
    el 'nodo_inicio' con el 'nodo_fin'.
    """
    tuberias = []
    
    # Verificar que existan las conexiones topológicas en tus datos
    if 'nodo_inicio' not in df_mapa.columns or 'nodo_fin' not in df_mapa.columns:
        print("⚠️ No hay datos de conectividad topológica para trazar tuberías.")
        return gpd.GeoDataFrame()
    
    # Filtrar solo registros que actúen como enlaces/tuberías
    df_lineas = df_mapa[df_mapa['nodo_inicio'].notna() & df_mapa['nodo_fin'].notna()]
    
    # Indexar nodos por su ID para búsquedas ultra rápidas de coordenadas
    nodos_indexados = gdf_nodos.set_index('_id')
    
    for idx, fila in df_lineas.iterrows():
        id_ini = str(fila['nodo_inicio'])
        id_fin = str(fila['nodo_fin'])
        
        if id_ini in nodos_indexados.index and id_fin in nodos_indexados.index:
            # Extraer las coordenadas geográficas de ambos extremos
            punto_ini = nodos_indexados.loc[id_ini, 'geometry']
            punto_fin = nodos_indexados.loc[id_fin, 'geometry']
            
            # Crear la línea física que une los dos puntos
            linea_tuberia = LineString([punto_ini, punto_fin])
            tuberias.append({
                'id_tuberia': fila.get('_id'),
                'diametro': fila.get('diametro'),
                'geometry': linea_tuberia
            })
            
    gdf_tuberias = gpd.GeoDataFrame(tuberias, crs="EPSG:9377")
    return gdf_tuberias
