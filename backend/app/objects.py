"""Cinco vistas y cinco funciones PL/pgSQL vinculadas a cinco triggers."""
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

VIEWS = {
'v_u5_catalogo': '''
SELECT i.id_instrumento, i.nombre_instrumento, c.nombre_categoria,
       i.marca, i.precio_venta, i.stock_actual, i.activo
FROM instrumento i JOIN categoria_instrumento c ON c.id_categoria = i.id_categoria''',
'v_u5_clases': '''
SELECT c.id_clase, c.nombre_clase, c.nivel, c.cupo_maximo,
       u.nombre || ' ' || u.apellido_paterno AS maestro, m.especialidad,
       p.nombre_periodo, c.costo_mensual
FROM clase c JOIN maestro m ON m.id_maestro = c.id_maestro
JOIN usuario u ON u.id_usuario = m.id_usuario
JOIN periodo_academico p ON p.id_periodo = c.id_periodo''',
'v_u5_ventas': '''
SELECT v.id_venta, v.fecha_venta, u.nombre AS comprador, v.metodo_pago,
       v.estado_venta, COALESCE(SUM(d.cantidad*d.precio_unitario),0) AS total_mxn
FROM venta v JOIN cliente cl ON cl.id_cliente = v.id_cliente
JOIN usuario u ON u.id_usuario = cl.id_usuario
LEFT JOIN detalle_venta d ON d.id_venta = v.id_venta
GROUP BY v.id_venta, v.fecha_venta, u.nombre, v.metodo_pago, v.estado_venta''',
'v_u5_inscripciones': '''
SELECT ic.id_inscripcion, u.nombre AS alumno, c.nombre_clase,
       ic.estado_inscripcion, ic.costo_mensual_acordado, ic.fecha_inscripcion
FROM inscripcion_clase ic JOIN cliente cl ON cl.id_cliente = ic.id_cliente
JOIN usuario u ON u.id_usuario = cl.id_usuario
JOIN clase c ON c.id_clase = ic.id_clase''',
'v_u5_abastecimiento': '''
SELECT oa.id_orden, p.nombre_proveedor, oa.estado_orden, oa.fecha_orden,
       COALESCE(SUM(d.cantidad_solicitada),0) AS unidades_solicitadas,
       COALESCE(SUM(d.cantidad_recibida),0) AS unidades_recibidas
FROM orden_abastecimiento oa JOIN proveedor p ON p.id_proveedor = oa.id_proveedor
LEFT JOIN detalle_orden d ON d.id_orden = oa.id_orden
GROUP BY oa.id_orden, p.nombre_proveedor, oa.estado_orden, oa.fecha_orden'''
}

