"""DaVinciMusic · Unidad 6. Local teaching-only API with fixed NoSQL examples."""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

import certifi
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from catalog import BY_ID, CATALOG, VIEWS, prepare_views, public_exercise, run_exercise
from config import get_settings
from seed import DEMO_TAG, seed_database
from serialize import clean_bson

logger = logging.getLogger('davincimusic.u6')
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncMongoClient(
        settings.mongodb_uri,
        tlsCAFile=certifi.where() if settings.mongodb_uri.startswith('mongodb+srv://') else None,
        serverSelectionTimeoutMS=9000,
        appname='DavinciMusicUnidad6',
    )
    try:
        await client.admin.command('ping')
        app.state.database = client[settings.mongodb_database]
        logger.info('Conexión MongoDB confirmada con la base configurada.')
        yield
    finally:
        await client.close()


app = FastAPI(
    title='DaVinciMusic · Unidad 6 NoSQL',
    description='Consultas predefinidas con PyMongo Async. No incluye login ni motor de migración.',
    version='1.0.0',
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.frontend_origins),
                   allow_credentials=False, allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])


@app.get('/api/health')
async def health(request: Request):
    try:
        result = await request.app.state.database.command('ping')
        return {'ok': result.get('ok') == 1, 'base_datos': settings.mongodb_database,
                'escritura_demo_habilitada': settings.demo_write_enabled}
    except PyMongoError as exc:
        logger.warning('Error de conexión MongoDB: %s', type(exc).__name__)
        raise HTTPException(503, 'Atlas no responde. Verifica la URI y Network Access.') from None


@app.get('/api/catalogo')
async def list_catalog():
    return {'ejercicios': [public_exercise(item) for item in CATALOG], 'categorias': [
        {'id': 'simples', 'titulo': 'Consultas simples'},
        {'id': 'joins', 'titulo': 'Operaciones JOIN'},
        {'id': 'agregadas', 'titulo': 'Funciones agregadas'},
        {'id': 'vistas', 'titulo': 'Vistas MongoDB'},
    ]}


@app.get('/api/estado')
async def database_status(request: Request):
    database = request.app.state.database
    try:
        names = await database.list_collection_names()
        counts = {}
        for name in ['usuario', 'instrumento', 'clase', 'venta', 'orden_abastecimiento',
                     'inscripcion_clase', 'pago_clase', 'periodo_academico', 'proveedor']:
            counts[name] = await database[name].count_documents({'demo_unidad6': DEMO_TAG}) if name in names else 0
        return {'base_datos': settings.mongodb_database, 'colecciones': counts,
                'vistas': [name for name in VIEWS if name in names],
                'total_demo': sum(counts.values()),
                'escritura_demo_habilitada': settings.demo_write_enabled}
    except PyMongoError:
        raise HTTPException(503, 'No se pudo consultar MongoDB Atlas.') from None


@app.get('/api/consultas/{exercise_id}')
async def execute_query(exercise_id: str, request: Request):
    exercise = BY_ID.get(exercise_id.upper())
    if not exercise:
        raise HTTPException(404, 'Ejercicio desconocido.')
    started = time.perf_counter()
    try:
        database = request.app.state.database
        if exercise.kind == 'view' and exercise.collection not in (await database.list_collection_names()):
            raise HTTPException(409, 'Prepara las vistas primero desde el panel.')
        documents = await run_exercise(database, exercise)
    except HTTPException:
        raise
    except PyMongoError as exc:
        logger.warning('Fallo en ejercicio %s: %s', exercise.code, type(exc).__name__)
        raise HTTPException(503, 'No se pudo ejecutar el ejercicio en Atlas.') from None
    return {'ejercicio': exercise.code, 'filas': len(documents),
            'duracion_ms': round((time.perf_counter() - started) * 1000, 1),
            'resultados': clean_bson(documents), 'limite': 100}


def require_demo_write() -> None:
    if not settings.demo_write_enabled:
        raise HTTPException(403, 'Las escrituras están desactivadas. Habilita DEMO_WRITE_ENABLED=true en .env solo para uso local.')


@app.post('/api/datos-prueba')
async def insert_demo(request: Request):
    require_demo_write()
    try:
        inserted = await seed_database(request.app.state.database)
        return {'insertados': inserted, 'total_nuevos': sum(inserted.values()), 'mensaje': 'Datos demo preparados sin modificar documentos migrados.'}
    except PyMongoError as exc:
        logger.warning('No se pudo preparar los datos: %s', type(exc).__name__)
        raise HTTPException(503, 'Falló la carga de datos de prueba. Comprueba permisos de escritura.') from None


@app.post('/api/vistas/preparar')
async def create_demo_views(request: Request):
    require_demo_write()
    try:
        views = await prepare_views(request.app.state.database)
        return {'vistas': views, 'mensaje': 'Vistas creadas o actualizadas.'}
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from None
    except PyMongoError as exc:
        logger.warning('No se pudieron crear vistas: %s', type(exc).__name__)
        raise HTTPException(503, 'No se pudieron crear las vistas en Atlas. Verifica el usuario y sus permisos.') from None
