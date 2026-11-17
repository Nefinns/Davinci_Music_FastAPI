-- OPCIONAL: datos FICTICIOS para presentación, SIN credenciales ni cobros ficticios.
-- Reejecutable; no modifica registros preexistentes. Productos marcados DEMO, sin fotos.
-- Ejecutar sobre BD de pruebas después de las migraciones. No crea usuarios de SuperTokens.
BEGIN;
-- Serializar este sembrado para no duplicar instrumentos al ejecutarlo simultáneamente.
SELECT pg_advisory_xact_lock(7364,1);
INSERT INTO proveedor(nombre_proveedor,rfc,correo,direccion,telefono) VALUES
 ('DEMO Distribuidora Armonía','DAR010101A11','armonia@example.invalid','Domicilio ficticio 100','3300000001'),
 ('DEMO Instrumentos del Occidente','DIO010101B22','occidente@example.invalid','Domicilio ficticio 200','3300000002'),
 ('DEMO Accesorios Musicales','DAM010101C33','accesorios@example.invalid','Domicilio ficticio 300','3300000003')
 ON CONFLICT(rfc) DO NOTHING;
INSERT INTO categoria_instrumento(nombre_categoria,descripcion) VALUES
 ('DEMO Cuerdas','Instrumentos ficticios para presentación'),
 ('DEMO Teclados','Instrumentos ficticios para presentación'),
 ('DEMO Percusión','Instrumentos ficticios para presentación'),
 ('DEMO Vientos','Instrumentos ficticios para presentación')
 ON CONFLICT(nombre_categoria) DO NOTHING;
WITH productos(categoria,nombre,precio,stock) AS (VALUES
 ('DEMO Cuerdas','DEMO Guitarra acústica de estudio',1890.00,12),
 ('DEMO Cuerdas','DEMO Guitarra clásica para principiantes',1490.00,8),
 ('DEMO Cuerdas','DEMO Guitarra eléctrica de práctica',3250.00,6),
 ('DEMO Cuerdas','DEMO Bajo eléctrico de cuatro cuerdas',4190.00,5),
 ('DEMO Cuerdas','DEMO Ukulele soprano',790.00,15),
 ('DEMO Cuerdas','DEMO Ukulele concierto',1190.00,9),
 ('DEMO Cuerdas','DEMO Violín de estudio 4/4',2290.00,7),
 ('DEMO Cuerdas','DEMO Violín de estudio 3/4',1990.00,4),
 ('DEMO Teclados','DEMO Teclado de 61 teclas',3990.00,6),
 ('DEMO Teclados','DEMO Piano digital de estudio',9990.00,3),
 ('DEMO Teclados','DEMO Controlador musical de 49 teclas',2690.00,8),
 ('DEMO Percusión','DEMO Cajón de práctica',1290.00,10),
 ('DEMO Percusión','DEMO Batería acústica para estudio',7990.00,3),
 ('DEMO Percusión','DEMO Batería electrónica para práctica',8990.00,2),
 ('DEMO Percusión','DEMO Pandereta de estudio',290.00,20),
 ('DEMO Percusión','DEMO Bongós de práctica',1390.00,7),
 ('DEMO Vientos','DEMO Flauta dulce soprano',190.00,25),
 ('DEMO Vientos','DEMO Flauta transversal de estudio',3990.00,4),
 ('DEMO Vientos','DEMO Saxofón alto de estudio',8990.00,3),
 ('DEMO Vientos','DEMO Trompeta de estudio',4990.00,4))
INSERT INTO instrumento(id_categoria,nombre_instrumento,marca,modelo,precio_venta,stock_actual,activo)
 SELECT c.id_categoria,p.nombre,'DEMO','Presentación',p.precio,p.stock,TRUE
 FROM productos p JOIN categoria_instrumento c ON c.nombre_categoria=p.categoria
 WHERE NOT EXISTS(SELECT 1 FROM instrumento i WHERE i.nombre_instrumento=p.nombre);
INSERT INTO periodo_academico(nombre_periodo,fecha_inicio,fecha_fin,estado)
 VALUES('DEMO Presentación '||EXTRACT(YEAR FROM CURRENT_DATE)::text,CURRENT_DATE,CURRENT_DATE+180,'Abierto')
 ON CONFLICT(nombre_periodo) DO NOTHING;
-- Crear grupos solo si ya existe al menos un perfil docente activo y un usuario activo.
-- Cada horario se verifica contra maestro y salón para no introducir superposiciones.
DO $$
DECLARE docente INT; instrumento_demo INT; periodo_demo INT; grupo INT; j INT; dia TEXT; inicio TIME; fin TIME; nombre TEXT;
BEGIN
 SELECT m.id_maestro INTO docente FROM maestro m JOIN usuario u USING(id_usuario)
 WHERE m.activo AND u.activo ORDER BY m.id_maestro LIMIT 1;
 IF docente IS NULL THEN RAISE NOTICE 'No se crearon clases: primero registra un maestro real y su perfil docente desde la aplicación.'; RETURN; END IF;
 SELECT id_instrumento INTO instrumento_demo FROM instrumento WHERE nombre_instrumento='DEMO Guitarra acústica de estudio' ORDER BY id_instrumento LIMIT 1;
 SELECT id_periodo INTO periodo_demo FROM periodo_academico WHERE nombre_periodo='DEMO Presentación '||EXTRACT(YEAR FROM CURRENT_DATE)::text;
 LOCK TABLE horario_clase IN SHARE ROW EXCLUSIVE MODE;
 FOR j IN 1..4 LOOP
  dia := (ARRAY['Lunes','Martes','Miércoles','Jueves'])[j];
  inicio := '17:00'::time; fin := '18:00'::time; nombre := 'DEMO Guitarra grupo '||j::text;
  IF EXISTS(SELECT 1 FROM clase WHERE nombre_clase=nombre AND id_periodo=periodo_demo) THEN CONTINUE; END IF;
  IF EXISTS(SELECT 1 FROM clase c JOIN horario_clase h USING(id_clase) JOIN periodo_academico p USING(id_periodo)
    WHERE c.activa AND p.fecha_inicio<=CURRENT_DATE+180 AND p.fecha_fin>=CURRENT_DATE AND h.dia_semana=dia
    AND h.hora_inicio<fin AND h.hora_fin>inicio AND (c.id_maestro=docente OR lower(h.salon)=lower('DEMO Salón '||j::text)))
  THEN RAISE NOTICE 'Grupo % omitido por conflicto de horario.',j; CONTINUE; END IF;
  INSERT INTO clase(id_maestro,id_instrumento,id_periodo,nombre_clase,nivel,costo_mensual,cupo_maximo)
   VALUES(docente,instrumento_demo,periodo_demo,nombre,'Inicial',550.00,12) RETURNING id_clase INTO grupo;
  INSERT INTO horario_clase(id_clase,dia_semana,hora_inicio,hora_fin,salon) VALUES(grupo,dia,inicio,fin,'DEMO Salón '||j::text);
 END LOOP;
END $$;
COMMIT;
-- Órdenes, inscripciones y pagos se generan desde la interfaz para demostrar los flujos reales.
-- Pendiente ampliar catálogo comercial: imágenes autorizadas, especificaciones y precios reales.
