import lector_mongo
import validaciones
import red_hidraulica
import pandas as pd

def flujo_con_control_de_calidad():
    print("📡 Conectando y descargando datos...")
    client = lector_mongo.obtener_cliente_mongo()
    
    # Descargas crudas de MongoDB
    df_mapa_crudo = pd.DataFrame(list(client['Mapa']['mapa hidraulico'].find({})))
    puntos_crudos = client['GemeloDigitalGirardot']['gemelo_digital_puntos'].find({})
    
    dict_demandas_crudo = {}
    for doc in puntos_crudos:
        id_nodo = doc.get('id_punto', doc.get('_id'))
        dict_demandas_crudo[str(id_nodo)] = doc.get('caudal', 0.0)
    client.close()
    
    # ✨ PASO RECOMENDADO: VALIDACIÓN Y LIMPIEZA
    print("🧼 Validando consistencia de datos hidráulicos...")
    df_mapa_limpio = validaciones.limpiar_y_validar_infraestructura(df_mapa_crudo)
    dict_demandas_limpio = validaciones.validar_diccionario_demandas(dict_demandas_crudo)
    
    # Simulación segura
    print("💧 Procesando en motor de simulación WNTR/EPANET...")
    presiones, caudales = red_hidraulica.construir_y_simular_red_desde_mongo(df_mapa_limpio, dict_demandas_limpio)
    print("🏁 Proceso completado de extremo a extremo.")

if __name__ == "__main__":
    flujo_con_control_de_calidad()
