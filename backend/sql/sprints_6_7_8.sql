BEGIN;
CREATE TABLE IF NOT EXISTS suscripcion_escuela (
 id_inscripcion INT PRIMARY KEY REFERENCES inscripcion_clase(id_inscripcion),
 solicitud UUID NOT NULL UNIQUE,
 centavos BIGINT NOT NULL CHECK(centavos>=1000),
 nombre TEXT NOT NULL,
 fin_ciclo BIGINT NOT NULL,
 stripe_session_id TEXT UNIQUE,
 stripe_subscription_id TEXT UNIQUE,
 estado VARCHAR(40) NOT NULL DEFAULT 'Creando',
 cancelar BOOLEAN NOT NULL DEFAULT FALSE,
 fin TIMESTAMPTZ,
 actualizado TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS factura_escuela (
 stripe_invoice_id TEXT PRIMARY KEY,
 id_pago_clase INT NOT NULL UNIQUE REFERENCES pago_clase(id_pago_clase),
 id_inscripcion INT NOT NULL REFERENCES inscripcion_clase(id_inscripcion),
 url TEXT
);
CREATE TABLE IF NOT EXISTS asistencia_clase (
 id_inscripcion INT NOT NULL REFERENCES inscripcion_clase(id_inscripcion),
 fecha DATE NOT NULL,
 estado VARCHAR(20) NOT NULL CHECK(estado IN ('Presente','Ausente','Justificada')),
 registrado_por INT NOT NULL REFERENCES usuario(id_usuario),
 actualizado TIMESTAMPTZ NOT NULL DEFAULT now(),
 PRIMARY KEY(id_inscripcion,fecha)
);
COMMIT;
