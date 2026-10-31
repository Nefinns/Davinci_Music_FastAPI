"""Conexión protegida: nunca ejecutar sobre la base principal."""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

load_dotenv(Path(__file__).resolve().parents[1] / '.env')

@lru_cache(maxsize=1)
def get_engine():
    raw = os.getenv('DATABASE_URL', '').strip()
    allowed = os.getenv('UNIT5_ALLOWED_DATABASE', 'davinci_music_unidad5').strip()
    if not raw:
        raise HTTPException(503, 'Configura DATABASE_URL en backend/.env.')
    if not allowed or 'unidad5' not in allowed.lower() or allowed.lower() in ('neondb', 'postgres', 'davinci_music'):
        raise HTTPException(400, 'UNIT5_ALLOWED_DATABASE debe identificar una BD exclusiva de unidad5.')
    try:
        url = make_url(raw)
    except Exception:
        raise HTTPException(400, 'DATABASE_URL no tiene un formato válido.') from None
    if url.get_backend_name() != 'postgresql':
        raise HTTPException(400, 'Solo se permite PostgreSQL.')
    if url.database != allowed:
        raise HTTPException(403, 'Seguridad: el nombre de la BD de la URL no coincide con UNIT5_ALLOWED_DATABASE.')
    return create_engine(raw, pool_pre_ping=True, pool_size=3, max_overflow=2, connect_args={'connect_timeout': 8})


def connect_checked():
    engine = get_engine()
    conn = engine.connect()
    try:
        current = conn.execute(text('SELECT current_database()')).scalar_one()
        allowed = os.getenv('UNIT5_ALLOWED_DATABASE', 'davinci_music_unidad5').strip()
        if current != allowed:
            raise HTTPException(403, 'Operación rechazada: servidor conectado a otra base de datos.')
        conn.rollback()
        return conn
    except Exception:
        conn.close()
        raise
