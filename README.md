# DaVinciMusic — Unidad 6 · Aplicación NoSQL con frameworks

Miniaplicación **independiente** para consultar la base `davincimusic_nosql_dev` **ya migrada** a MongoDB Atlas. No modifica el backend principal de DaVinciMusic ni necesita Neon, SuperTokens, login o un proceso de migración.

## Stack conservado

- **Backend:** Python 3.13, FastAPI, Pydantic (vía FastAPI), PyMongo Async.
- **Frontend:** React 19, Vite 8, TypeScript 6, Tailwind CSS 4, componentes shadcn/ui estilo `base-nova` y Lucide React.
- **Base:** MongoDB Atlas, usando exactamente `davincimusic_nosql_dev`.
- Diseño basado en el ZIP y capturas de la Unidad 5: verde oscuro `#0A3D3A`, marfil `#F3F5F2`, dorado `#C8A04A`, encabezados Cormorant Garamond y textos Source Sans 3.

## Preparar Windows (PowerShell)

Se recomienda **Node.js 22.12+** y **Python 3.13**. Usa dos terminales.

**1. Extrae el ZIP en tu disco D:**, por ejemplo `D:\Proyectos\DaVinciMusic_NoSQL_Unidad6`. No necesitas copiar el ZIP original del frontend ni su `node_modules`.

**2. Configura el backend** (terminal 1):

```powershell
cd D:\Proyectos\DaVinciMusic_NoSQL_Unidad6\backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

En `.env`, sustituye `MONGODB_URI` por la URI de Atlas **con las credenciales de un usuario de base de datos**, nunca las de tu cuenta de Atlas. Si tu contraseña incluye `@`, `:`, `/`, `%` o `#`, codifica esos caracteres para la URI (o genera una contraseña alfanumérica exclusiva de desarrollo). En Atlas, autoriza la IP actual en **Network Access** y verifica el permiso `readWrite` sobre `davincimusic_nosql_dev` si vas a insertar datos o crear vistas.

```dotenv
MONGODB_URI=mongodb+srv://USUARIO:CONTRASENA@TU_CLUSTER.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=davincimusic_nosql_dev
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DEMO_WRITE_ENABLED=true
```

- El valor `DEMO_WRITE_ENABLED=true` autoriza **solo la inserción ficticia idempotente y preparación de tres vistas**. Para conservar un entorno de solo lectura, vuelve a `false` y reinicia el backend.
- La cadena se guarda **únicamente en backend/.env**. **Nunca la coloques en `frontend/.env` ni en código React**.

Arranca el backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Visita `http://127.0.0.1:8000/api/health` o `http://127.0.0.1:8000/docs`. Si el servidor falla al arrancar, comprueba credenciales, SSL e IP autorizada en Atlas. El comando no activa el MongoDB Community Server de Windows.

**3. Instala y abre el frontend** (terminal 2):

```powershell
cd D:\Proyectos\DaVinciMusic_NoSQL_Unidad6\frontend
node --version
npm.cmd ci
npm.cmd run build
npm.cmd run dev
```

Abre `http://127.0.0.1:5173/`. Vite usa `127.0.0.1` para servir y conectar al backend. Si trabajas con `localhost`, ambos están permitidos en el CORS. Si cambias la URL de la API, copia `frontend/.env.example` a `frontend/.env` y modifica **solo** `VITE_API_URL` (nunca pongas secretos ahí).

El archivo `package-lock.json` se entrega para usar **`npm ci`**, que reproduce las versiones bloqueadas. **No ejecutes `npm install` automáticamente antes de `npm ci`**, ni `npm audit fix --force`. Para revisar posibles nuevas vulnerabilidades:

```powershell
npm.cmd audit
npm.cmd audit --omit=dev
```

La versión no incluye ESLint, SuperTokens, Router, librerías de gráficos, ORM SQL ni otras dependencias innecesarias. Es **más pequeña** que el frontend original. Vite/Rolldown instala automáticamente el binario nativo apropiado para Windows mediante `npm ci`.

## Uso de la aplicación