FUNCTIONS = {
'T01': '''
CREATE OR REPLACE FUNCTION fn_u5_validar_stock()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.stock_actual < 0 THEN
        RAISE EXCEPTION 'Unidad 5: no se permite stock negativo';
    END IF;
    RETURN NEW;
END;
$$;''',
'T02': '''
CREATE OR REPLACE FUNCTION fn_u5_validar_precio()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.precio_venta <= 0 THEN
        RAISE EXCEPTION 'Unidad 5: el precio de venta debe ser positivo';
    END IF;
    RETURN NEW;
END;
$$;''',
'T03': '''
CREATE OR REPLACE FUNCTION fn_u5_descuento_stock()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.cantidad <= 0 OR NEW.precio_unitario <= 0 THEN
        RAISE EXCEPTION 'Unidad 5: cantidad y precio deben ser positivos';
    END IF;
    UPDATE instrumento SET stock_actual = stock_actual - NEW.cantidad
    WHERE id_instrumento = NEW.id_instrumento AND stock_actual >= NEW.cantidad;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unidad 5: instrumento sin stock suficiente';
    END IF;
    RETURN NEW;
END;
$$;''',
'T04': '''
CREATE OR REPLACE FUNCTION fn_u5_validar_cupo()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    limite INTEGER;
    actual INTEGER;
BEGIN
    IF NEW.estado_inscripcion <> 'Activa' THEN
        RETURN NEW;
    END IF;
    SELECT cupo_maximo INTO limite FROM clase WHERE id_clase = NEW.id_clase FOR UPDATE;
    IF limite IS NULL THEN
        RAISE EXCEPTION 'Unidad 5: clase inexistente';
    END IF;
    SELECT COUNT(*) INTO actual FROM inscripcion_clase
    WHERE id_clase = NEW.id_clase AND estado_inscripcion = 'Activa'
    AND (TG_OP = 'INSERT' OR id_inscripcion <> NEW.id_inscripcion);
    IF actual >= limite THEN
        RAISE EXCEPTION 'Unidad 5: la clase ya alcanzó el cupo máximo';
    END IF;
    RETURN NEW;
END;
$$;''',
'T05': '''
CREATE OR REPLACE FUNCTION fn_u5_validar_recepcion()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.cantidad_solicitada <= 0 OR NEW.cantidad_recibida < 0
       OR NEW.cantidad_recibida > NEW.cantidad_solicitada THEN
        RAISE EXCEPTION 'Unidad 5: recepción fuera del rango solicitado';
    END IF;
    RETURN NEW;
END;
$$;''',
}

TRIGGERS = {
'T01': ('tr_u5_validar_stock','instrumento','BEFORE INSERT OR UPDATE OF stock_actual', 'fn_u5_validar_stock'),
'T02': ('tr_u5_validar_precio','instrumento','BEFORE INSERT OR UPDATE OF precio_venta', 'fn_u5_validar_precio'),
'T03': ('tr_u5_descuento_stock','detalle_venta','AFTER INSERT', 'fn_u5_descuento_stock'),
'T04': ('tr_u5_validar_cupo','inscripcion_clase','BEFORE INSERT OR UPDATE OF id_clase, estado_inscripcion', 'fn_u5_validar_cupo'),
'T05': ('tr_u5_validar_recepcion','detalle_orden','BEFORE INSERT OR UPDATE OF cantidad_solicitada, cantidad_recibida', 'fn_u5_validar_recepcion'),
}

def trigger_source(code):
    trigger, table, event, fn = TRIGGERS[code]
    return FUNCTIONS[code] + f'\n\nCREATE TRIGGER {trigger}\n{event} ON {table}\nFOR EACH ROW EXECUTE FUNCTION {fn}();'


def install_objects(conn):
    for name, body in VIEWS.items():
        conn.exec_driver_sql(f'CREATE OR REPLACE VIEW {name} AS {body}')
    for code, sql in FUNCTIONS.items():
        conn.exec_driver_sql(sql)
        trigger, table, event, fn = TRIGGERS[code]
        conn.exec_driver_sql(f'DROP TRIGGER IF EXISTS {trigger} ON {table}')
        conn.exec_driver_sql(f'CREATE TRIGGER {trigger} {event} ON {table} FOR EACH ROW EXECUTE FUNCTION {fn}()')


def _expected_rejection(conn, statement, values):
    sp = conn.begin_nested()
    try:
        conn.execute(text(statement), values)
        sp.rollback()
        return {'resultado': 'No se produjo el rechazo esperado', 'cumple': False}
    except SQLAlchemyError as exc:
        sp.rollback()
        raw = str(getattr(exc, 'orig', exc)).splitlines()[0]
        return {'resultado': 'Operación bloqueada correctamente', 'cumple': True, 'detalle': raw[:230]}


