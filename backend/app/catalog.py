"""Catálogo cerrado de operaciones; no se ejecuta SQL enviado por el navegador."""
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Exercise:
    code: str
    group: str
    title: str
    description: str
    sql: str
    params: list[dict] = field(default_factory=list)

EXERCISES: dict[str, Exercise] = {}
GROUPS = [
    {'id': 'simples', 'title': 'Consultas simples', 'target': 25},
    {'id': 'joins', 'title': 'Operaciones JOIN', 'target': 15},
    {'id': 'agregadas', 'title': 'Funciones agregadas', 'target': 15},
    {'id': 'vistas', 'title': 'Vistas', 'target': 5},
    {'id': 'triggers', 'title': 'Funciones y disparadores', 'target': 5},
]

def P(name: str, label: str, kind: str, default):
    return {'name': name, 'label': label, 'kind': kind, 'default': default}

def add(code, group, title, description, sql, params=None):
    if code in EXERCISES:
        raise ValueError('Código duplicado: ' + code)
    EXERCISES[code] = Exercise(code, group, title, description, sql.strip(), params or [])

add('S01', 'simples', 'Inventario activo', 'Instrumentos activos ordenados por nombre.', '''
SELECT id_instrumento, nombre_instrumento, marca, precio_venta, stock_actual
FROM instrumento WHERE activo = TRUE ORDER BY nombre_instrumento LIMIT 100''')
add('S02', 'simples', 'Existencias bajas', 'Instrumentos con unidades inferiores al umbral.', '''
SELECT nombre_instrumento, stock_actual FROM instrumento
WHERE stock_actual < :max_stock ORDER BY stock_actual, nombre_instrumento''', [P('max_stock','Stock inferior a','int',6)])
add('S03', 'simples', 'Precio mínimo', 'Busca instrumentos por precio mínimo de venta.', '''
SELECT nombre_instrumento, marca, precio_venta FROM instrumento
WHERE precio_venta >= :min_price ORDER BY precio_venta DESC''', [P('min_price','Precio mínimo (MXN)','float',3000)])
add('S04', 'simples', 'Filtrar marca', 'Igualdad exacta de la marca.', '''
SELECT nombre_instrumento, marca, modelo, precio_venta FROM instrumento
WHERE marca = :marca ORDER BY precio_venta''', [P('marca','Marca','string','Yamaha')])
add('S05', 'simples', 'Búsqueda por nombre', 'Coincidencia parcial sin distinguir mayúsculas.', '''
SELECT id_instrumento, nombre_instrumento, precio_venta FROM instrumento
WHERE nombre_instrumento ILIKE '%' || :busqueda || '%' ORDER BY nombre_instrumento''', [P('busqueda','Buscar','string','guitarra')])
add('S06', 'simples', 'Lista de categorías', 'Proyección de categorías de instrumentos.', '''
SELECT id_categoria, nombre_categoria, descripcion FROM categoria_instrumento ORDER BY nombre_categoria''')
add('S07', 'simples', 'Usuarios activos', 'Usuarios ficticios; no consulta documentos ni contraseñas.', '''
SELECT id_usuario, nombre_usuario, nombre, apellido_paterno, activo
FROM usuario WHERE activo IS TRUE ORDER BY apellido_paterno, nombre''')
add('S08', 'simples', 'Maestros activos', 'Especialidades y contrataciones activas.', '''
SELECT id_maestro, especialidad, fecha_contratacion FROM maestro
WHERE activo IS TRUE ORDER BY especialidad''')
add('S09', 'simples', 'Clientes recientes', 'Muestra los clientes registrados más recientemente.', '''
SELECT id_cliente, id_usuario, fecha_alta FROM cliente ORDER BY fecha_alta DESC, id_cliente DESC LIMIT 10''')
add('S10', 'simples', 'Periodos académicos', 'Periodos disponibles y fechas.', '''
SELECT nombre_periodo, fecha_inicio, fecha_fin, estado FROM periodo_academico ORDER BY fecha_inicio DESC''')
add('S11', 'simples', 'Clases activas', 'Lista clases que se pueden impartir.', '''
SELECT id_clase, nombre_clase, nivel, cupo_maximo, costo_mensual FROM clase
WHERE activa IS TRUE ORDER BY nombre_clase''')
add('S12', 'simples', 'Clases por nivel', 'Selecciona clases de un nivel determinado.', '''
SELECT nombre_clase, nivel, cupo_maximo FROM clase WHERE nivel = :nivel ORDER BY nombre_clase''', [P('nivel','Nivel','string','Principiante')])
add('S13', 'simples', 'Horarios por día', 'Selecciona las clases de un día de la semana.', '''
SELECT id_clase, dia_semana, hora_inicio, hora_fin, salon FROM horario_clase
WHERE dia_semana = :dia ORDER BY hora_inicio''', [P('dia','Día','string','Lunes')])
add('S14', 'simples', 'Pagos pendientes', 'Pagos de clase con estado pendiente.', '''
SELECT id_pago_clase, id_inscripcion, importe, fecha_vencimiento FROM pago_clase
WHERE estado_pago = 'Pendiente' ORDER BY fecha_vencimiento''')
add('S15', 'simples', 'Pagos realizados', 'Pagos liquidados ordenados por fecha.', '''
SELECT id_pago_clase, importe, fecha_pago, metodo_pago FROM pago_clase
WHERE estado_pago = 'Pagado' ORDER BY fecha_pago DESC''')
add('S16', 'simples', 'Ventas completadas', 'Operaciones comerciales cerradas.', '''
SELECT id_venta, id_cliente, fecha_venta, metodo_pago FROM venta
WHERE estado_venta = 'Completada' ORDER BY fecha_venta DESC''')
add('S17', 'simples', 'Ventas por método', 'Filtra las ventas por forma de pago.', '''
SELECT id_venta, fecha_venta, metodo_pago, estado_venta FROM venta
WHERE metodo_pago = :metodo ORDER BY fecha_venta DESC''', [P('metodo','Método','string','Tarjeta')])
add('S18', 'simples', 'Proveedores activos', 'Directorio sintético sin datos sensibles reales.', '''
SELECT id_proveedor, nombre_proveedor, activo FROM proveedor
WHERE activo IS TRUE ORDER BY nombre_proveedor''')
add('S19', 'simples', 'Órdenes pendientes', 'Abastecimientos todavía sin cerrar.', '''
SELECT id_orden, id_proveedor, fecha_orden, estado_orden FROM orden_abastecimiento
WHERE estado_orden = 'Pendiente' ORDER BY fecha_orden DESC''')
add('S20', 'simples', 'Instrumentos por categoría', 'Filtrado usando la llave foránea de categoría.', '''
SELECT nombre_instrumento, precio_venta, stock_actual FROM instrumento
WHERE id_categoria = :id_categoria ORDER BY nombre_instrumento''', [P('id_categoria','ID de categoría','int',1)])
add('S21', 'simples', 'Clases más caras', 'Ordena el costo mensual descendente.', '''
SELECT nombre_clase, costo_mensual FROM clase ORDER BY costo_mensual DESC LIMIT 5''')
add('S22', 'simples', 'Sin existencias', 'Instrumentos agotados, incluso si siguen activos.', '''
SELECT nombre_instrumento, marca, stock_actual FROM instrumento WHERE stock_actual = 0''')
add('S23', 'simples', 'Altas recientes', 'Usuarios registrados en los últimos N días.', '''
SELECT nombre_usuario, fecha_registro FROM usuario
WHERE fecha_registro >= CURRENT_TIMESTAMP - (:dias * INTERVAL '1 day')
ORDER BY fecha_registro DESC''', [P('dias','Días','int',90)])
add('S24', 'simples', 'Vencimientos anteriores', 'Pagos cuya fecha de vencimiento antecede el día elegido.', '''
SELECT id_pago_clase, importe, estado_pago, fecha_vencimiento FROM pago_clase
WHERE fecha_vencimiento < CAST(:fecha AS DATE) ORDER BY fecha_vencimiento''', [P('fecha','Fecha límite','date','2026-12-01')])
add('S25', 'simples', 'Catálogo alfabético', 'Selección con orden múltiple y límite de filas.', '''
SELECT id_instrumento, nombre_instrumento, marca, modelo
FROM instrumento ORDER BY nombre_instrumento, marca LIMIT 20''')

