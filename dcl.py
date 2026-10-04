# Solo define los usuarios válidos; el CREATE ROLE real se arma en main.py con la contraseña de la interfaz
dcl_usuarios = {
    "director": "CREATE ROLE director LOGIN;",

    "vendedor_tienda": "CREATE ROLE vendedor_tienda LOGIN;",

    "ventas_mostrador": "CREATE ROLE ventas_mostrador LOGIN;",

    "recepcion": "CREATE ROLE recepcion LOGIN;",

    "control_escolar": "CREATE ROLE control_escolar LOGIN;",

    "consulta_catalogo": "CREATE ROLE consulta_catalogo LOGIN;",

    "captura_catalogo": "CREATE ROLE captura_catalogo LOGIN;",

    "almacen": "CREATE ROLE almacen LOGIN;",

    "contabilidad": "CREATE ROLE contabilidad LOGIN;",

    "compras": "CREATE ROLE compras LOGIN;",

    "administrador": "CREATE ROLE administrador LOGIN;",

    "supervisor_inventario": "CREATE ROLE supervisor_inventario LOGIN;",

    "gestion_proveedores": "CREATE ROLE gestion_proveedores LOGIN;",

    "inventario": "CREATE ROLE inventario LOGIN;",

    "auditor": "CREATE ROLE auditor LOGIN;"
}

# Diccionario para las consultas de asignación de permisos
dcl_grant = {
    "director": "GRANT SELECT ON TABLE public.cliente TO director;",

    "vendedor_tienda": "GRANT SELECT ON TABLE public.instrumento TO vendedor_tienda;",

    "ventas_mostrador": "GRANT INSERT ON TABLE public.cliente TO ventas_mostrador;",

    "recepcion": "GRANT SELECT ON TABLE public.usuario TO recepcion;",

    "control_escolar": "GRANT UPDATE ON TABLE public.usuario TO control_escolar;",

    "consulta_catalogo": "GRANT SELECT ON TABLE public.categoria_instrumento TO consulta_catalogo;",

    "captura_catalogo": "GRANT INSERT ON TABLE public.categoria_instrumento TO captura_catalogo;",

    "almacen": "GRANT SELECT ON TABLE public.proveedor TO almacen;",

    "contabilidad": "GRANT SELECT ON TABLE public.cliente TO contabilidad;",

    "compras": "GRANT INSERT ON TABLE public.proveedor TO compras;",

    "administrador": "GRANT UPDATE ON TABLE public.cliente TO administrador;",

    "supervisor_inventario": "GRANT UPDATE ON TABLE public.instrumento TO supervisor_inventario;",

    "gestion_proveedores": "GRANT UPDATE ON TABLE public.proveedor TO gestion_proveedores;",

    "inventario": "GRANT DELETE ON TABLE public.categoria_instrumento TO inventario;",

    "auditor": "GRANT SELECT ON TABLE public.usuario TO auditor;"
}

# Diccionario para revocar permisos
dcl_revoke = {
    "director": "REVOKE SELECT ON TABLE public.cliente FROM director;",

    "vendedor_tienda": "REVOKE SELECT ON TABLE public.instrumento FROM vendedor_tienda;",

    "ventas_mostrador": "REVOKE INSERT ON TABLE public.cliente FROM ventas_mostrador;",

    "recepcion": "REVOKE SELECT ON TABLE public.usuario FROM recepcion;",

    "control_escolar": "REVOKE UPDATE ON TABLE public.usuario FROM control_escolar;",

    "consulta_catalogo": "REVOKE SELECT ON TABLE public.categoria_instrumento FROM consulta_catalogo;",

    "captura_catalogo": "REVOKE INSERT ON TABLE public.categoria_instrumento FROM captura_catalogo;",

    "almacen": "REVOKE SELECT ON TABLE public.proveedor FROM almacen;",

    "contabilidad": "REVOKE SELECT ON TABLE public.cliente FROM contabilidad;",

    "compras": "REVOKE INSERT ON TABLE public.proveedor FROM compras;",

    "administrador": "REVOKE UPDATE ON TABLE public.cliente FROM administrador;",

    "supervisor_inventario": "REVOKE UPDATE ON TABLE public.instrumento FROM supervisor_inventario;",

    "gestion_proveedores": "REVOKE UPDATE ON TABLE public.proveedor FROM gestion_proveedores;",

    "inventario": "REVOKE DELETE ON TABLE public.categoria_instrumento FROM inventario;",

    "auditor": "REVOKE SELECT ON TABLE public.usuario FROM auditor;"
}

# Diccionario para eliminar roles/usuarios
dcl_drop_user = {
    "director": "DROP ROLE director;",

    "vendedor_tienda": "DROP ROLE vendedor_tienda;",

    "ventas_mostrador": "DROP ROLE ventas_mostrador;",

    "recepcion": "DROP ROLE recepcion;",

    "control_escolar": "DROP ROLE control_escolar;",

    "consulta_catalogo": "DROP ROLE consulta_catalogo;",

    "captura_catalogo": "DROP ROLE captura_catalogo;",

    "almacen": "DROP ROLE almacen;",

    "contabilidad": "DROP ROLE contabilidad;",

    "compras": "DROP ROLE compras;",

    "administrador": "DROP ROLE administrador;",

    "supervisor_inventario": "DROP ROLE supervisor_inventario;",

    "gestion_proveedores": "DROP ROLE gestion_proveedores;",

    "inventario": "DROP ROLE inventario;",

    "auditor": "DROP ROLE auditor;"
}