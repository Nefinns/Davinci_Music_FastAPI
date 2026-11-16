-- OPCIONAL. Datos ficticios identificados DEMO; no crea usuarios ni identidades.
-- Requiere al menos un instrumento activo. Primero crear/asignar un maestro desde la app.
-- Ejecutar nuevamente NO duplica clases, horarios ni periodo.
BEGIN;
INSERT INTO periodo_academico(nombre_periodo,fecha_inicio,fecha_fin,estado)
VALUES('DEMO Presentación',CURRENT_DATE-7,CURRENT_DATE+120,'Abierto')
ON CONFLICT(nombre_periodo) DO NOTHING;
DO $$
DECLARE docente INT; instr INT; periodo INT; clase_id INT; n INT;
BEGIN
 SELECT m.id_maestro INTO docente FROM maestro m JOIN usuario u USING(id_usuario)
 WHERE m.activo AND u.activo ORDER BY m.id_maestro LIMIT 1;
 SELECT id_instrumento INTO instr FROM instrumento WHERE activo ORDER BY id_instrumento LIMIT 1;
 SELECT id_periodo INTO periodo FROM periodo_academico WHERE nombre_periodo='DEMO Presentación';
 IF docente IS NULL OR instr IS NULL THEN
  RAISE NOTICE 'Se creó el periodo DEMO. Falta maestro o instrumento activo: créalos y vuelve a ejecutar.';
  RETURN;
 END IF;
 FOR n IN 1..3 LOOP
  SELECT id_clase INTO clase_id FROM clase WHERE nombre_clase='DEMO Taller musical '||n AND id_periodo=periodo LIMIT 1;
  IF clase_id IS NULL THEN
   INSERT INTO clase(id_maestro,id_instrumento,id_periodo,nombre_clase,nivel,costo_mensual,cupo_maximo)
   VALUES(docente,instr,periodo,'DEMO Taller musical '||n,'Inicial',450+n*100,10)
   RETURNING id_clase INTO clase_id;
   INSERT INTO horario_clase(id_clase,dia_semana,hora_inicio,hora_fin,salon)
   VALUES(clase_id,'Sábado',make_time(9+n,0,0),make_time(10+n,0,0),'DEMO Aula 1');
  END IF;
 END LOOP;
END $$;
COMMIT;
-- No inventa pagos, ventas ni inscripciones: generarlos con cuentas de prueba desde la interfaz.
-- Las clases DEMO deben revisarse por posibles choques con horarios reales existentes.
SELECT c.nombre_clase,c.costo_mensual,c.cupo_maximo FROM clase c
JOIN periodo_academico p USING(id_periodo) WHERE p.nombre_periodo='DEMO Presentación';
