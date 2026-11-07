"""Fixed, auditable MongoDB exercises. No arbitrary query string from the browser."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from seed import DEMO_TAG

QueryKind = Literal['find', 'aggregate', 'view']


@dataclass(frozen=True)
class Exercise:
    code: str
    category: str
    title: str
    description: str
    collection: str
    kind: QueryKind
    filter: dict[str, Any] | None = None
    projection: dict[str, Any] | None = None
    sort: dict[str, int] | None = None
    pipeline: list[dict[str, Any]] | None = None


def exercise_code(e: Exercise) -> str:
    if e.kind == 'find':
        clause = json.dumps(e.filter or {}, ensure_ascii=False, indent=2)
        fields = json.dumps(e.projection or {}, ensure_ascii=False, indent=2)
        query = f'db.{e.collection}.find(\n{clause},\n{fields}\n)'
        if e.sort:
            query += f'.sort({json.dumps(e.sort, ensure_ascii=False)})'
        return query + '.forEach(printjson);'
    if e.kind == 'aggregate':
        stages = json.dumps(e.pipeline or [], ensure_ascii=False, indent=2)
        return f'db.{e.collection}.aggregate({stages}).forEach(printjson);'
    return f'db.{e.collection}.find({{}}).forEach(printjson);'


def view_code(name: str, source: str, pipeline: list[dict[str, Any]]) -> str:
    stages = json.dumps(pipeline, ensure_ascii=False, indent=2)
    return f'db.createView("{name}", "{source}", {stages});'


D = {'demo_unidad6': DEMO_TAG}


def lookup(frm: str, local: str, foreign: str, alias: str) -> list[dict]:
    return [
        {'$lookup': {'from': frm, 'localField': local, 'foreignField': foreign, 'as': alias}},
        {'$unwind': '$' + alias},
    ]


SALES_TOTALS = [
    {'$match': D},
    {'$unwind': '$detalles'},
    {'$group': {
        '_id': '$id_venta',
        'total_venta': {'$sum': {'$multiply': ['$detalles.precio_unitario', '$detalles.cantidad']}},
        'unidades': {'$sum': '$detalles.cantidad'},
    }},
    {'$sort': {'_id': 1}},
]

SALES_VIEW = [
    {'$match': D},
    *lookup('usuario', 'id_cliente', 'cliente.id_cliente', 'datos_cliente'),
    {'$project': {
        '_id': 0, 'id_venta': 1, 'fecha_venta': 1, 'metodo_pago': 1, 'estado_venta': 1,
        'cliente': {'$concat': ['$datos_cliente.nombre', ' ', '$datos_cliente.apellido_paterno']},
        'cantidad_productos': {'$sum': '$detalles.cantidad'},
        'total_venta': {'$sum': {'$map': {'input': '$detalles', 'as': 'r', 'in': {
            '$multiply': ['$$r.precio_unitario', '$$r.cantidad']
        }}}},
    }},
    {'$sort': {'id_venta': 1}},
]

CATALOG_VIEW = [
    {'$match': D},
    {'$project': {'_id': 0, 'id_instrumento': 1, 'nombre_instrumento': 1,
                  'marca': 1, 'categoria': '$categoria_instrumento.nombre_categoria',
                  'precio_venta': 1, 'stock_actual': 1}},
    {'$sort': {'nombre_instrumento': 1}},
]

CLASSES_VIEW = [
    {'$match': D},
    *lookup('usuario', 'id_maestro', 'maestro.id_maestro', 'docente'),
    *lookup('periodo_academico', 'id_periodo', 'id_periodo', 'periodo'),
    {'$project': {'_id': 0, 'id_clase': 1, 'nombre_clase': 1, 'nivel': 1,
                  'costo_mensual': 1, 'horarios': 1,
                  'docente': {'$concat': ['$docente.nombre', ' ', '$docente.apellido_paterno']},
                  'periodo': '$periodo.nombre_periodo'}},
    {'$sort': {'id_clase': 1}},
]

VIEWS: dict[str, tuple[str, list[dict[str, Any]]]] = {
    'vista_u6_ventas_clientes': ('venta', SALES_VIEW),
    'vista_u6_catalogo': ('instrumento', CATALOG_VIEW),
    'vista_u6_clases': ('clase', CLASSES_VIEW),
}


def build_catalog() -> list[Exercise]:
    simple = [
        Exercise('S01', 'simples', 'Usuarios de prueba', 'Perfiles de clientes, maestros y administradores embebidos.', 'usuario', 'find', D,
                 {'_id': 0, 'id_usuario': 1, 'nombre_usuario': 1, 'nombre': 1, 'apellido_paterno': 1, 'cliente': 1, 'maestro': 1, 'administrador': 1}),
        Exercise('S02', 'simples', 'Usuario migrado', 'Usuarios originales de Neon (sin campos sensibles).', 'usuario', 'find', {'demo_unidad6': {'$ne': DEMO_TAG}},
                 {'_id': 0, 'id_usuario': 1, 'nombre_usuario': 1, 'nombre': 1, 'apellido_paterno': 1, 'activo': 1}),
        Exercise('S03', 'simples', 'Maestros activos', 'Filtro por propiedad anidada maestro.activo.', 'usuario', 'find', {'demo_unidad6': DEMO_TAG, 'maestro.activo': True},
                 {'_id': 0, 'nombre': 1, 'apellido_paterno': 1, 'maestro.especialidad': 1}),
        Exercise('S04', 'simples', 'Instrumentos de más de $5,000', 'Filtrado por precio utilizando $gt.', 'instrumento', 'find', {'demo_unidad6': DEMO_TAG, 'precio_venta': {'$gt': 5000}},
                 {'_id': 0, 'nombre_instrumento': 1, 'precio_venta': 1, 'stock_actual': 1}),
        Exercise('S05', 'simples', 'Catálogo por precio', 'ORDER BY equivalente con sort descendente.', 'instrumento', 'find', D,
                 {'_id': 0, 'nombre_instrumento': 1, 'precio_venta': 1, 'categoria_instrumento': 1}, {'precio_venta': -1}),
        Exercise('S06', 'simples', 'Ventas y sus artículos', 'Relación embebida: arreglos de detalles.', 'venta', 'find', D,
                 {'_id': 0, 'id_venta': 1, 'fecha_venta': 1, 'metodo_pago': 1, 'detalles': 1}),
        Exercise('S07', 'simples', 'Horarios de clase', 'Arreglo embebido sin JOIN.', 'clase', 'find', D,
                 {'_id': 0, 'nombre_clase': 1, 'nivel': 1, 'horarios': 1}),
        Exercise('S08', 'simples', 'Pagos pendientes', 'Documentos con estado_pago Pendiente.', 'pago_clase', 'find', {'demo_unidad6': DEMO_TAG, 'estado_pago': 'Pendiente'},
                 {'_id': 0, 'id_pago_clase': 1, 'importe': 1, 'fecha_vencimiento': 1, 'estado_pago': 1}),
    ]
    joins = [
        Exercise('J01', 'joins', 'Ventas con clientes', '$lookup de ventas y usuarios con perfil de cliente.', 'venta', 'aggregate', pipeline=[
            {'$match': D}, *lookup('usuario', 'id_cliente', 'cliente.id_cliente', 'cliente_doc'),
            {'$project': {'_id': 0, 'id_venta': 1, 'metodo_pago': 1, 'estado_venta': 1,
                          'cliente': {'$concat': ['$cliente_doc.nombre', ' ', '$cliente_doc.apellido_paterno']},
                          'unidades': {'$sum': '$detalles.cantidad'}}},
            {'$sort': {'id_venta': 1}},
        ]),
        Exercise('J02', 'joins', 'Inscripciones, alumnos y clases', 'Dos $lookup vinculando tres colecciones.', 'inscripcion_clase', 'aggregate', pipeline=[
            {'$match': D}, *lookup('clase', 'id_clase', 'id_clase', 'curso'),
            *lookup('usuario', 'id_cliente', 'cliente.id_cliente', 'alumno'),
            {'$project': {'_id': 0, 'id_inscripcion': 1, 'alumno': {'$concat': ['$alumno.nombre', ' ', '$alumno.apellido_paterno']},
                          'clase': '$curso.nombre_clase', 'nivel': '$curso.nivel',
                          'costo_mensual_acordado': 1, 'estado_inscripcion': 1}},
        ]),
        Exercise('J03', 'joins', 'Clases y docentes', 'Clases relacionadas mediante maestro.id_maestro.', 'clase', 'aggregate', pipeline=[
            {'$match': D}, *lookup('usuario', 'id_maestro', 'maestro.id_maestro', 'docente'),
            {'$project': {'_id': 0, 'nombre_clase': 1, 'nivel': 1,
                          'maestro': '$docente.nombre', 'especialidad': '$docente.maestro.especialidad', 'horarios': 1}},
        ]),
        Exercise('J04', 'joins', 'Órdenes y proveedores', 'Orden con el nombre del proveedor.', 'orden_abastecimiento', 'aggregate', pipeline=[
            {'$match': D}, *lookup('proveedor', 'id_proveedor', 'id_proveedor', 'proveedor_doc'),
            {'$project': {'_id': 0, 'id_orden': 1, 'estado_orden': 1, 'fecha_orden': 1,
                          'proveedor': '$proveedor_doc.nombre_proveedor', 'detalles': 1}},
        ]),
        Exercise('J05', 'joins', 'Pagos e inscripciones', 'Estado del pago junto a la inscripción.', 'pago_clase', 'aggregate', pipeline=[
            {'$match': D}, *lookup('inscripcion_clase', 'id_inscripcion', 'id_inscripcion', 'inscripcion'),
            {'$project': {'_id': 0, 'id_pago_clase': 1, 'importe': 1, 'estado_pago': 1,
                          'id_inscripcion': 1, 'estado_inscripcion': '$inscripcion.estado_inscripcion',
                          'id_cliente': '$inscripcion.id_cliente'}},
        ]),
    ]
    agg = [
        Exercise('A01', 'agregadas', 'Total de cada venta', 'SUM y GROUP BY sobre líneas embebidas.', 'venta', 'aggregate', pipeline=SALES_TOTALS),
        Exercise('A02', 'agregadas', 'Resumen de ingresos', 'COUNT, SUM, AVG, MIN y MAX por venta.', 'venta', 'aggregate', pipeline=[
            *SALES_TOTALS[:3],
            {'$group': {'_id': None, 'numero_ventas': {'$sum': 1}, 'ingresos': {'$sum': '$total_venta'},
                        'promedio': {'$avg': '$total_venta'}, 'minimo': {'$min': '$total_venta'}, 'maximo': {'$max': '$total_venta'}}},
            {'$project': {'_id': 0}},
        ]),
        Exercise('A03', 'agregadas', 'Inventario por categoría', 'Stock y valor comercial por categoría.', 'instrumento', 'aggregate', pipeline=[
            {'$match': D}, {'$group': {'_id': '$categoria_instrumento.nombre_categoria', 'productos': {'$sum': 1},
                                     'stock_total': {'$sum': '$stock_actual'},
                                     'valor_inventario': {'$sum': {'$multiply': ['$stock_actual', '$precio_venta']}}}},
            {'$sort': {'_id': 1}},
        ]),
        Exercise('A04', 'agregadas', 'Pagos por estado', 'Total facturado y pendiente, agrupado por estado.', 'pago_clase', 'aggregate', pipeline=[
            {'$match': D}, {'$group': {'_id': '$estado_pago', 'numero_pagos': {'$sum': 1},
                                     'importe_total': {'$sum': '$importe'}, 'promedio': {'$avg': '$importe'}}},
            {'$sort': {'_id': 1}},
        ]),
        Exercise('A05', 'agregadas', 'Inscripciones por clase', 'COUNT de inscripciones de prueba por clase.', 'inscripcion_clase', 'aggregate', pipeline=[
            {'$match': D}, {'$group': {'_id': '$id_clase', 'inscripciones': {'$sum': 1},
                                     'importe_mensual': {'$sum': '$costo_mensual_acordado'}}},
            {'$sort': {'_id': 1}},
        ]),
    ]
    views = [
        Exercise('V01', 'vistas', 'Vista de ventas', 'Vista dinámica: clientes, cantidades y totales.', 'vista_u6_ventas_clientes', 'view'),
        Exercise('V02', 'vistas', 'Vista de catálogo', 'Nombre, categoría, existencias y precio.', 'vista_u6_catalogo', 'view'),
        Exercise('V03', 'vistas', 'Vista académica', 'Clases, docentes, periodos y horarios.', 'vista_u6_clases', 'view'),
    ]
    return [*simple, *joins, *agg, *views]


CATALOG = build_catalog()
BY_ID = {item.code: item for item in CATALOG}


def public_exercise(item: Exercise) -> dict:
    return {'id': item.code, 'categoria': item.category, 'titulo': item.title,
            'descripcion': item.description, 'coleccion': item.collection,
            'tipo': item.kind, 'codigo': exercise_code(item)}


async def run_exercise(database, item: Exercise) -> list[dict]:
    collection = database[item.collection]
    if item.kind == 'find':
        cursor = collection.find(item.filter or {}, item.projection or {'_id': 0})
        if item.sort:
            cursor = cursor.sort(list(item.sort.items()))
    elif item.kind == 'aggregate':
        cursor = await collection.aggregate(item.pipeline or [])
    else:
        cursor = collection.find({}, {'_id': 0})
    return await cursor.to_list(length=100)


async def prepare_views(database) -> list[str]:
    changed = []
    for name, (source, pipeline) in VIEWS.items():
        existing = await (await database.list_collections(filter={'name': name})).to_list(length=1)
        if not existing:
            await database.create_collection(name, viewOn=source, pipeline=pipeline)
        elif existing[0].get('type') == 'view':
            await database.command({'collMod': name, 'viewOn': source, 'pipeline': pipeline})
        else:
            raise ValueError(f'El nombre {name} ya corresponde a una colección física.')
        changed.append(name)
    return changed
