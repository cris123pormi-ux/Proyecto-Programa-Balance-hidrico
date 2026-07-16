import json
import logging
import os

def cargar_configuracion(ruta_config="config.json"):
    with open(ruta_config, 'r', encoding='utf-8') as f:
        return json.load(f)

def inicializar_logger(ruta_log):
    carpeta_log = os.path.dirname(ruta_log)
    if carpeta_log: os.makedirs(carpeta_log, exist_ok=True)
    logger = logging.getLogger("HydroAI_Logger")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        formato = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler(ruta_log, encoding='utf-8')
        file_handler.setFormatter(formato)
        logger.addHandler(file_handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formato)
        logger.addHandler(stream_handler)
    return logger
