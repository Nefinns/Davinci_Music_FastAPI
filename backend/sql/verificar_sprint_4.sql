-- Solo consulta; ejecutar después de la migración.
SELECT table_name FROM information_schema.tables WHERE table_schema='public'
 AND table_name IN ('solicitud_reembolso','historial_venta');
SELECT column_name,data_type,column_default FROM information_schema.columns
 WHERE table_schema='public' AND table_name='venta' AND column_name='estado_entrega';
SELECT estado_venta,estado_entrega,count(*) AS ventas FROM venta GROUP BY 1,2 ORDER BY 1,2;
SELECT r.id_venta,r.estado,r.stripe_refund_id,r.stock_devuelto,v.estado_venta,v.estado_entrega
 FROM solicitud_reembolso r JOIN venta v USING(id_venta) ORDER BY r.id_venta;
-- Los siguientes resultados deben estar vacíos salvo inconsistencias anteriores:
SELECT id_instrumento,nombre_instrumento,stock_actual FROM instrumento WHERE stock_actual<0;
SELECT o.id_orden,o.estado_orden,d.* FROM orden_abastecimiento o JOIN detalle_orden d USING(id_orden)
 WHERE d.cantidad_recibida>d.cantidad_solicitada OR
 (o.estado_orden='Recibida' AND d.cantidad_recibida<>d.cantidad_solicitada);
SELECT x.id_inscripcion,x.estado_inscripcion,c.nombre_clase,u.correo AS profesor
 FROM inscripcion_clase x JOIN cliente cl USING(id_cliente) JOIN clase c USING(id_clase)
 JOIN maestro m USING(id_maestro) JOIN usuario u ON u.id_usuario=m.id_usuario
 WHERE cl.id_usuario=m.id_usuario AND x.estado_inscripcion='Activa';
-- Si aparecen inscripciones del propio profesor, revisarlas en Administración > Escuela.
-- No se borran ni dan de baja automáticamente.
