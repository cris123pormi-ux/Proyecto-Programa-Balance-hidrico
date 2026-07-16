import pandas as pd
import lector_mongo
import red_hidraulica

def ejecutar_gemelo_digital_completo():
    print("🔋 Conectando a MongoDB Atlas como 'render_user'...")
    
    try:
        # 1. Descargar topología de red de tuberías de Girardot
        client = lector_mongo.obtener_cliente_mongo()
        db_mapa = client['Mapa']['mapa hidraulico']
        df_mapa = pd.DataFrame(list(db_mapa.find({})))
        print(f"✅ Infraestructura descargada: {len(df_mapa)} elementos de red encontrados.")
        
        # 2. Descargar demandas / consumos de agua en tiempo real
        db_puntos = client['GemeloDigitalGirardot']['gemelo_digital_puntos']
        cursor_puntos = db_puntos.find({})
        
        diccionario_demandas = {}
        for doc in cursor_puntos:
            id_nodo = doc.get('id_punto', doc.get('_id'))
            caudal = doc.get('caudal', doc.get('consumo', 0.0))
            diccionario_demandas[str(id_nodo)] = float(caudal)
        print(f"✅ Demandas cargadas: {len(diccionario_demandas)} puntos con consumo activo.")
        
        client.close()
        
        # 3. Procesar y simular hidráulicamente con EPANET (WNTR)
        print("💧 Procesando simulación matemática de presiones urbanas...")
        presiones, caudales = red_hidraulica.construir_y_simular_red_desde_mongo(df_mapa, diccionario_demandas)
        
        if presiones is not None:
            print("🎉 ¡Simulación finalizada! El Gemelo Digital está sincronizado y corriendo.")
            
    except Exception as e:
        print(f"❌ Error crítico en la ejecución del ecosistema: {e}")

if __name__ == "__main__":
    ejecutar_gemelo_digital_completo()
