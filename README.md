# DaVinci Music

Aplicación web en desarrollo para gestionar una academia de música y una tienda de instrumentos.

El proyecto integra un backend con FastAPI, un frontend con React y TypeScript, y una base de datos PostgreSQL alojada en Neon. El avance actual se concentra en el registro de usuarios, la autenticación y la gestión de sesiones, como base para incorporar los módulos académicos y comerciales.

## Estado del proyecto

**En desarrollo activo. Sin despliegue público.**

La rama `desarrollo_proyecto` contiene el avance de la aplicación principal. Las otras ramas incluyen ejercicios y prototipos de la materia de Bases de Datos; no representan funcionalidades integradas en el producto.

### Funcionalidades implementadas

- Registro de usuarios con validación de campos únicos.
- Inicio de sesión mediante correo y contraseña.
- Almacenamiento de contraseñas mediante hash Argon2.
- Autenticación de la API mediante tokens JWT con expiración.
- Consulta del perfil y los roles del usuario autenticado.
- Dependencias de autorización por roles, como base para futuros módulos.
- Página pública, formularios de registro e inicio de sesión y una página protegida.
- Gestión de sesión en el frontend y cierre de sesión.
- Endpoints de recuperación y restablecimiento de contraseña, con envío de correo mediante SMTP.
- Endpoint de comprobación de conexión a la base de datos.

La recuperación de contraseña está implementada en el backend. Su integración visual está pendiente: el enlace enviado por correo apunta a una ruta que todavía no está disponible en el frontend.

### Funcionalidades previstas

- Gestión académica de alumnos, docentes y clases.
- Catálogo e inventario de instrumentos y productos.
- Gestión de ventas y operaciones comerciales.
- Interfaces administrativas con permisos por rol.
- Integración completa del flujo de recuperación de contraseña.
- Ampliación de pruebas automatizadas y preparación para despliegue.

El esquema SQL contempla entidades de estos módulos. Su presencia en la base de datos no implica que sus interfaces o flujos de negocio estén implementados.

## Tecnologías

| Capa | Tecnologías |
|---|---|
| Backend | Python, FastAPI y Uvicorn |
| Persistencia | PostgreSQL, Neon, SQLModel y SQLAlchemy |
| Autenticación | PyJWT y pwdlib con Argon2 |
| Frontend | React, TypeScript, Vite y React Router |
| Estilos e interfaz | Tailwind CSS, Base UI y Lucide |
| Configuración | Variables de entorno y python-dotenv |

## Organización del código

```text
backend/
├── main.py
└── app/
    ├── api/routes/     # Endpoints de autenticación y usuarios
    ├── core/           # Configuración, seguridad y permisos
    ├── db/             # Conexión y sesiones de base de datos
    ├── models/         # Modelos de persistencia
    ├── schemas/        # Datos de entrada y salida
    └── services/       # Lógica de usuarios y envío de correo

frontend/
├── src/
│   ├── components/    # Componentes de interfaz
│   ├── contexts/      # Estado de sesión
│   ├── pages/         # Páginas de la aplicación
│   ├── services/      # Comunicación con la API
│   └── lib/           # Utilidades
└── package-lock.json

DaVinciMusic_schema_canonico.sql
requirements.txt
```

El backend separa las rutas HTTP, la lógica de negocio y el acceso a datos. El frontend consume la API y gestiona la navegación y el estado de sesión.

## Entorno probado

Validación local realizada el **25 de octubre de 2026**:

| Herramienta | Versión |
|---|---|
| Python | 3.13.17 |
| pip | 26.2.2 |
| Node.js | 22.23.4 |
| npm | 10.9.9 |

Las dependencias Python se declaran en `requirements.txt`. Las versiones resueltas del frontend se conservan en `frontend/package-lock.json`.

## Instalación local

Los siguientes comandos están preparados para Windows y PowerShell.

### 1. Clonar la rama de desarrollo

```powershell
git clone --branch desarrollo_proyecto https://github.com/Nefinns/Davinci_Music_FastAPI.git
cd Davinci_Music_FastAPI
```

### 2. Preparar Python

Comprueba que `python` corresponde a la versión que deseas utilizar:

```powershell
python --version
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Los comandos utilizan directamente el intérprete del entorno virtual, por lo que no es necesario activarlo.

### 3. Preparar PostgreSQL

Crea una base de datos de desarrollo en PostgreSQL o Neon.

Ejecuta `DaVinciMusic_schema_canonico.sql` sobre una base vacía, utilizando un cliente PostgreSQL o el editor SQL de Neon. El archivo crea el esquema inicial; no es un sistema de migraciones y no debe ejecutarse sobre una base existente sin revisar su contenido.

La API no crea automáticamente las tablas al arrancar.

### 4. Configurar el backend

Crea un archivo `.env` en la raíz del proyecto:

```dotenv
DATABASE_URL=postgresql://USUARIO:CONTRASENA@HOST/BASE_DE_DATOS?sslmode=require
SECRET_KEY=REEMPLAZAR_POR_UNA_CLAVE_ALEATORIA
ACCESS_TOKEN_MINUTES=30
```

Utiliza la cadena de conexión correspondiente a tu base de datos. Puedes generar una clave para `SECRET_KEY` con:

```powershell
.\venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Para habilitar el envío de correos de recuperación, añade:

