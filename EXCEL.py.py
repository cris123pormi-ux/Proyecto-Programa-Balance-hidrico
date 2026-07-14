import pandas as pd

# Reemplaza 'tu_archivo.xlsx' por el nombre real de tu documento de Excel
# Asegúrate de que el archivo Excel esté guardado dentro de la carpeta Auditoria_IA
nombre_archivo = 'C:\Users\christian.godoy\Desktop\Copia de CONSUMOS JUNIO-2026.xlsm' 

try:
    df = pd.read_excel("C:\Users\christian.godoy\Desktop\Copia de CONSUMOS JUNIO-2026.xlsm")
    print("¡Archivo cargado con éxito!")
    print("\n--- Primeras filas del archivo ---")
    print(df.head())
except Exception as e:
    print(f"Error al cargar el archivo: {e}")
    
