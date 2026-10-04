# Consultas CREATE
crear_usuario = """CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(100) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    fecha_nacimiento DATE NOT NULL,
    curp VARCHAR(18) NOT NULL UNIQUE,
    ine VARCHAR(20) UNIQUE,
    correo VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    contrasena_hash VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro TIMESTAMP NOT NULL DEFAULT NOW()
);"""

crear_cliente = """CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE REFERENCES usuario(id_usuario),
    fecha_alta DATE NOT NULL DEFAULT CURRENT_DATE
);"""

crear_categoria_instrumento = """CREATE TABLE categoria_instrumento (
    id_categoria SERIAL PRIMARY KEY,
    nombre_categoria VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
);"""

crear_instrumento = """CREATE TABLE instrumento (
    id_instrumento SERIAL PRIMARY KEY,
    id_categoria INT NOT NULL REFERENCES categoria_instrumento(id_categoria),
    nombre_instrumento VARCHAR(100) NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    tamano VARCHAR(50),
    color VARCHAR(50),
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);"""

crear_proveedor = """CREATE TABLE proveedor (
    id_proveedor SERIAL PRIMARY KEY,
    nombre_proveedor VARCHAR(150) NOT NULL,
    rfc VARCHAR(13) NOT NULL UNIQUE,
    correo VARCHAR(150),
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);"""

# Consultas ALTER
alterar_usuario = """ALTER TABLE usuario
ADD COLUMN ultimo_acceso TIMESTAMP;"""

alterar_cliente = """ALTER TABLE cliente
ADD COLUMN observaciones VARCHAR(255);"""

alterar_categoria_instrumento = """ALTER TABLE categoria_instrumento
ADD COLUMN activa BOOLEAN NOT NULL DEFAULT TRUE;"""

alterar_instrumento = """ALTER TABLE instrumento
ADD COLUMN stock_minimo INT NOT NULL DEFAULT 0;"""

alterar_proveedor = """ALTER TABLE proveedor
ADD COLUMN contacto VARCHAR(80);"""

# Consultas DROP
borrar_cliente = """DROP TABLE cliente;"""

borrar_instrumento = """DROP TABLE instrumento;"""

borrar_usuario = """DROP TABLE usuario;"""

borrar_categoria_instrumento = """DROP TABLE categoria_instrumento;"""

borrar_proveedor = """DROP TABLE proveedor;"""

ddl_create = {
    "usuario": crear_usuario,
    "cliente": crear_cliente,
    "categoria_instrumento": crear_categoria_instrumento,
    "instrumento": crear_instrumento,
    "proveedor": crear_proveedor
}

ddl_alter = {
    "usuario": alterar_usuario,
    "cliente": alterar_cliente,
    "categoria_instrumento": alterar_categoria_instrumento,
    "instrumento": alterar_instrumento,
    "proveedor": alterar_proveedor
}

ddl_drop = {
    "cliente": borrar_cliente,
    "instrumento": borrar_instrumento,
    "usuario": borrar_usuario,
    "categoria_instrumento": borrar_categoria_instrumento,
    "proveedor": borrar_proveedor
}
