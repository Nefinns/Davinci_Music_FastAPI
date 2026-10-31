-- DaVinci Music - esquema canónico PostgreSQL
-- Basado en el modelo relacional y el diccionario de datos corregidos.
-- Nombres oficiales: detalle_orden e id_proveedor.
-- Este archivo crea las 16 tablas; ejecútese en una base de datos vacía.
-- La versión Next.js debe mapear sus nombres físicos antiguos si se conserva su esquema previo.

BEGIN;

CREATE TABLE usuario (
    id_usuario         SERIAL PRIMARY KEY,
    nombre_usuario     VARCHAR(100) NOT NULL UNIQUE,
    nombre             VARCHAR(100) NOT NULL,
    apellido_paterno   VARCHAR(100) NOT NULL,
    apellido_materno   VARCHAR(100),              -- opcional
    fecha_nacimiento   DATE NOT NULL,
    curp               VARCHAR(18) NOT NULL UNIQUE,
    ine                VARCHAR(20) UNIQUE,         -- opcional
    correo             VARCHAR(150) NOT NULL UNIQUE,
    telefono           VARCHAR(20),                -- opcional
    direccion          VARCHAR(255),               -- opcional
    contrasena_hash    VARCHAR(255) NOT NULL,
    activo             BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro     TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE cliente (
    id_cliente  SERIAL PRIMARY KEY,
    id_usuario  INT NOT NULL UNIQUE REFERENCES usuario(id_usuario),
    fecha_alta  DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE administrador (
    id_administrador    SERIAL PRIMARY KEY,
    id_usuario          INT NOT NULL UNIQUE REFERENCES usuario(id_usuario),
    fecha_contratacion  DATE NOT NULL
);

CREATE TABLE maestro (
    id_maestro          SERIAL PRIMARY KEY,
    id_usuario          INT NOT NULL UNIQUE REFERENCES usuario(id_usuario),
    especialidad        VARCHAR(100) NOT NULL,
    fecha_contratacion  DATE NOT NULL,
    activo              BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE periodo_academico (
    id_periodo      SERIAL PRIMARY KEY,
    nombre_periodo  VARCHAR(100) NOT NULL UNIQUE,
    fecha_inicio    DATE NOT NULL,
    fecha_fin       DATE NOT NULL,
    estado          VARCHAR(30) NOT NULL
);

CREATE TABLE categoria_instrumento (
    id_categoria      SERIAL PRIMARY KEY,
    nombre_categoria  VARCHAR(100) NOT NULL UNIQUE,
    descripcion       VARCHAR(255)               -- opcional
);

CREATE TABLE instrumento (
    id_instrumento      SERIAL PRIMARY KEY,
    id_categoria        INT NOT NULL REFERENCES categoria_instrumento(id_categoria),
    nombre_instrumento  VARCHAR(100) NOT NULL,
    marca               VARCHAR(100),            -- opcional
    modelo              VARCHAR(100),            -- opcional
    tamano              VARCHAR(50),             -- opcional
    color               VARCHAR(50),             -- opcional
    precio_venta        DECIMAL(10,2) NOT NULL,
    stock_actual        INT NOT NULL DEFAULT 0,
    activo              BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE clase (
    id_clase        SERIAL PRIMARY KEY,
    id_maestro      INT NOT NULL REFERENCES maestro(id_maestro),
    id_instrumento  INT NOT NULL REFERENCES instrumento(id_instrumento),
    id_periodo      INT NOT NULL REFERENCES periodo_academico(id_periodo),
    nombre_clase    VARCHAR(100) NOT NULL,
    nivel           VARCHAR(30) NOT NULL,
    costo_mensual   DECIMAL(10,2) NOT NULL,
    cupo_maximo     INT NOT NULL,
    activa          BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE horario_clase (
    id_horario   SERIAL PRIMARY KEY,
    id_clase     INT NOT NULL REFERENCES clase(id_clase),
    dia_semana   VARCHAR(20) NOT NULL,
    hora_inicio  TIME NOT NULL,
    hora_fin     TIME NOT NULL,
    salon        VARCHAR(50)                      -- opcional
);

CREATE TABLE inscripcion_clase (
    id_inscripcion           SERIAL PRIMARY KEY,
    id_cliente               INT NOT NULL REFERENCES cliente(id_cliente),
    id_clase                 INT NOT NULL REFERENCES clase(id_clase),
    fecha_inscripcion        DATE NOT NULL DEFAULT CURRENT_DATE,
    costo_mensual_acordado   DECIMAL(10,2) NOT NULL,
    estado_inscripcion       VARCHAR(30) NOT NULL DEFAULT 'Activa'
);

CREATE TABLE pago_clase (
    id_pago_clase       SERIAL PRIMARY KEY,
    id_inscripcion      INT NOT NULL REFERENCES inscripcion_clase(id_inscripcion),
    periodo_pagado      DATE NOT NULL,
    importe             DECIMAL(10,2) NOT NULL,
    fecha_vencimiento   DATE NOT NULL,
    fecha_pago          TIMESTAMP,                 -- opcional: nulo mientras esté pendiente
    metodo_pago         VARCHAR(30),               -- opcional: se llena al pagar
    estado_pago         VARCHAR(30) NOT NULL DEFAULT 'Pendiente'
);

CREATE TABLE venta (
    id_venta          SERIAL PRIMARY KEY,
    id_cliente        INT NOT NULL REFERENCES cliente(id_cliente),
    id_administrador  INT NOT NULL REFERENCES administrador(id_administrador),
    fecha_venta       TIMESTAMP NOT NULL DEFAULT NOW(),
    metodo_pago       VARCHAR(30) NOT NULL,
    estado_venta      VARCHAR(30) NOT NULL DEFAULT 'Completada'
);

CREATE TABLE detalle_venta (
    id_venta         INT NOT NULL REFERENCES venta(id_venta),
    id_instrumento   INT NOT NULL REFERENCES instrumento(id_instrumento),
    cantidad         INT NOT NULL,
    precio_unitario  DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_venta, id_instrumento)
);

CREATE TABLE proveedor (
    id_proveedor       SERIAL PRIMARY KEY,
    nombre_proveedor   VARCHAR(150) NOT NULL,
    rfc                VARCHAR(13) NOT NULL UNIQUE,
    correo             VARCHAR(150),               -- opcional
    direccion          VARCHAR(255),               -- opcional
    telefono           VARCHAR(20),                -- opcional
    activo             BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE orden_abastecimiento (
    id_orden          SERIAL PRIMARY KEY,
    id_proveedor      INT NOT NULL REFERENCES proveedor(id_proveedor),
    id_administrador  INT NOT NULL REFERENCES administrador(id_administrador),
    fecha_orden       TIMESTAMP NOT NULL DEFAULT NOW(),
    estado_orden      VARCHAR(30) NOT NULL DEFAULT 'Pendiente'
);

CREATE TABLE detalle_orden (
    id_orden             INT NOT NULL REFERENCES orden_abastecimiento(id_orden),
    id_instrumento       INT NOT NULL REFERENCES instrumento(id_instrumento),
    cantidad_solicitada  INT NOT NULL,
    cantidad_recibida    INT NOT NULL DEFAULT 0,   -- 0 hasta que llegue mercancía
    costo_unitario       DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_orden, id_instrumento)
);

COMMIT;