```dotenv
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=usuario_smtp
SMTP_PASSWORD=credencial_smtp
SMTP_FROM=cuenta@example.com
FRONTEND_URL=http://localhost:5173
```

La implementación utiliza SMTP sobre SSL. Configura un proveedor y un puerto compatibles. El envío requiere credenciales válidas; la interfaz de restablecimiento sigue pendiente.

No publiques el archivo `.env` ni utilices credenciales o datos personales reales en demostraciones públicas.

### 5. Iniciar la API

Desde la raíz del proyecto:

```powershell
cd backend
..\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Direcciones locales:

- API: http://127.0.0.1:8000
- Documentación interactiva: http://127.0.0.1:8000/docs
- Comprobación de conexión: http://127.0.0.1:8000/db-test

### 6. Iniciar el frontend

En otra terminal, desde la raíz del proyecto:

```powershell
cd frontend
npm ci
npm run dev
```

Abre la dirección que indique Vite, normalmente http://localhost:5173.

El frontend utiliza `http://127.0.0.1:8000` como dirección predeterminada de la API. Para cambiarla, crea `frontend/.env.local`:

```dotenv
VITE_API_URL=http://127.0.0.1:8000
```

Las variables `VITE_*` son públicas para el navegador: no deben contener secretos.

La configuración CORS del backend permite los orígenes locales `http://localhost:5173` y `http://127.0.0.1:5173`. Si cambias el puerto del frontend, ajusta también esa configuración.

## Endpoints principales

| Método | Ruta | Función |
|---|---|---|
| GET | `/` | Comprobar que la API responde |
| GET | `/db-test` | Comprobar la conexión a PostgreSQL |
| POST | `/auth/registro` | Registrar un usuario |
| POST | `/auth/login` | Obtener un token de acceso |
| GET | `/usuarios/me` | Consultar el perfil autenticado |
| GET | `/usuarios/me/roles` | Consultar los roles del usuario |
| POST | `/auth/recuperar-contrasena` | Solicitar un correo de recuperación |
| POST | `/auth/restablecer-contrasena` | Cambiar la contraseña con un token válido |

Los endpoints de perfil y roles requieren la cabecera:

```text
Authorization: Bearer <token>
```

Los formatos de solicitud y respuesta están disponibles en `/docs`.

## Validación y mantenimiento

Comprobaciones realizadas durante la actualización del entorno:

- Instalación del frontend mediante `npm ci`.
- Compilación de TypeScript y Vite mediante `npm run build`.
- Comprobación de compatibilidad Python mediante `pip check`.
- Auditorías de dependencias con `npm audit` y `pip-audit`, sin vulnerabilidades conocidas reportadas en las versiones analizadas.
- Prueba manual de funcionamiento local después de actualizar Node.js y Python.

Estos resultados corresponden a la fecha de revisión y no constituyen una garantía de ausencia de vulnerabilidades.

Para repetir las comprobaciones básicas:

```powershell
# Desde la raíz
.\venv\Scripts\python.exe -m pip check

# Desde frontend
npm run build
npm run lint
npm audit
```

### Pendientes técnicos conocidos

- Corregir cinco errores de lint relacionados con exportaciones para Fast Refresh y actualizaciones de estado dentro de efectos.
- Completar la interfaz de recuperación de contraseña.
- Ampliar las pruebas automatizadas de autenticación, autorización y flujos de negocio.
- Automatizar las comprobaciones de calidad y dependencias.
- Revisar la configuración y los controles de seguridad antes de un despliegue público.

## Ramas académicas

Además de la aplicación principal, el repositorio conserva ejercicios de Bases de Datos:

| Rama | Propósito |
|---|---|
| `desarrollo_proyecto` | Aplicación principal |
| `main` | Versión inicial del ejercicio CRUD |
| `prueba-crud-categoria-instrumento` | Prototipo CRUD de categorías de instrumentos |
| `actividades_3.3_3.4` | Ejercicios DDL/DCL con interfaz de escritorio |
| `bd_experimental_unidad4` | Panel experimental de administración de bases de datos |

Los ejercicios administrativos deben utilizarse únicamente con bases de prácticas y dentro del alcance documentado en cada rama. No forman parte del backend de la aplicación principal.