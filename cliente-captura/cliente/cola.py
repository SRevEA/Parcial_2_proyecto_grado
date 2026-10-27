import sqlite3
from datetime import datetime


def abrir(ruta: str) -> sqlite3.Connection:
    conexion = sqlite3.connect(ruta)
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS pendientes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            imagen       BLOB NOT NULL,
            capturado_en TEXT NOT NULL
        )
    """)
    conexion.commit()
    return conexion


def encolar(conexion: sqlite3.Connection, imagen: bytes, capturado_en: datetime) -> None:
    conexion.execute(
        'INSERT INTO pendientes (imagen, capturado_en) VALUES (?, ?)',
        (imagen, capturado_en.isoformat()),
    )
    conexion.commit()


def pendientes(conexion: sqlite3.Connection, limite: int = 10) -> list[tuple[int, bytes, str]]:
    filas = conexion.execute(
        'SELECT id, imagen, capturado_en FROM pendientes ORDER BY id LIMIT ?', (limite,)
    ).fetchall()
    return [(int(f[0]), bytes(f[1]), str(f[2])) for f in filas]


def descartar(conexion: sqlite3.Connection, id_pendiente: int) -> None:
    conexion.execute('DELETE FROM pendientes WHERE id = ?', (id_pendiente,))
    conexion.commit()


def cuantos(conexion: sqlite3.Connection) -> int:
    fila = conexion.execute('SELECT COUNT(*) FROM pendientes').fetchone()
    return int(fila[0])
