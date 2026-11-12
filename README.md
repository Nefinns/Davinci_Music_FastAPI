# DaVinci Music

Aplicación web en desarrollo para una tienda de instrumentos y una escuela de música. Utiliza FastAPI, React con TypeScript y PostgreSQL en Neon. La identidad, las credenciales y las sesiones se gestionan con SuperTokens.

## Estado del proyecto

La rama `desarrollo_proyecto` contiene la aplicación principal. Las ramas de prácticas de Bases de Datos y el prototipo de categorías son trabajos separados; sus funciones no están integradas automáticamente en esta aplicación.

El código incluye:

- Registro con validación de datos, creación del perfil en PostgreSQL y alta de identidad en SuperTokens.
- Asignación inicial del rol `cliente` y creación del registro local correspondiente.
- Inicio de sesión por correo y contraseña y sesiones mediante cookies.
- Cierre de sesión mediante el SDK de SuperTokens.
- Recuperación y restablecimiento de contraseña, con pantallas React y envío por SMTP SSL.
- Consulta del perfil, roles y permisos del usuario autenticado.
- Administración de roles con búsqueda y paginación de usuarios, confirmación de cambios y revocación de sesiones de la cuenta afectada.
- Página pública y página de inicio protegida.
- Comprobación de disponibilidad de la API y de conexión a PostgreSQL.

La presencia de estas funciones en el código no sustituye las pruebas de integración contra los servicios configurados.

Pendientes: edición del perfil, catálogo e inventario, ventas, abastecimiento, módulos académicos, reportes y despliegue. Las secciones públicas de tienda y escuela son informativas. Las tablas previstas para esos módulos no representan flujos terminados.

## Stack

| Capa | Tecnologías |
|---|---|
| Backend | Python, FastAPI y Uvicorn |
| Persistencia | PostgreSQL en Neon, SQLModel, SQLAlchemy y psycopg2 |
| Identidad y sesiones | SuperTokens Core, `supertokens_python` y `supertokens-web-js` |
| Frontend | React, TypeScript, Vite y React Router |
| Interfaz | Tailwind CSS, componentes shadcn/ui configurados con Base UI y Lucide |
| Correo | SMTP SSL mediante `smtplib` |

Las dependencias están declaradas en `requirements.txt` y `frontend/package.json`; el frontend conserva su resolución en `frontend/package-lock.json`. Las versiones y auditorías deben verificarse en el entorno de instalación.

## Identidad y modelo de datos

PostgreSQL conserva los datos del negocio en las 16 tablas canónicas. `usuario.id_usuario` sigue siendo la clave primaria local y las relaciones existentes conservan sus claves foráneas.

`usuario.identidad_externa` es un `VARCHAR(128) UNIQUE` que enlaza el perfil con el ID de usuario de SuperTokens. No contiene un token de sesión ni una contraseña. El esquema actualizado no incluye `contrasena_hash`; el modelo y el servicio de registro tampoco deben incluirlo.

La columna de identidad permite `NULL` porque el registro primero realiza un `flush` del perfil local para validar restricciones y después crea la identidad externa. Antes del `commit`, asigna la identidad y crea el cliente. Las operaciones protegidas exigen un perfil vinculado y activo. Si falla el registro, el servicio revierte la transacción local e intenta eliminar la identidad externa creada; una falla de esa compensación requiere revisión.

Las contraseñas recibidas en los formularios se envían a la API para su validación y uso con SuperTokens. No se guardan como campos del perfil local. SuperTokens administra sus credenciales; la aplicación no calcula ni verifica hashes propios.

Los roles `cliente`, `maestro` y `administrador`, y sus permisos de acceso, se consultan en SuperTokens. Asignar un rol no crea por sí solo un registro de maestro o administrador en PostgreSQL; la gestión de esas entidades se completará con los módulos del negocio. El registro público siempre asigna `cliente`.

## Instalación local en Windows / PowerShell

### 1. Obtener la aplicación y preparar Python

```powershell
git clone --branch desarrollo_proyecto https://github.com/Nefinns/Davinci_Music_FastAPI.git
cd Davinci_Music_FastAPI
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Se utiliza directamente el intérprete del entorno virtual. Si ya tienes el proyecto, trabaja en tu copia de `desarrollo_proyecto` conservando tus cambios locales.

### 2. Preparar PostgreSQL y SuperTokens

Para una base vacía, ejecuta `DaVinciMusic_schema_canonico.sql` desde pgAdmin o el editor SQL de Neon. El archivo crea las 16 tablas dentro de una transacción. La API no crea las tablas al arrancar.

Para una base existente, no ejecutes de nuevo ese script: es un esquema inicial, no una migración. Si la identidad externa ya está incorporada y solo queda la columna del hash antiguo, primero aplica la limpieza del modelo y del servicio. La eliminación física de la columna es un paso separado; no requiere borrar usuarios ni recrear tablas.

Configura una instancia de SuperTokens Core accesible para el backend. Usa su URI y, para Core remoto, su API key. PostgreSQL del negocio y el almacenamiento administrado por Core tienen responsabilidades distintas.

### 3. Variables del backend

Crea `.env` en la raíz del repositorio, al mismo nivel que `backend` y `frontend`:

```dotenv
DATABASE_URL=postgresql://USUARIO:CONTRASENA@HOST/BASE_DE_DATOS?sslmode=require
SUPERTOKENS_CONNECTION_URI=https://TU_INSTANCIA_DE_SUPERTOKENS
SUPERTOKENS_API_KEY=REEMPLAZAR_POR_LA_CLAVE_DE_CORE
API_DOMAIN=http://localhost:8000
FRONTEND_URL=http://localhost:5173

SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=usuario_smtp
SMTP_PASSWORD=credencial_smtp
SMTP_FROM=cuenta@example.com
```

Los valores son ejemplos. `DATABASE_URL` y `SUPERTOKENS_CONNECTION_URI` son obligatorios. Para Core remoto, la API key también es obligatoria. La configuración exige HTTPS para dominios que no sean locales. El tenant utilizado por la aplicación es `public`.

El correo requiere un servidor compatible con SMTP SSL. Si el envío falla, la API mantiene una respuesta genérica para no revelar si una cuenta existe; comprueba la entrega real durante las pruebas.

`SECRET_KEY` y `ACCESS_TOKEN_MINUTES` de la implementación antigua ya no son utilizados por la configuración actual. La política de duración de sesiones debe verificarse en SuperTokens; el frontend no implementa actualmente el aviso previo de cinco minutos.

No publiques `.env` ni pongas secretos en variables `VITE_*`.

### 4. Iniciar el backend

Desde la raíz:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Accede a `http://localhost:8000`, `http://localhost:8000/docs` y `http://localhost:8000/db-test`. El inicio de la aplicación prepara los roles en Core, por lo que SuperTokens debe estar disponible.

### 5. Iniciar el frontend

En otra terminal, desde la raíz:

```powershell
cd frontend
npm ci
npm run dev
```

El frontend utiliza `http://localhost:8000` de forma predeterminada. Puedes declararlo en `frontend/.env.local`:

```dotenv
VITE_API_URL=http://localhost:8000
```

Abre `http://localhost:5173`. Mantén coherentes `API_DOMAIN`, `VITE_API_URL` y la dirección del navegador. El backend permite en CORS el origen exacto de `FRONTEND_URL`, con credenciales; cambia esa variable si usas otro origen o puerto. Evita mezclar `localhost` y `127.0.0.1` entre la configuración y el navegador.

## API y sesiones

| Método | Ruta | Función |
|---|---|---|
| GET | `/` | Estado básico de la API |
| GET | `/db-test` | Comprobación de PostgreSQL |
| POST | `/auth/registro` | Crear identidad, perfil y cliente |
| POST | `/auth/login` | Crear sesión mediante cookies |
| POST | `/auth/logout` | Revocar la sesión actual desde el adaptador de la aplicación |
| POST | `/auth/recuperar-contrasena` | Solicitar enlace por correo |
| POST | `/auth/restablecer-contrasena` | Consumir token, revocar sesiones y cambiar contraseña |
| GET | `/usuarios/me` | Consultar perfil |
| GET | `/usuarios/me/roles` | Consultar roles actuales |
| GET | `/usuarios/me/permisos` | Consultar permisos actuales |
| GET | `/usuarios` | Buscar y paginar usuarios; requiere administración |
| PUT | `/usuarios/{id_usuario}/roles/{rol}` | Asignar rol; requiere administración |
| DELETE | `/usuarios/{id_usuario}/roles/{rol}` | Retirar rol; requiere administración |

El frontend inicializa `supertokens-web-js`, envía peticiones con `credentials: "include"` y usa `Session.signOut()` para cerrar sesión mediante el endpoint gestionado por el SDK. Este flujo es distinto del adaptador `/auth/logout`, que también existe en la API.

Las rutas personalizadas de `/auth` exigen `rid: session` y validan el origen cuando está presente. Las operaciones privadas verifican la sesión con Core y el perfil local activo. No se utiliza el antiguo contrato de devolver un JWT para guardarlo en `sessionStorage`; el frontend elimina esa clave antigua al iniciar.

Los cambios de roles revocan las sesiones de la cuenta afectada. Un administrador no puede retirarse a sí mismo su rol administrativo desde esta API. La cuenta inicial con privilegios debe aprovisionarse de forma controlada en Core y estar vinculada a un perfil local activo; el repositorio no incluye un comando de bootstrap.

## Organización

```text
backend/
  main.py
  app/
    api/routes/     # Autenticación y usuarios
    core/           # Configuración, SuperTokens, identidad y permisos
    db/             # Motor y sesiones SQLModel
    models/         # Persistencia
    schemas/        # Entrada y salida de la API
    services/       # Registro, autenticación y correo
frontend/
  src/
    components/
    contexts/
    pages/
    services/
    lib/
DaVinciMusic_schema_canonico.sql
requirements.txt
```

## Verificación

```powershell
# Desde la raíz
.\.venv\Scripts\python.exe -m pip check

# Desde frontend
npm run build
npm run lint
```

Pruebas de integración pendientes de repetir en el entorno configurado: registro y persistencia de identidad/cliente, login, consulta del perfil, logout y rechazo posterior de la sesión, recuperación por correo, rechazo de reutilización del enlace, control de roles y denegación a cuentas inactivas o sin vínculo.

La revisión que acompaña la retirada del hash comprueba referencias en el código y sintaxis Python; no certifica entrega SMTP, disponibilidad de Core, ejecución PostgreSQL ni una compilación nueva del frontend. El repositorio revisado no contiene una suite automatizada de pruebas. Las auditorías históricas de dependencias no representan una evaluación de seguridad actual.

## Próximo desarrollo

Completar RF-05 (edición de perfil) y después RF-08–19 (categorías e instrumentos). Mantener permisos comprobados en el backend, integridad de datos y mensajes claros. Antes de ventas y escuela, completar las entidades locales de administrador y maestro y sus reglas de negocio.
