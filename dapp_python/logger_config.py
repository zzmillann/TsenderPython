"""
logger_config.py
================
Módulo centralizado de logging para TSender.

El módulo estándar `logging` de Python tiene 5 niveles de gravedad, de menor
a mayor:

    DEBUG    → mensajes de depuración (solo en desarrollo)
    INFO     → confirmaciones de que todo va bien
    WARNING  → algo inesperado, pero la app sigue funcionando
    ERROR    → un error real que impide hacer algo
    CRITICAL → error grave, la app podría no recuperarse

Un Logger tiene 1 o más Handlers. Cada Handler decide DÓNDE se escribe el mensaje:
    - FileHandler  → escribe en un archivo .log del disco
    - StreamHandler → escribe en la consola (terminal)

El Formatter decide CÓMO se ve cada línea de log.

Flujo completo:
    tu código → logger.info("msg") → Logger → Handler(s) → destino (archivo / consola)
"""

import logging
import os

# Ruta del archivo de log junto al propio módulo.
# os.path.dirname(__file__) devuelve el directorio del script actual,
# así el .log se crea siempre en dapp_python/ independientemente de
# desde qué directorio se ejecute la app.
LOG_PATH = os.path.join(os.path.dirname(__file__), 'tsender.log')


def get_logger(name: str) -> logging.Logger:
    """
    Devuelve un Logger ya configurado con FileHandler y StreamHandler.

    El módulo `logging` tiene un registro global de loggers indexado por nombre.
    Si pedimos el mismo nombre dos veces nos devuelve el mismo objeto, sin
    duplicar handlers. Esto es importante en Streamlit, que puede reimportar
    módulos en cada interacción del usuario.

    Args:
        name (str): nombre del logger. Por convención se usa __name__,
                    que coincide con el nombre del módulo (ej: 'app', 'db').

    Returns:
        logging.Logger: instancia lista para usar.

    Uso típico al inicio de cada módulo:
        from logger_config import get_logger
        logger = get_logger(__name__)
        logger.info("Módulo cargado correctamente")
    """
    logger = logging.getLogger(name)

    # Evitamos añadir handlers duplicados si el logger ya existe en el registro.
    # Streamlit ejecuta el script completo en cada interacción, así que esta
    # comprobación es fundamental.
    if logger.handlers:
        return logger

    # Nivel raíz del logger: DEBUG → captura TODOS los mensajes.
    # Los handlers individuales pueden filtrar a un nivel más alto.
    logger.setLevel(logging.DEBUG)

    # ─────────────────────────────────────────────
    # FORMATO
    # ─────────────────────────────────────────────
    # %(asctime)s   → fecha y hora (formato dado por datefmt)
    # %(levelname)s → nivel del mensaje, left-justified en 8 caracteres
    # %(name)s      → nombre del logger (el módulo que generó el mensaje)
    # %(message)s   → el texto que pasamos con logger.info() / logger.error() / etc.
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # ─────────────────────────────────────────────
    # HANDLER 1: FileHandler  →  escribe en tsender.log
    # ─────────────────────────────────────────────
    # mode='a'         → append: acumula líneas, no sobreescribe al reiniciar.
    # encoding='utf-8' → necesario para acentos y caracteres especiales.
    file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)   # guarda TODO (DEBUG en adelante)
    file_handler.setFormatter(formatter)

    # ─────────────────────────────────────────────
    # HANDLER 2: StreamHandler  →  imprime en consola
    # ─────────────────────────────────────────────
    # Solo muestra INFO en adelante para no llenar la terminal de mensajes DEBUG.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Registramos ambos handlers en el logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