1. **Preparar datos demo:** carga 18 documentos ficticios en 9 colecciones, compatibles con los IDs y documentos embebidos del trabajo de mongosh. Inserta solo los que falten (operación `upsert` con `$setOnInsert`). Los documentos migrados no se reemplazan.
2. **Crear / actualizar vistas:** configura tres vistas `vista_u6_ventas_clientes`, `vista_u6_catalogo`, `vista_u6_clases`. Si una colección física ya tiene alguno de esos nombres, el backend detendrá la operación, no la eliminará.
3. Explora **Consultas simples**, **JOIN**, **Agregadas** y **Vistas**. Cada ejercicio muestra su código **mongosh equivalente**, el botón Ejecutar y la tabla de resultados con documentos embebidos desplegables.
4. Pulsa **Copiar código** para ejecutar ese mismo ejemplo en mongosh desde Compass o PowerShell. Las consultas del navegador **no ejecutan JavaScript arbitrario**: llaman a un catálogo fijo de operaciones PyMongo en FastAPI.

**Catálogo:** 8 consultas simples, 5 JOIN mediante `$lookup`, 5 agregaciones y 3 vistas = **21 ejercicios**.

### Ejemplo de salida esperada

El total de las dos ventas de ejemplo es **15,400.00 MXN** (9000 + 6400). Los importes se guardan en BSON Decimal128 y se transportan como cadenas JSON, evitando convertirlos a floats. Los ejemplos filtrados por `demo_unidad6` no mezclan datos reales.

## Estructura

```text
DaVinciMusic_NoSQL_Unidad6/
├── backend/
│   ├── main.py                 # API, CORS, conexión Atlas, límites de escritura
│   ├── catalog.py              # Consulta de 21 ejercicios y pipelines de 3 vistas
│   ├── seed.py                 # Inserción ficticia idempotente
│   ├── serialize.py            # BSON a JSON seguro (Decimal128, ObjectId, fechas)
│   ├── config.py               # Lectura del .env, sin secretos en frontend
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── components.json         # shadcn / base-nova
│   ├── vite.config.ts
│   ├── src/App.tsx
│   ├── src/components/Results.tsx
│   └── src/components/ui/button.tsx
├── tests/test_catalog.py
└── README.md
```

## Endpoints

| Método | Ruta | Operación |
|---|---|---|
| GET | `/api/health` | Ping a Atlas |
| GET | `/api/estado` | Conteos demo de las 9 colecciones |
| GET | `/api/catalogo` | 21 ejercicios y código mongosh |
| GET | `/api/consultas/{id}` | Ejecuta un ejercicio **predefinido** (100 docs máx.) |
| POST | `/api/datos-prueba` | Inserción ficticia, requiere `DEMO_WRITE_ENABLED=true` |
| POST | `/api/vistas/preparar` | Crear/actualizar 3 vistas, requiere el flag de escritura |

## Pruebas y límites de verificación

Para ejecutar pruebas locales con el entorno virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest ..\tests -q
```

Se verificó estáticamente la sintaxis Python, el TypeScript (sin errores), la estructura del package-lock y la coherencia del catálogo y de las 18 muestras. No es posible confirmar una conexión real a **tu** clúster desde esta entrega: la URI es privada y no se incluyó. Tampoco fue posible completar un `vite build` en el entorno Linux de generación porque el `node_modules` que proporcionaste contiene binarios nativos **de Windows**; en Windows deberás ejecutar los comandos de instalación y compilación anteriores.

## Seguridad

- Para actividades locales únicamente. **No publiques esta API sin añadir autenticación y controles de acceso**. Los endpoints de inserción no tienen login, como pediste.
- El backend se sirve en `127.0.0.1`, no en `0.0.0.0`.
- La URI de MongoDB no debe ser pública ni compartirse; `.gitignore` excluye `.env`.
- El botón de inserción es opcional y está protegido por una variable de entorno en el backend. No implementa modificaciones generales de usuarios o de instrumentos.
- No incluye migración ni CRUD peligroso. No hay `eval`, pipelines arbitrarios, endpoints que acepten consultas MongoDB, ni operaciones para borrar colecciones.
