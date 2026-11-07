from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name('.env'))


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str
    mongodb_database: str
    frontend_origins: tuple[str, ...]
    demo_write_enabled: bool


def get_settings() -> Settings:
    uri = os.getenv('MONGODB_URI', '').strip()
    database = os.getenv('MONGODB_DATABASE', 'davincimusic_nosql_dev').strip()
    if not uri or not uri.startswith(('mongodb://', 'mongodb+srv://')):
        raise ValueError('Configura MONGODB_URI en backend/.env con la cadena de Atlas.')
    if database != 'davincimusic_nosql_dev':
        raise ValueError('Esta actividad está restringida a davincimusic_nosql_dev.')
    origins = tuple(origin.strip() for origin in os.getenv(
        'FRONTEND_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173'
    ).split(',') if origin.strip())
    return Settings(
        mongodb_uri=uri,
        mongodb_database=database,
        frontend_origins=origins,
        demo_write_enabled=os.getenv('DEMO_WRITE_ENABLED', 'false').strip().lower() == 'true',
    )
