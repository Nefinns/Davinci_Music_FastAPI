"""API local para ejecutar exclusivamente los ejercicios de DaVinciMusic Unidad 5."""
import os
import time
from datetime import date, datetime, time as dt_time
from decimal import Decimal
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.catalog import EXERCISES, list_catalog
from app.database import connect_checked
from app.objects import demo_trigger, trigger_source
from app.setup import prepare, is_ready

load_dotenv(Path(__file__).resolve().parent / '.env')
app = FastAPI(title='DaVinciMusic | Laboratorio Unidad 5', version='1.0.0',
              description='65 operaciones PostgreSQL predefinidas; datos de prueba y base aislada.')
origins = [x.strip() for x in os.getenv('FRONTEND_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET','POST'], allow_headers=['Content-Type'])

class RunBody(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)


def normalize(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime, dt_time)):
        return value.isoformat()
    return value


def checked_params(exercise, raw):
    allowed = {p['name'] for p in exercise.params}
    if set(raw) - allowed:
        raise HTTPException(422, 'Se proporcionaron parámetros no definidos para este ejercicio.')
    result = {}
    for item in exercise.params:
        name = item['name']
        value = raw.get(name, item['default'])
        try:
            if item['kind'] == 'int':
                if isinstance(value, bool): raise ValueError()
                value = int(value)
                if not -10000000 <= value <= 10000000: raise ValueError()
            elif item['kind'] == 'float':
                value = float(value)
                if not -10000000 <= value <= 10000000: raise ValueError()
            elif item['kind'] == 'date':
                value = date.fromisoformat(str(value)).isoformat()
            else:
                value = str(value)
                if len(value) > 80: raise ValueError()
        except (TypeError, ValueError, OverflowError):
            raise HTTPException(422, f'Parámetro inválido: {name}') from None
        result[name] = value
    return result

@app.get('/')
def root():
    return {'message':'Laboratorio de bases de datos DaVinciMusic','version':'1.0.0','ejercicios':65}

@app.get('/api/catalogo')
def catalog():
    items = list_catalog()
    for ex in items['exercises']:
        if ex['group'] == 'triggers':
            ex['sql'] = trigger_source(ex['code'])
    return items

@app.get('/api/estado')
def state():
    try:
        conn = connect_checked()
        try:
            ready = is_ready(conn)
            db = conn.execute(text('SELECT current_database()')).scalar_one()
            return {'connected': True, 'ready': ready, 'database': db,
                    'message':'Preparada' if ready else 'Conectada; requiere preparación'}
        finally:
            conn.close()
    except HTTPException as exc:
        return {'connected':False,'ready':False,'message':exc.detail}
    except SQLAlchemyError:
        return {'connected':False,'ready':False,'message':'No es posible conectar con PostgreSQL. Revisa DATABASE_URL y red.'}

@app.post('/api/preparar')
def setup():
    try:
        return prepare()
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(503, 'No fue posible preparar la BD. Revisa conexión, permisos y que esté vacía.') from None

@app.post('/api/ejecutar/{code}')
def run(code: str, body: RunBody):
    code = code.upper()
    exercise = EXERCISES.get(code)
    if not exercise:
        raise HTTPException(404, 'El ejercicio no existe.')
    values = checked_params(exercise, body.params)
    start = time.perf_counter()
    try:
        conn = connect_checked()
        try:
            if not is_ready(conn):
                raise HTTPException(409,'Primero prepara la base de datos experimental.')
            if exercise.group == 'triggers':
                conn.rollback()
                transaction = conn.begin()
                try:
                    result = demo_trigger(conn, code)
                finally:
                    transaction.rollback()
                return {'code':code,'title':exercise.title,'columns':list(result.keys()),
                        'rows':[{k:normalize(v) for k,v in result.items()}],
                        'duration_ms':round((time.perf_counter()-start)*1000,2),
                        'message':'Demostración completada. Todos sus cambios fueron revertidos.'}
            result = conn.execute(text(exercise.sql), values)
            columns = list(result.keys())
            rows = [{k:normalize(v) for k,v in dict(row).items()} for row in result.mappings().fetchmany(101)]
            truncated = len(rows) > 100
            return {'code':code,'title':exercise.title,'columns':columns,'rows':rows[:100],
                    'truncated':truncated,'duration_ms':round((time.perf_counter()-start)*1000,2),
                    'message':'Se muestran las primeras 100 filas.' if truncated else f'{len(rows)} filas recuperadas.'}
        finally:
            conn.close()
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(400,'La operación no pudo ejecutarse. Verifica que el entorno demo esté preparado.') from None