add('J01','joins','Instrumentos y categorías','INNER JOIN de catálogo con clasificación.', '''
SELECT i.nombre_instrumento, c.nombre_categoria, i.precio_venta
FROM instrumento i INNER JOIN categoria_instrumento c ON c.id_categoria = i.id_categoria
ORDER BY c.nombre_categoria, i.nombre_instrumento''')
add('J02','joins','Maestro de cada clase','JOIN múltiple de clase, maestro y usuario.', '''
SELECT c.nombre_clase, u.nombre || ' ' || u.apellido_paterno AS maestro, m.especialidad
FROM clase c JOIN maestro m ON m.id_maestro = c.id_maestro
JOIN usuario u ON u.id_usuario = m.id_usuario ORDER BY c.nombre_clase''')
add('J03','joins','Instrumento de cada clase','Relación entre academia e inventario.', '''
SELECT c.nombre_clase, i.nombre_instrumento, c.nivel
FROM clase c JOIN instrumento i ON i.id_instrumento = c.id_instrumento ORDER BY c.nombre_clase''')
add('J04','joins','Clases y periodo','Asocia las clases con el calendario académico.', '''
SELECT c.nombre_clase, p.nombre_periodo, p.fecha_inicio, p.fecha_fin
FROM clase c INNER JOIN periodo_academico p ON p.id_periodo = c.id_periodo
ORDER BY p.fecha_inicio, c.nombre_clase''')
add('J05','joins','Horario completo','Vincula horario y nombre de clase.', '''
SELECT c.nombre_clase, h.dia_semana, h.hora_inicio, h.hora_fin, h.salon
FROM horario_clase h JOIN clase c ON c.id_clase = h.id_clase
ORDER BY h.dia_semana, h.hora_inicio''')
add('J06','joins','Identidad de clientes','JOIN cliente con usuario sin exponer datos personales sensibles.', '''
SELECT cl.id_cliente, u.nombre, u.apellido_paterno, cl.fecha_alta
FROM cliente cl JOIN usuario u ON u.id_usuario = cl.id_usuario ORDER BY cl.id_cliente''')
add('J07','joins','Inscripciones y alumnos','Cuatro tablas: inscripción, cliente, usuario y clase.', '''
SELECT ic.id_inscripcion, u.nombre AS alumno, c.nombre_clase, ic.estado_inscripcion
FROM inscripcion_clase ic JOIN cliente cl ON cl.id_cliente = ic.id_cliente
JOIN usuario u ON u.id_usuario = cl.id_usuario JOIN clase c ON c.id_clase = ic.id_clase
ORDER BY ic.id_inscripcion''')
add('J08','joins','Pagos e inscripción','Relaciona importe, estado y clase inscrita.', '''
SELECT pc.id_pago_clase, c.nombre_clase, pc.importe, pc.estado_pago
FROM pago_clase pc JOIN inscripcion_clase ic ON ic.id_inscripcion = pc.id_inscripcion
JOIN clase c ON c.id_clase = ic.id_clase ORDER BY pc.id_pago_clase''')
add('J09','joins','Ventas con comprador','Relaciona la venta con el usuario cliente.', '''
SELECT v.id_venta, u.nombre AS comprador, v.metodo_pago, v.fecha_venta
FROM venta v JOIN cliente cl ON cl.id_cliente = v.id_cliente
JOIN usuario u ON u.id_usuario = cl.id_usuario ORDER BY v.id_venta''')
add('J10','joins','Productos vendidos','Detalle de venta, catálogo y precio histórico.', '''
SELECT dv.id_venta, i.nombre_instrumento, dv.cantidad, dv.precio_unitario
FROM detalle_venta dv JOIN instrumento i ON i.id_instrumento = dv.id_instrumento
ORDER BY dv.id_venta, i.nombre_instrumento''')
add('J11','joins','Órdenes y proveedor','Relaciona abastecimientos con sus proveedores.', '''
SELECT oa.id_orden, p.nombre_proveedor, oa.estado_orden, oa.fecha_orden
FROM orden_abastecimiento oa INNER JOIN proveedor p ON p.id_proveedor = oa.id_proveedor
ORDER BY oa.id_orden''')
add('J12','joins','Detalle de abastecimiento','JOIN de órdenes, proveedores, detalles e instrumentos.', '''
SELECT oa.id_orden, p.nombre_proveedor, i.nombre_instrumento, d.cantidad_solicitada, d.cantidad_recibida
FROM detalle_orden d JOIN orden_abastecimiento oa ON oa.id_orden = d.id_orden
JOIN proveedor p ON p.id_proveedor = oa.id_proveedor
JOIN instrumento i ON i.id_instrumento = d.id_instrumento ORDER BY oa.id_orden''')
add('J13','joins','Categorías aunque estén vacías','LEFT JOIN conserva categorías sin instrumentos.', '''
SELECT c.nombre_categoria, i.nombre_instrumento, i.stock_actual
FROM categoria_instrumento c LEFT JOIN instrumento i ON i.id_categoria = c.id_categoria
ORDER BY c.nombre_categoria, i.nombre_instrumento''')
add('J14','joins','Instrumentos aún no vendidos','LEFT JOIN y filtro IS NULL para hallar productos sin ventas.', '''
SELECT i.id_instrumento, i.nombre_instrumento, i.stock_actual
FROM instrumento i LEFT JOIN detalle_venta dv ON dv.id_instrumento = i.id_instrumento
WHERE dv.id_venta IS NULL ORDER BY i.nombre_instrumento''')
add('J15','joins','Docentes sin grupo','LEFT JOIN permite encontrar docentes sin clases asignadas.', '''
SELECT u.nombre AS maestro, m.especialidad, m.id_maestro
FROM maestro m JOIN usuario u ON u.id_usuario = m.id_usuario
LEFT JOIN clase c ON c.id_maestro = m.id_maestro
WHERE c.id_clase IS NULL ORDER BY u.nombre''')

