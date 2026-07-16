from pymongo import MongoClient

def obtener_cliente_mongo():
    """Establece conexión a MongoDB Atlas mediante usuario y contraseña (SCRAM)."""
    # Definimos las credenciales que configuraste en la interfaz
    usuario = "render_user"
    contrasenia = "Girardot2026"
    
    # Cadena de conexión estándar usando las tres réplicas de tu clúster
    uri = (
        f"mongodb://{usuario}:{contrasenia}@ac-pcoifqi-shard-00-02.oafwuqv.mongodb.net,"
        "ac-pcoifqi-shard-00-01.oafwuqv.mongodb.net,"
        "ac-pcoifqi-shard-00-00.oafwuqv.mongodb.net/"
        "?ssl=true&authSource=admin&replicaSet=atlas-t1u5dd-shard-0"
        "&compressors=zlib&maxIdleTimeMS=45000&minPoolSize=0"
    )
    
    return MongoClient(uri)
