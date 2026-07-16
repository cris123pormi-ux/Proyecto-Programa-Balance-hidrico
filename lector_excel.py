import pandas as pd
import os
import difflib

def buscar_columna_semantica(columnas_excel, familias_palabras, columna_defecto):
    """
    Busca coincidencias semánticas exactas, parciales o aproximadas 
    en la lista de columnas reales del archivo Excel.
    """
    columnas_mayusculas = [str(c).upper().strip() for c in columnas_excel]
    
    # 1. Búsqueda por palabra clave contenida (Ej: si busca JUNIO y encuentra LEC JUNIO 2026 o LEC JUNIO 202)
    for palabra in familias_palabras:
        for idx, col_real in enumerate(columnas_mayusculas):
            if palabra.upper() in col_real: 
                return columnas_excel[idx]
                
    # 2. Búsqueda por aproximación difusa (Levenshtein) por si hay errores de digitación
    for palabra in familias_palabras:
        coincidencias = difflib.get_close_matches(palabra.upper(), columnas_mayusculas, n=1, cutoff=0.4)
        if coincidencias:
            idx = columnas_mayusculas.index(coincidencias[0])
            return columnas_excel[idx]
            
    # 3. Retorno por defecto si no se encuentra mapeo
    return columna_defecto


def cargar_y_mapear_excel_universal(ruta_archivo):
    """
    Carga el archivo Excel de Girardot de forma flexible y mapea las columnas
    de manera automática detectando nombres recortados o completos.
    """
    if not os.path.exists(ruta_archivo): 
        raise FileNotFoundError(f"No se encontró el archivo en: {ruta_archivo}")
    
    print(f"\n📥 Cargando archivo de facturación: {os.path.basename(ruta_archivo)}...")
    
    # Carga limpia del archivo Excel
    df = pd.read_excel(ruta_archivo, sheet_name=0, header=0)
    df.columns = df.columns.astype(str).str.strip()
    
    columnas_lista = list(df.columns)
    
    # Familias ampliadas con términos recortados basados en tus imágenes reales
    famillas = {
        'id_cuenta': ['CONTRATO', 'CUENTA', 'SUSCRIPTOR', 'ID', 'CODIGO', 'MATRICULA'],
        'c_jun': ['JUNIO', 'JUN', 'LEC JUNIO', 'LECTURA ACTUAL', 'LEC_ACT', 'LEC JUN'],
        'c_may': ['MAYO', 'MAY', 'LEC MAYO', 'LECTURA ANTERIOR', 'LEC_ANT', 'LEC MAY'],
        'c_abr': ['ABRIL', 'ABR', 'LEC ABRIL', 'LEC_ABR', 'LEC ABR'],
        'col_facturar': ['FACT', 'CONSUMO', 'CONSU A FACT', 'CONSUMO A FACTURAR', 'M3', 'VOLUMEN'],
        'col_observacion': ['OBSERVACION', 'OBS', 'ANOMALIA', 'OBSERVACION JUNIO', 'OBS_JUN'],
        'col_estrato': ['ESTRATO', 'NIVEL', 'CLASE', 'CATEGORIA'],
        'col_estado_tec': ['TECNICO', 'ESTADO TECNICO', 'ESTADO_MEDIDOR', 'CONDICION', 'ESTADO'],
        'col_fecha_inst': ['INSTALACION', 'FECHA_INST', 'F_INST', 'FECHA DE INSTALACION', 'FECHA_MEDIDOR']
    }
    
    col_map = {}
    for clave, terminos in famillas.items():
        col_map[clave] = buscar_columna_semantica(columnas_lista, terminos, f"COL_VIRTUAL_{clave.upper()}")
    
    # 🚨 Validar si falló el buscador para inyectar un plan de contingencia seguro si falta alguna columna
    if col_map['col_observacion'] == "COL_VIRTUAL_COL_OBSERVACION":
        df["COL_VIRTUAL_COL_OBSERVACION"] = "LECTURA NORMAL"
        
    # Acoplar las coordenadas geoespaciales de Girardot si existen
    for col_real in df.columns:
        if 'LATITUD' in str(col_real).upper():
            df['LATITUD'] = df[col_real]
        if 'LONGITUD' in str(col_real).upper():
            df['LONGITUD'] = df[col_real]

    print("=============================================================")
    print("🤖 MAPEADOR INTELIGENTE HYDROAI PRO ACTIVADO")
    print("🔍 Columnas enlazadas semánticamente:")
    for k, v in col_map.items():
        print(f"  • {k.ljust(15)} ➡️ '{v}'")
    print("=============================================================\n")
        
    return df, col_map