add('A01','agregadas','Conteo por categoría','COUNT de instrumentos, incluyendo categorías vacías.', '''
SELECT c.nombre_categoria, COUNT(i.id_instrumento) AS total_instrumentos
FROM categoria_instrumento c LEFT JOIN instrumento i ON i.id_categoria = c.id_categoria
GROUP BY c.id_categoria, c.nombre_categoria ORDER BY total_instrumentos DESC''')
add('A02','agregadas','Precio medio por categoría','AVG de precios agrupado por nombre.', '''
SELECT c.nombre_categoria, ROUND(AVG(i.precio_venta), 2) AS precio_promedio
FROM instrumento i JOIN categoria_instrumento c ON c.id_categoria = i.id_categoria
GROUP BY c.nombre_categoria ORDER BY precio_promedio DESC''')
add('A03','agregadas','Rango de precios','MIN y MAX para conocer extremos del catálogo.', '''
SELECT c.nombre_categoria, MIN(i.precio_venta) AS minimo, MAX(i.precio_venta) AS maximo
FROM instrumento i JOIN categoria_instrumento c ON c.id_categoria = i.id_categoria
GROUP BY c.nombre_categoria ORDER BY c.nombre_categoria''')
add('A04','agregadas','Unidades de inventario','SUM de unidades por marca.', '''
SELECT COALESCE(marca, 'Sin marca') AS marca, SUM(stock_actual) AS unidades
FROM instrumento GROUP BY marca ORDER BY unidades DESC''')
add('A05','agregadas','Valorización de inventario','SUM de precio multiplicado por existencias.', '''
SELECT c.nombre_categoria, SUM(i.stock_actual * i.precio_venta) AS valor_mxn
FROM instrumento i JOIN categoria_instrumento c ON c.id_categoria = i.id_categoria
GROUP BY c.nombre_categoria ORDER BY valor_mxn DESC''')
add('A06','agregadas','Grupos por maestro','COUNT de clases asignadas, incluso cero.', '''
SELECT u.nombre AS maestro, COUNT(c.id_clase) AS grupos
FROM maestro m JOIN usuario u ON u.id_usuario = m.id_usuario
LEFT JOIN clase c ON c.id_maestro = m.id_maestro
GROUP BY m.id_maestro, u.nombre ORDER BY grupos DESC''')
add('A07','agregadas','Inscritos por clase','COUNT y HAVING para clases que superan un mínimo.', '''
SELECT c.nombre_clase, COUNT(ic.id_inscripcion) AS inscritos
FROM clase c LEFT JOIN inscripcion_clase ic ON ic.id_clase = c.id_clase
AND ic.estado_inscripcion = 'Activa'
GROUP BY c.id_clase, c.nombre_clase HAVING COUNT(ic.id_inscripcion) >= :min_inscritos
ORDER BY inscritos DESC''', [P('min_inscritos','Mínimo de inscritos','int',1)])
add('A08','agregadas','Suma de pagos por estado','SUM y COUNT de pagos pagados o pendientes.', '''
SELECT estado_pago, COUNT(*) AS cantidad, SUM(importe) AS total_mxn
FROM pago_clase GROUP BY estado_pago ORDER BY total_mxn DESC''')
add('A09','agregadas','Ingresos mensuales de ventas','DATE_TRUNC y SUM de importes históricos.', '''
SELECT TO_CHAR(DATE_TRUNC('month', v.fecha_venta), 'YYYY-MM') AS mes,
SUM(dv.cantidad * dv.precio_unitario) AS ingresos_mxn
FROM venta v JOIN detalle_venta dv ON dv.id_venta = v.id_venta
WHERE v.estado_venta = 'Completada'
GROUP BY DATE_TRUNC('month', v.fecha_venta) ORDER BY mes''')
add('A10','agregadas','Compras por cliente','SUM de importe total por comprador.', '''
SELECT u.nombre AS cliente, COUNT(DISTINCT v.id_venta) AS num_ventas,
COALESCE(SUM(dv.cantidad * dv.precio_unitario), 0) AS gasto_mxn
FROM cliente cl JOIN usuario u ON u.id_usuario = cl.id_usuario
LEFT JOIN venta v ON v.id_cliente = cl.id_cliente AND v.estado_venta = 'Completada'
LEFT JOIN detalle_venta dv ON dv.id_venta = v.id_venta
GROUP BY cl.id_cliente, u.nombre ORDER BY gasto_mxn DESC''')
add('A11','agregadas','Productos más vendidos','SUM de cantidades de cada instrumento.', '''
SELECT i.nombre_instrumento, COALESCE(SUM(dv.cantidad), 0) AS unidades_vendidas
FROM instrumento i LEFT JOIN detalle_venta dv ON dv.id_instrumento = i.id_instrumento
GROUP BY i.id_instrumento, i.nombre_instrumento ORDER BY unidades_vendidas DESC''')
add('A12','agregadas','Órdenes por proveedor','Número de órdenes registradas por proveedor.', '''
SELECT p.nombre_proveedor, COUNT(o.id_orden) AS total_ordenes
FROM proveedor p LEFT JOIN orden_abastecimiento o ON o.id_proveedor = p.id_proveedor
GROUP BY p.id_proveedor, p.nombre_proveedor ORDER BY total_ordenes DESC''')
add('A13','agregadas','Abastecimiento pendiente','Resta de unidades recibidas y solicitadas por proveedor.', '''
SELECT p.nombre_proveedor, COALESCE(SUM(d.cantidad_solicitada),0) AS solicitadas,
COALESCE(SUM(d.cantidad_recibida),0) AS recibidas,
COALESCE(SUM(d.cantidad_solicitada-d.cantidad_recibida),0) AS pendientes
FROM proveedor p LEFT JOIN orden_abastecimiento o ON o.id_proveedor = p.id_proveedor
LEFT JOIN detalle_orden d ON d.id_orden = o.id_orden
GROUP BY p.id_proveedor, p.nombre_proveedor ORDER BY pendientes DESC''')
add('A14','agregadas','Usuarios según rol','COUNT DISTINCT con filtro para tres roles.', '''
SELECT COUNT(DISTINCT c.id_usuario) AS clientes,
COUNT(DISTINCT m.id_usuario) AS maestros,
COUNT(DISTINCT a.id_usuario) AS administradores
FROM usuario u LEFT JOIN cliente c ON c.id_usuario = u.id_usuario
LEFT JOIN maestro m ON m.id_usuario = u.id_usuario
LEFT JOIN administrador a ON a.id_usuario = u.id_usuario''')
add('A15','agregadas','Ventas según método de pago','COUNT y SUM para cada forma de pago.', '''
SELECT v.metodo_pago, COUNT(DISTINCT v.id_venta) AS ventas,
COALESCE(SUM(dv.cantidad * dv.precio_unitario),0) AS total_mxn
FROM venta v LEFT JOIN detalle_venta dv ON dv.id_venta = v.id_venta
WHERE v.estado_venta = 'Completada' GROUP BY v.metodo_pago ORDER BY total_mxn DESC''')

