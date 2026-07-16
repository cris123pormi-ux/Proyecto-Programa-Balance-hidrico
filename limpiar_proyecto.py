import os
import shutil

def corregir_estructura():
    print("🚀 Iniciando reorganización de Auditoria_IA...\n")
    
    # Base del proyecto (directorio actual)
    raiz = os.getcwd()
    
    # 1. Definir rutas de origen y destino
    src_path = os.path.join(raiz, "src")
    auto_path = os.path.join(src_path, "automatizacion")
    tests_path = os.path.join(raiz, "tests")
    
    # 2. Crear carpetas faltantes si no existen
    os.makedirs(auto_path, exist_ok=True)
    print(f"📁 Subcarpeta creada: {os.path.relpath(auto_path, raiz)}")
    
    # Crear archivos __init__.py para el correcto funcionamiento de los imports
    for folder in [auto_path, tests_path]:
        init_file = os.path.join(folder, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                pass
            print(f"✨ Archivo __init__.py creado en: {os.path.relpath(folder, raiz)}")

    # 3. Mover scripts de automatización a su nueva subcarpeta
    scripts_a_mover = [
        (os.path.join(src_path, "automatizar.py"), os.path.join(auto_path, "automatizar.py")),
        (os.path.join(src_path, "instalar_tarea.py"), os.path.join(auto_path, "instalar_tarea.py")),
        (os.path.join(raiz, "organizador.py"), os.path.join(auto_path, "organizador.py"))
    ]
    
    for origen, destino in scripts_a_mover:
        if os.path.exists(origen):
            shutil.move(origen, destino)
            print(f"📦 Movido: {os.path.relpath(origen, raiz)} ➡️ {os.path.relpath(destino, raiz)}")
        else:
            print(f"⚠️ No se encontró para mover: {os.path.relpath(origen, raiz)}")

    # 4. Resolver el conflicto de los archivos de configuración
    config_raiz = os.path.join(raiz, "config.json")
    config_tests = os.path.join(tests_path, "config.json")
    
    if os.path.exists(config_raiz) and os.path.exists(config_tests):
        print("🔍 Se detectaron dos config.json. Conservando el de la raíz principal...")
        try:
            os.remove(config_tests)
            print(f"🗑️ Eliminado duplicado de pruebas: {os.path.relpath(config_tests, raiz)}")
        except Exception as e:
            print(f"❌ No se pudo borrar el config de tests: {e}")
            
    print("\n✅ ¡Estructura corregida con éxito!")

if __name__ == "__main__":
    corregir_estructura()
