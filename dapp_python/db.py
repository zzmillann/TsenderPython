import sqlite3
import os
from datetime import datetime

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
    return [dict(row) for row in rows]