for idx, title, desc, view in [
    (1,'Vista de catálogo','Vista de productos, categorías y existencias','v_u5_catalogo'),
    (2,'Vista académica','Vista de clases con docentes y periodos','v_u5_clases'),
    (3,'Vista de ventas','Vista de ventas con sus importes calculados','v_u5_ventas'),
    (4,'Vista de inscripciones','Vista de alumnos y clases inscritas','v_u5_inscripciones'),
    (5,'Vista de abastecimiento','Vista de proveedores y recepción de pedidos','v_u5_abastecimiento'),
]:
    add(f'V{idx:02d}', 'vistas', title, desc, f'SELECT * FROM {view} ORDER BY 1 LIMIT 100')

for idx, title, desc, function, trig in [
    (1, 'Validar stock', 'Rechaza valores negativos al actualizar un instrumento.', 'fn_u5_validar_stock','tr_u5_validar_stock'),
    (2, 'Validar precio', 'Rechaza precios cero o negativos.', 'fn_u5_validar_precio','tr_u5_validar_precio'),
    (3, 'Descontar stock por venta', 'Descuenta unidades al insertar un detalle de venta.', 'fn_u5_descuento_stock','tr_u5_descuento_stock'),
    (4, 'Evitar sobrecupo de clase', 'Impide una inscripción que supera el cupo.', 'fn_u5_validar_cupo','tr_u5_validar_cupo'),
    (5, 'Control de recepción', 'Valida cantidades recibidas en abastecimiento.', 'fn_u5_validar_recepcion','tr_u5_validar_recepcion'),
]:
    add(f'T{idx:02d}', 'triggers', title, desc,
        f'-- Función PostgreSQL: {function}\n-- Disparador: {trig}\n-- Código completo disponible en backend/app/objects.py\n-- Ejecución: demostración transaccional con ROLLBACK.')

assert len(EXERCISES) == 65
assert all(sum(ex.group == g['id'] for ex in EXERCISES.values()) == g['target'] for g in GROUPS)

def list_catalog():
    return {'groups': GROUPS, 'exercises': [vars(e) for e in EXERCISES.values()], 'total': len(EXERCISES)}