def demo_trigger(conn, code):
    """El llamador abre transacción y ejecuta rollback incondicional al terminar."""
    if code == 'T01':
        instrument = conn.execute(text('SELECT id_instrumento FROM instrumento ORDER BY id_instrumento LIMIT 1')).scalar_one()
        result = _expected_rejection(conn, 'UPDATE instrumento SET stock_actual = -1 WHERE id_instrumento = :id', {'id': instrument})
        result['ejemplo'] = 'Actualizar stock a -1'
        return result
    if code == 'T02':
        instrument = conn.execute(text('SELECT id_instrumento FROM instrumento ORDER BY id_instrumento LIMIT 1')).scalar_one()
        result = _expected_rejection(conn, 'UPDATE instrumento SET precio_venta = 0 WHERE id_instrumento = :id', {'id': instrument})
        result['ejemplo'] = 'Actualizar precio a $0'
        return result
    if code == 'T03':
        instrument = conn.execute(text('SELECT id_instrumento, stock_actual, precio_venta FROM instrumento WHERE stock_actual > 1 ORDER BY id_instrumento LIMIT 1')).mappings().one()
        ids = conn.execute(text('SELECT (SELECT id_cliente FROM cliente ORDER BY id_cliente LIMIT 1) AS id_cliente, (SELECT id_administrador FROM administrador ORDER BY id_administrador LIMIT 1) AS id_admin')).mappings().one()
        sale = conn.execute(text("INSERT INTO venta(id_cliente,id_administrador,metodo_pago) VALUES (:c,:a,'Efectivo') RETURNING id_venta"), {'c':ids['id_cliente'],'a':ids['id_admin']}).scalar_one()
        conn.execute(text('INSERT INTO detalle_venta(id_venta,id_instrumento,cantidad,precio_unitario) VALUES (:v,:i,1,:p)'), {'v':sale,'i':instrument['id_instrumento'],'p':instrument['precio_venta']})
        after = conn.execute(text('SELECT stock_actual FROM instrumento WHERE id_instrumento=:i'), {'i':instrument['id_instrumento']}).scalar_one()
        return {'resultado': 'Se descontó una unidad; se revertirá la transacción', 'cumple': after == instrument['stock_actual'] - 1,
                'stock_antes': instrument['stock_actual'], 'stock_despues_temporal': after, 'ejemplo': 'Insertar detalle de venta de 1 unidad'}
    if code == 'T04':
        row = conn.execute(text("""SELECT c.id_clase, c.cupo_maximo, COUNT(ic.id_inscripcion) AS inscritos
        FROM clase c LEFT JOIN inscripcion_clase ic ON ic.id_clase = c.id_clase AND ic.estado_inscripcion='Activa'
        GROUP BY c.id_clase, c.cupo_maximo ORDER BY c.cupo_maximo, c.id_clase LIMIT 1""")).mappings().one()
        first_client = conn.execute(text('SELECT id_cliente FROM cliente ORDER BY id_cliente LIMIT 1')).scalar_one()
        for _ in range(max(0, row['cupo_maximo'] - row['inscritos'])):
            conn.execute(text("""INSERT INTO inscripcion_clase(id_cliente,id_clase,costo_mensual_acordado,estado_inscripcion)
                VALUES (:cliente,:clase,300,'Activa')"""), {'cliente':first_client, 'clase':row['id_clase']})
        result = _expected_rejection(conn, """INSERT INTO inscripcion_clase(id_cliente,id_clase,costo_mensual_acordado,estado_inscripcion)
            VALUES (:cliente,:clase,300,'Activa')""", {'cliente':first_client,'clase':row['id_clase']})
        result['ejemplo'] = 'Registrar una inscripción por encima del cupo máximo'
        return result
    if code == 'T05':
        item = conn.execute(text('SELECT id_orden, id_instrumento FROM detalle_orden ORDER BY id_orden, id_instrumento LIMIT 1')).mappings().one()
        result = _expected_rejection(conn, 'UPDATE detalle_orden SET cantidad_recibida = cantidad_solicitada + 1 WHERE id_orden=:o AND id_instrumento=:i', {'o':item['id_orden'],'i':item['id_instrumento']})
        result['ejemplo'] = 'Recibir más piezas de las solicitadas'
        return result
    raise ValueError('Ejercicio no encontrado')
