-- Aplicar DESPUÉS de sprints_5_6_3.sql. Reejecutable, sin borrar datos.
BEGIN;
ALTER TABLE venta ADD COLUMN IF NOT EXISTS estado_entrega VARCHAR(30) NOT NULL DEFAULT 'Por preparar';
CREATE TABLE IF NOT EXISTS solicitud_reembolso (
 id_venta INT PRIMARY KEY REFERENCES venta(id_venta),
 motivo VARCHAR(500) NOT NULL,
 estado VARCHAR(30) NOT NULL DEFAULT 'Solicitado'
 CHECK (estado IN ('Solicitado','Procesando','Pendiente','RequiereAccion','Reembolsado','Fallido','Rechazado')),
 solicitado_por INT NOT NULL REFERENCES usuario(id_usuario),
 solicitado TIMESTAMPTZ NOT NULL DEFAULT now(),
 resuelto_por INT REFERENCES usuario(id_usuario),
 resolucion VARCHAR(500),
 actualizado TIMESTAMPTZ NOT NULL DEFAULT now(),
 payment_intent VARCHAR(255),
 stripe_refund_id VARCHAR(255) UNIQUE,
 stock_devuelto BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE IF NOT EXISTS historial_venta (
 id_historial BIGSERIAL PRIMARY KEY,
 id_venta INT NOT NULL REFERENCES venta(id_venta),
 id_usuario INT NOT NULL REFERENCES usuario(id_usuario),
 accion VARCHAR(100) NOT NULL,
 fecha TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS historial_venta_venta ON historial_venta(id_venta,fecha);
COMMIT;
