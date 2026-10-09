# DaVinci Music - Sistema de Gestión Integral

Bienvenido al repositorio del backend de DaVinci Music, una plataforma centralizada diseñada para administrar eficientemente las operaciones de una academia de música y tienda de instrumentos. 

Este proyecto proporciona una API RESTful robusta, segura y escalable para gestionar el inventario comercial, el control académico y los accesos del personal.

## Arquitectura y Tecnologías

El sistema está diseñado bajo una arquitectura cliente-servidor, separando claramente la lógica de negocio de la interfaz de usuario:

* **Backend y API:** Python 3, FastAPI, Uvicorn
* **Base de Datos:** PostgreSQL (Alojado en Neon Cloud)
* **ORM:** SQLAlchemy / SQLModel
* **Frontend Principal:** React (El cliente web principal de producción se gestiona de forma independiente)
* **Herramientas de Pruebas:** Tkinter (Scripts de escritorio utilizados exclusivamente para validaciones internas y entornos experimentales de prueba)
* **Seguridad:** Gestión de credenciales mediante `python-dotenv` y parametrización de consultas.

## Módulos Principales del Sistema

El backend centraliza las siguientes operaciones de negocio:

1. **Gestión Académica:** 
   * Control y registro de perfiles para alumnos (`CLIENTE`) y plantilla docente (`MAESTRO`).
   * Estructuración de la información necesaria para impartir clases y llevar seguimiento.
2. **Control de Inventario y Tienda:** 
   * Administración del catálogo de instrumentos y productos de la tienda física.
3. **Administración de Usuarios y Accesos:** 
   * Sistema de autenticación y autorización basado en roles (Administradores, Empleados, Usuarios regulares) para garantizar el principio de mínimo privilegio.
4. **Operaciones Generales:** 
   * Endpoints dedicados a mantener la sincronización entre las ventas de la tienda y la administración de la escuela.

## Configuración del Entorno de Desarrollo Local

Para ejecutar la API en un entorno local, siga los pasos descritos a continuación:

**1. Clonar el repositorio:**
```bash
git clone <url-de-tu-repositorio>
cd <nombre-de-la-carpeta>
