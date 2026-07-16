import pandas as pd
from pymongo import MongoClient

def integrar_gemelo_digital(df_auditoria, col_map_auditoria, log, ruta_pem=None):
    uri = "mongodb://ac-pcoifqi-shard-00-01.oafwuqv.mongodb.net,ac-pcoifqi-shard-00-00.oafwuqv.mongodb.net,ac-pcoifqi-shard-00-02.oafwuqv.mongodb.net/?tls=true&authMechanism=MONGODB-X509&authSource=%24external&maxIdleTimeMS=45000&minPoolSize=0&replicaSet=atlas-t1u5dd-shard-0&compressors=zlib&appName=Data+Explorer--6a524b2b366a569efa0c75c6"
    args = {'tlsCertificateKeyFile': ruta_pem} if ruta_pem else {}
    try:
        log.info("🌐 Conectando a MongoDB Atlas para alimentar el Gemelo Digital...")
        client = MongoClient(uri, **args)
        df_puntos = pd.DataFrame(list(client['GemeloDigitalGirardot']['gemelo_digital_puntos'].find({})))
        if df_puntos.empty: return df_auditoria
        
        df_puntos.columns = df_puntos.columns.astype(str).str.strip()
        if '_id' in df_puntos.columns: df_puntos = df_puntos.drop(columns=['_id'])
        
        col_llave_comercial = col_map_auditoria['id_cuenta']
        col_llave_espacial = 'Contrato' if 'Contrato' in df_puntos.columns else ('ID' if 'ID' in df_puntos.columns else df_puntos.columns)
        
        df_auditoria[col_llave_comercial] = df_auditoria[col_llave_comercial].astype(str).str.strip()
        df_puntos[col_llave_espacial] = df_puntos[col_llave_espacial].astype(str).str.strip()
        
        return pd.merge(df_auditoria, df_puntos, left_on=col_llave_comercial, right_on=col_llave_espacial, how='left')
    except Exception as e:
        log.error(f"❌ Error en sincronización geoespacial: {e}")
        return df_auditoria
