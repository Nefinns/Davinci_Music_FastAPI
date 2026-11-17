-- Solo consulta. No acredita pagos ni modifica datos.
SELECT table_name FROM information_schema.tables WHERE table_schema='public'
 AND table_name IN ('suscripcion_escuela','factura_escuela','asistencia_clase');
SELECT s.id_inscripcion,s.estado,s.stripe_session_id,s.stripe_subscription_id,s.centavos,s.actualizado
 FROM suscripcion_escuela s ORDER BY id_inscripcion;
SELECT p.id_inscripcion,p.periodo_pagado,p.importe,p.estado_pago,f.stripe_invoice_id
 FROM pago_clase p LEFT JOIN factura_escuela f USING(id_pago_clase) ORDER BY p.id_pago_clase DESC;
SELECT estado,count(*) FROM asistencia_clase GROUP BY estado;
-- Debe devolver cero filas:
SELECT f.stripe_invoice_id,count(*) FROM factura_escuela f GROUP BY 1 HAVING count(*)>1;
