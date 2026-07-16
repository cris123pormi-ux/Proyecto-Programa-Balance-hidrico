import pandas as pd
import sys
import difflib
from pymongo import MongoClient

# Cadena de conexión blindada con límites de tiempo SCRAM
URI_ATLAS_PASSWORD = (
    "mongodb+srv://render_user:Girardot2026@ac-pcoifqi-shard-00-00.oafwuqv.mongodb.net/?"
    "retryWrites=true&w=majority&appName=Data+Explorer--6a524b2b366a569efa0c75c6"
    "&serverSelectionTimeoutMS=15000&connectTimeoutMS=15000"
)

def _descubrir_coleccion_y_campos(client, sinonimos_base_datos, sinonimos_coleccion):
    """
    Escanea el clúster de Mongo para encontrar dinámicamente la base de datos 
    y la colección correctas usando lógica semántica y proximidad de nombres.
    """
    # 1. Descubrir la Base de Datos adecuada
    todas_las_dbs = client.list_database_names()
    db_seleccionada = None
    
    for termino in sinonimos_base_datos:
        coincidencias = difflib.get_close_matches(termino.upper(), [db.upper() for db in todas_las_dbs], n=1, cutoff=0.4)
        if coincidencias:
            idx = [db.upper() for db in todas_las_dbs].index(coincidencias[0])
            db_seleccionada = todas_las_dbs[idx]
            break
            
    if not db_seleccionada:
        return None, None, []

    # 2. Descubrir la Colección adecuada dentro de esa Base de Datos
    db = client[db_seleccionada]
    todas_las_colecciones = db.list_collection_names()
    coleccion_seleccionada = None
    
    for termino in sinonimos_coleccion:
        coincidencias = difflib.get_close_matches(termino.upper(), [c.upper() for c in todas_las_colecciones], n=1, cutoff=0.4)
        if coincidencias:
            idx = [c.upper() for c in todas_las_colecciones].index(coincidencias[0])
            coleccion_seleccionada = todas_las_colecciones[idx]
            break
            
    if not coleccion_seleccionada:
        return db_seleccionada, None, []

    # 3. Mapear dinámicamente las llaves (campos) leyendo el primer registro disponible
    primer_documento = db[coleccion_seleccionada].find_one()
    campos_disponibles = list(primer_documento.keys()) if primer_documento else []
    
    return db_seleccionada, coleccion_seleccionada, campos_disponibles


def cargar_datos_mongo_autoadaptable(sinonimos_db, sinonimos_col, mapa_campos_esperados):
    """
    Punto de entrada universal: Se conecta a la nube, detecta la base de datos,
    descubre la colección y adapta las columnas de forma dinámica.
    """
    try:
        client = MongoClient(URI_ATLAS_PASSWORD, serverSelectionTimeoutMS=15000)
        
        # Ejecutar el motor de descubrimiento
        db_real, col_real, campos = _descubrir_coleccion_y_campos(client, sinonimos_db, sinonimos_col)
        
        if not col_real:
            print(f"⚠️ No se encontró ninguna colección compatible en la nube para {sinonimos_col}.")
            return pd.DataFrame(), {}

        print(f"🤖 CLOUD DISCOVERY: Mapeada base de datos '{db_real}' ➡️ Colección '{col_real}'")
        
        # Descargar los documentos de la colección descubierta
        cursor = client[db_real][col_real].find({}).max_time_ms(15000)
        lista_docs = list(cursor)
        
        if not lista_docs:
            return pd.DataFrame(), {}
            
        df = pd.DataFrame(lista_docs)
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])

        # Mapear dinámicamente los campos internos usando aproximación de texto
        col_map_dinamico = {}
        for clave_sistema, lista_sinonimos in mapa_campos_esperados.items():
            campo_encontrado = None
            for sinonimo in lista_sinonimos:
                coincidencias = difflib.get_close_matches(sinonimo.upper(), [str(c).upper() for c in df.columns], n=1, cutoff=0.4)
                if coincidencias:
                    idx = [str(c).upper() for c in df.columns].index(coincidencias[0])
                    campo_encontrado = df.columns[idx]
                    break
            
            # Asignar el campo encontrado o crear una columna virtual segura si falta
            if campo_encontrado:
                col_map_dinamico[clave_sistema] = campo_encontrado
            else:
                col_map_dinamico[clave_sistema] = f"VIRTUAL_{clave_sistema.upper()}"
                df[f"VIRTUAL_{clave_sistema.upper()}"] = 0
                
        return df, col_map_dinamico

    except Exception as e:
        print(f"❌ Error en el motor de autoadaptación Cloud: {e}", file=sys.stderr)
        return pd.DataFrame(), {}
