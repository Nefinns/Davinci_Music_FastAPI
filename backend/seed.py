from __future__ import annotations

from datetime import datetime, timezone
from bson import Decimal128

DEMO_TAG = 'unidad6_demo_2026'


def dt(day: str) -> datetime:
    return datetime.fromisoformat(day + 'T12:00:00+00:00').astimezone(timezone.utc)


def money(value: str) -> Decimal128:
    return Decimal128(value)


def demo_collections() -> dict[str, list[dict]]:
    """Idempotent, fictional docs. Preserve relational integer IDs for $lookup."""
    users = [
        {'_id': 'U6-USR-01', 'id_usuario': 60001, 'nombre_usuario': 'u6_cliente_andrea', 'nombre': 'Andrea', 'apellido_paterno': 'Martínez', 'apellido_materno': 'López', 'correo': 'andrea.u6@example.com', 'activo': True, 'fecha_registro': dt('2026-11-01'), 'cliente': {'id_cliente': 61001, 'id_usuario': 60001, 'fecha_alta': dt('2026-11-01')}},
        {'_id': 'U6-USR-02', 'id_usuario': 60002, 'nombre_usuario': 'u6_cliente_diego', 'nombre': 'Diego', 'apellido_paterno': 'García', 'apellido_materno': 'Ruiz', 'correo': 'diego.u6@example.com', 'activo': True, 'fecha_registro': dt('2026-11-01'), 'cliente': {'id_cliente': 61002, 'id_usuario': 60002, 'fecha_alta': dt('2026-11-01')}},
        {'_id': 'U6-USR-03', 'id_usuario': 60003, 'nombre_usuario': 'u6_maestra_sofia', 'nombre': 'Sofía', 'apellido_paterno': 'Hernández', 'apellido_materno': 'Vega', 'correo': 'sofia.u6@example.com', 'activo': True, 'fecha_registro': dt('2026-11-01'), 'maestro': {'id_maestro': 62001, 'id_usuario': 60003, 'especialidad': 'Guitarra', 'fecha_contratacion': dt('2026-10-01'), 'activo': True}},
        {'_id': 'U6-USR-04', 'id_usuario': 60004, 'nombre_usuario': 'u6_admin_luis', 'nombre': 'Luis', 'apellido_paterno': 'Torres', 'apellido_materno': 'Pérez', 'correo': 'luis.u6@example.com', 'activo': True, 'fecha_registro': dt('2026-11-01'), 'administrador': {'id_administrador': 63001, 'id_usuario': 60004, 'fecha_contratacion': dt('2026-10-01')}},
    ]
    instruments = [
        {'_id': 'U6-INS-01', 'id_instrumento': 64001, 'id_categoria': 1, 'nombre_instrumento': 'Guitarra acústica Yamaha F310', 'marca': 'Yamaha', 'modelo': 'F310', 'precio_venta': money('3200.00'), 'stock_actual': 12, 'activo': True, 'categoria_instrumento': {'id_categoria': 1, 'nombre_categoria': 'Cuerdas'}},
        {'_id': 'U6-INS-02', 'id_instrumento': 64002, 'id_categoria': 2, 'nombre_instrumento': 'Teclado Casio CT-S300', 'marca': 'Casio', 'modelo': 'CT-S300', 'precio_venta': money('5800.00'), 'stock_actual': 6, 'activo': True, 'categoria_instrumento': {'id_categoria': 2, 'nombre_categoria': 'Teclados'}},
        {'_id': 'U6-INS-03', 'id_instrumento': 64003, 'id_categoria': 3, 'nombre_instrumento': 'Batería electrónica Alesis', 'marca': 'Alesis', 'modelo': 'Nitro', 'precio_venta': money('12500.00'), 'stock_actual': 3, 'activo': True, 'categoria_instrumento': {'id_categoria': 3, 'nombre_categoria': 'Percusión'}},
    ]
    periods = [{'_id': 'U6-PER-01', 'id_periodo': 66001, 'nombre_periodo': '2026-B DEMO', 'fecha_inicio': dt('2026-08-01'), 'fecha_fin': dt('2026-12-15'), 'estado': 'Activo'}]
    classes = [
        {'_id': 'U6-CLA-01', 'id_clase': 65001, 'id_maestro': 62001, 'id_instrumento': 64001, 'id_periodo': 66001, 'nombre_clase': 'Guitarra inicial', 'nivel': 'Básico', 'costo_mensual': money('800.00'), 'cupo_maximo': 15, 'activa': True, 'horarios': [{'id_horario': 65011, 'dia_semana': 'Lunes', 'hora_inicio': '16:00', 'hora_fin': '17:30', 'salon': 'A1'}, {'id_horario': 65012, 'dia_semana': 'Miércoles', 'hora_inicio': '16:00', 'hora_fin': '17:30', 'salon': 'A1'}]},
        {'_id': 'U6-CLA-02', 'id_clase': 65002, 'id_maestro': 62001, 'id_instrumento': 64001, 'id_periodo': 66001, 'nombre_clase': 'Guitarra intermedia', 'nivel': 'Intermedio', 'costo_mensual': money('1050.00'), 'cupo_maximo': 10, 'activa': True, 'horarios': [{'id_horario': 65013, 'dia_semana': 'Viernes', 'hora_inicio': '17:00', 'hora_fin': '19:00', 'salon': 'A2'}]},
    ]
    enrollments = [
        {'_id': 'U6-MAT-01', 'id_inscripcion': 67001, 'id_cliente': 61001, 'id_clase': 65001, 'fecha_inscripcion': dt('2026-11-02'), 'costo_mensual_acordado': money('800.00'), 'estado_inscripcion': 'Activa'},
        {'_id': 'U6-MAT-02', 'id_inscripcion': 67002, 'id_cliente': 61002, 'id_clase': 65002, 'fecha_inscripcion': dt('2026-11-02'), 'costo_mensual_acordado': money('1050.00'), 'estado_inscripcion': 'Activa'},
    ]
    payments = [
        {'_id': 'U6-PAG-01', 'id_pago_clase': 68001, 'id_inscripcion': 67001, 'periodo_pagado': dt('2026-11-01'), 'importe': money('800.00'), 'fecha_vencimiento': dt('2026-11-10'), 'fecha_pago': dt('2026-11-03'), 'metodo_pago': 'Tarjeta', 'estado_pago': 'Pagado'},
        {'_id': 'U6-PAG-02', 'id_pago_clase': 68002, 'id_inscripcion': 67002, 'periodo_pagado': dt('2026-11-01'), 'importe': money('1050.00'), 'fecha_vencimiento': dt('2026-11-10'), 'fecha_pago': None, 'metodo_pago': None, 'estado_pago': 'Pendiente'},
    ]
    sales = [
        {'_id': 'U6-VEN-01', 'id_venta': 69001, 'id_cliente': 61001, 'id_administrador': 63001, 'fecha_venta': dt('2026-11-03'), 'metodo_pago': 'Tarjeta', 'estado_venta': 'Completada', 'detalles': [{'id_instrumento': 64001, 'cantidad': 1, 'precio_unitario': money('3200.00')}, {'id_instrumento': 64002, 'cantidad': 1, 'precio_unitario': money('5800.00')}]},
        {'_id': 'U6-VEN-02', 'id_venta': 69002, 'id_cliente': 61002, 'id_administrador': 63001, 'fecha_venta': dt('2026-11-04'), 'metodo_pago': 'Efectivo', 'estado_venta': 'Completada', 'detalles': [{'id_instrumento': 64001, 'cantidad': 2, 'precio_unitario': money('3200.00')}]},
    ]
    suppliers = [{'_id': 'U6-PRO-01', 'id_proveedor': 70001, 'nombre_proveedor': 'Distribuidora Musical Demo', 'rfc': 'DMD010101AAA', 'correo': 'ventas@example.com', 'activo': True}]
    orders = [{'_id': 'U6-ORD-01', 'id_orden': 71001, 'id_proveedor': 70001, 'id_administrador': 63001, 'fecha_orden': dt('2026-11-03'), 'estado_orden': 'Pendiente', 'detalles': [{'id_instrumento': 64001, 'cantidad_solicitada': 8, 'cantidad_recibida': 0, 'costo_unitario': money('2100.00')}, {'id_instrumento': 64002, 'cantidad_solicitada': 4, 'cantidad_recibida': 0, 'costo_unitario': money('4000.00')}]}]
    batches = {'usuario': users, 'instrumento': instruments, 'periodo_academico': periods, 'clase': classes, 'inscripcion_clase': enrollments, 'pago_clase': payments, 'venta': sales, 'proveedor': suppliers, 'orden_abastecimiento': orders}
    for docs in batches.values():
        for item in docs:
            item['demo_unidad6'] = DEMO_TAG
    return batches


async def seed_database(database) -> dict[str, int]:
    """Inserts only demo ids not already present. Never modifies migrated docs."""
    counts = {}
    for collection, documents in demo_collections().items():
        added = 0
        for document in documents:
            result = await database[collection].update_one(
                {'_id': document['_id']}, {'$setOnInsert': document}, upsert=True
            )
            added += int(result.upserted_id is not None)
        counts[collection] = added
    return counts
