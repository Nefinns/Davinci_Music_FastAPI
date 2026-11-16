-- Migración ADITIVA sobre el esquema canónico existente. Respaldar antes.
BEGIN;
-- Una venta web no tiene administrador asignado hasta su atención posterior.
ALTER TABLE venta ALTER COLUMN id_administrador DROP NOT NULL;
CREATE TABLE IF NOT EXISTS compra_checkout (
 id_venta INT PRIMARY KEY REFERENCES venta(id_venta),
 solicitud UUID NOT NULL UNIQUE,
 stripe_session_id VARCHAR(255) UNIQUE,
 checkout_url TEXT,
 items_json JSONB NOT NULL,
 total_centavos BIGINT NOT NULL CHECK(total_centavos>0),
 creada TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS evento_pago (
 id_evento VARCHAR(255) PRIMARY KEY,
 recibido TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS inscripcion_activa_unica
 ON inscripcion_clase(id_cliente,id_clase) WHERE estado_inscripcion='Activa';
CREATE INDEX IF NOT EXISTS inscripcion_clase_estado ON inscripcion_clase(id_clase,estado_inscripcion);
CREATE INDEX IF NOT EXISTS venta_cliente_fecha ON venta(id_cliente,fecha_venta);
COMMIT;
-- Si falla el índice de inscripción: revisar duplicados activos existentes antes de reintentar.
