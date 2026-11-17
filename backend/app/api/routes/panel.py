import csv,io,unicodedata
from typing import Literal
from fastapi import APIRouter,Depends
from fastapi.responses import Response
from sqlmodel import Session
from app.api.routes.escuela import uno,filas
from app.core.dependencies import requerir_rol
from app.db.session import obtener_sesion
router=APIRouter(prefix='/panel',tags=['Panel y CSV'],dependencies=[Depends(requerir_rol('administrador'))])
@router.get('/resumen')
def resumen(db:Session=Depends(obtener_sesion)):
    return dict(uno(db,'''SELECT
    (SELECT count(*) FROM usuario WHERE activo) AS usuarios,
    (SELECT count(DISTINCT id_cliente) FROM inscripcion_clase WHERE estado_inscripcion='Activa') AS alumnos,
    (SELECT count(*) FROM clase WHERE activa) AS clases,
    (SELECT count(*) FROM venta WHERE estado_venta='Pagada' AND estado_entrega<>'Entregada') AS pedidos,
    (SELECT COALESCE(sum(d.cantidad*d.precio_unitario),0) FROM detalle_venta d JOIN venta v USING(id_venta) WHERE v.estado_venta IN ('Pagada','Completada')) AS ventas_netas,
    (SELECT COALESCE(sum(importe),0) FROM pago_clase WHERE estado_pago='Pagado') AS mensualidades,
    (SELECT count(*) FROM pago_clase WHERE estado_pago IN ('Pendiente','Vencido')) AS pagos_pendientes,
    (SELECT count(*) FROM instrumento WHERE activo AND stock_actual<=2) AS stock_bajo'''))
REPORTES={
 'ventas':'''SELECT v.id_venta,v.fecha_venta,u.nombre||' '||u.apellido_paterno||' '||COALESCE(u.apellido_materno,'') AS cliente,v.estado_venta,v.estado_entrega,
 COALESCE(sum(d.cantidad*d.precio_unitario),0) AS total FROM venta v JOIN cliente cl USING(id_cliente) JOIN usuario u USING(id_usuario)
 LEFT JOIN detalle_venta d USING(id_venta) GROUP BY v.id_venta,u.id_usuario ORDER BY v.id_venta''',
 'inscripciones':'''SELECT x.id_inscripcion,c.nombre_clase,u.nombre||' '||u.apellido_paterno AS alumno,x.estado_inscripcion,x.costo_mensual_acordado
 FROM inscripcion_clase x JOIN clase c USING(id_clase) JOIN cliente cl USING(id_cliente) JOIN usuario u USING(id_usuario) ORDER BY x.id_inscripcion''',
 'mensualidades':'''SELECT p.id_pago_clase,p.id_inscripcion,c.nombre_clase,u.nombre||' '||u.apellido_paterno AS alumno,
 p.periodo_pagado,p.importe,p.fecha_vencimiento,p.fecha_pago,p.estado_pago FROM pago_clase p JOIN inscripcion_clase x USING(id_inscripcion)
 JOIN clase c USING(id_clase) JOIN cliente cl USING(id_cliente) JOIN usuario u USING(id_usuario) ORDER BY p.id_pago_clase''',
 'inventario':'''SELECT id_instrumento,nombre_instrumento,marca,modelo,stock_actual,precio_venta,activo FROM instrumento ORDER BY id_instrumento''',
 'asistencia':'''SELECT c.nombre_clase,u.nombre||' '||u.apellido_paterno AS alumno,a.fecha,a.estado FROM asistencia_clase a JOIN inscripcion_clase x USING(id_inscripcion)
 JOIN clase c USING(id_clase) JOIN cliente cl USING(id_cliente) JOIN usuario u USING(id_usuario) ORDER BY a.fecha,c.id_clase'''
}
def celda(v):
    s='' if v is None else str(v)
    return "'"+s if s.lstrip().startswith(('=','+','-','@','\t','\r')) else s
@router.get('/csv/{tipo}')
def exportar(tipo:Literal['ventas','inscripciones','mensualidades','inventario','asistencia'],db:Session=Depends(obtener_sesion)):
    result=db.execute(__import__('sqlalchemy').text(REPORTES[tipo]));columnas=list(result.keys())
    out=io.StringIO();w=csv.writer(out);w.writerow(columnas)
    for row in result:w.writerow([celda(v) for v in row])
    return Response('\ufeff'+out.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="davinci_{tipo}.csv"'})
