import sqlite3
import os
from datetime import datetime
from logger_config import get_logger

# Logger de este módulo.
# __name__ vale 'db', así cada línea del log indica qué módulo la generó.
logger = get_logger(__name__)

# Ruta absoluta a la BD junto al propio módulo, independiente del directorio de trabajo.
# Así el archivo historial.db siempre se crea en la carpeta dapp_python/.
DB_PATH = os.path.join(os.path.dirname(__file__), 'historial.db')


def init_db():
    """
    Crea la tabla 'transacciones' si no existe todavía.
    Se llama una vez al arrancar la app.
    sqlite3 viene incluido en la stdlib de Python, no hace falta instalar nada.
    """
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS transacciones (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha         TEXT    NOT NULL,
                tipo          TEXT    NOT NULL,
                tx_hash       TEXT    NOT NULL,
                desde         TEXT,
                contrato      TEXT,
                destinatarios INTEGER,
                estado        TEXT    NOT NULL DEFAULT 'éxito'
            )
        """)
        con.commit()
    logger.info("Base de datos inicializada correctamente — ruta: %s", DB_PATH)


def save_tx(tipo, tx_hash, desde=None, contrato=None, destinatarios=None, estado="éxito"):
    """
    Inserta una nueva fila en el historial de transacciones.

    Parámetros:
        tipo          -- 'Airdrop', 'Approve', 'Deploy Token', 'Deploy Airdrop', 'Donación'
        tx_hash       -- hash de la transacción devuelto por la blockchain
        desde         -- dirección de la wallet que firmó la tx
        contrato      -- dirección del contrato involucrado
        destinatarios -- número de wallets receptoras (solo relevante para Airdrop)
        estado        -- 'éxito' o 'error'
    """
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """INSERT INTO transacciones
               (fecha, tipo, tx_hash, desde, contrato, destinatarios, estado)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (fecha, tipo, tx_hash, desde, contrato, destinatarios, estado)
        )
        con.commit()
    # Usamos logging.INFO para confirmar que la tx se guardó bien.
    logger.info(
        "TX guardada — tipo: %s | estado: %s | hash: %s | desde: %s | destinatarios: %s",
        tipo, estado, tx_hash[:12] + "..." if tx_hash and len(tx_hash) > 12 else tx_hash,
        desde, destinatarios
    )


def get_history():
    """
    Devuelve todas las transacciones guardadas como lista de diccionarios,
    ordenadas de más reciente a más antigua.
    row_factory = sqlite3.Row permite acceder a cada campo por nombre de columna.
    """
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT * FROM transacciones ORDER BY id DESC"
        ).fetchall()
    # logging.DEBUG: mensaje de depuración que solo aparece en el archivo .log,
    # no en la consola (el StreamHandler está configurado a nivel INFO).
    logger.debug("Historial consultado — %d registros devueltos", len(rows))
    return [dict(row) for row in rows]
