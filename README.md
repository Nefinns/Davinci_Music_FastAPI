# DaVinciMusic · Laboratorio de Bases de Datos — Unidad 5

Miniaplicación local independiente para la **Unidad 5 de Bases de Datos**, basada en el esquema canónico real de DaVinciMusic. Incluye **25 consultas simples, 15 JOIN, 15 consultas con funciones agregadas, 5 vistas y 5 funciones PL/pgSQL asociadas a 5 triggers**: **65 ejercicios**.

Esta entrega cubre la ejecución y presentación mediante **dos frameworks: FastAPI (backend) y React con Vite (frontend)**. La implementación separada de consultas SQL puras en modo consola para los proyectos de ejemplo **no está incluida**, conforme a lo solicitado.

## 1. Archivos del ZIP

```text
davincimusic_unidad5/
├── DISEÑO_UI.md                   # Diseño previo de la interfaz
├── README.md                     # Esta guía
├── EVIDENCIAS.md                 # Plan de capturas de la práctica
├── .gitignore
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── main.py
│   ├── sql/esquema_canonico.sql  # 16 tablas, archivo original aportado
│   ├── app/
│   │   ├── catalog.py           # Definición de las 65 operaciones
│   │   ├── database.py          # Aislamiento de la BD
│   │   ├── objects.py           # 5 vistas, 5 funciones y 5 triggers
│   │   ├── seed.py              # Datos de práctica 100 % ficticios
│   │   └── setup.py             # Instalación protegida e idempotente
│   └── tests/test_catalog.py
└── frontend/
    ├── .env.local.example
    ├── package.json                 # Igual al frontend estable del proyecto real
    ├── package-lock.json            # Resolución completa de dependencias, permite npm ci
    ├── eslint.config.js             # Igual al repositorio de desarrollo
    ├── CONFIGURACION_NPM.md         # Compatibilidad, errores frecuentes
    ├── .nvmrc                       # Node 22.23.4
    ├── vite.config.ts
    ├── tsconfig.app.json
    ├── tsconfig.node.json
    ├── components.json
    └── src/
        ├── App.tsx
        ├── api.ts
        ├── main.tsx
        ├── index.css
        ├── types.ts
        ├── components/ui/button.tsx
        └── lib/utils.ts
```

## 2. Tecnologías y versiones

Las dependencias fueron tomadas del `requirements.txt` entregado y del `frontend/package.json` en la rama `desarrollo_proyecto` del repositorio. **No se agregan dependencias nuevas en Python.** El `requirements.txt` de este laboratorio es una selección mínima del listado original, porque no se necesita autenticación, Argon2 ni JWT.

- **Python:** 3.13.17, **pip:** 26.2.2 (entorno documentado del proyecto).
- **FastAPI:** 0.141.1, **SQLAlchemy:** 2.0.54, **psycopg2-binary:** 2.9.13.
- **Node.js:** 22.23.4, **npm:** 10.9.9 (entorno documentado).
- **React:** 19.2.x, **Vite:** 8.3.x, **TypeScript:** 6.0.x.
- **Tailwind CSS:** 4.3.x, plugin `@tailwindcss/vite`, `@base-ui/react`, preset shadcn `base-nova`, iconos Lucide.
- **PostgreSQL:** la misma familia de motor usada en Neon.

`vite.config.ts` incluye `react()` y `tailwindcss()` con alias `@` hacia `src`, alineado con `tsconfig.app.json`. `components.json` conserva el preset `base-nova`. El frontend ahora incluye **el par original `package.json` y `package-lock.json` aportado**, además de **los tres `tsconfig`** y `eslint.config.js` del proyecto real. De esta manera `npm ci` instala versiones resueltas de antemano sin regenerar el lockfile. La lista de dependencias npm es la misma del frontend principal, aunque en esta miniaplicación varias no se usan (por ejemplo React Router).

> **Verificación de versiones:** se validó que `package.json` coincide con las dependencias raíz del lockfile y que este contiene resoluciones para Windows. La prueba `npm ci` en el entorno de generación quedó bloqueada por DNS (`EAI_AGAIN`) al intentar descargar paquetes de npm; por eso **no se pudo certificar aquí `npm run build` / `npm run lint`**. Una vez descargados los paquetes en tu equipo, ejecuta esos comandos para comprobar la compilación. El backend sí pasó sus cinco pruebas unitarias sin base de datos. Revisa **`frontend/CONFIGURACION_NPM.md`** para las configuraciones y los errores anteriores de instalación.

## 3. Crear una base completamente independiente

1. En Neon, crea una **nueva base de datos** llamada exactamente `davinci_music_unidad5`. No reutilices la BD principal ni la experimental de unidad 4. Puedes crearla dentro del proyecto de Neon que ya tienes si el proveedor permite bases adicionales.
2. Copia únicamente la **cadena de conexión de esa base nueva** desde Neon. Asegúrate de que el segmento de ruta de la URL sea `/davinci_music_unidad5` y que corresponda al servidor elegido.
3. La miniaplicación crea las 16 tablas y los datos sintéticos automáticamente al pulsar **Preparar base demo**. **No necesitas ejecutar manualmente el SQL canónico** para la primera instalación.
4. La preparación instala además las 5 vistas, las 5 funciones PL/pgSQL y sus 5 triggers. Si la repites, no duplica registros.

**Protección importante:** la API compara el nombre configurado en `DATABASE_URL` con `UNIT5_ALLOWED_DATABASE` y adicionalmente verifica `SELECT current_database()` en PostgreSQL. Si no coinciden, rechaza los accesos. También rechaza bases con tablas ajenas o datos no identificados como demo. El archivo de esquema original crea 16 tablas; la aplicación agrega una pequeña tabla auxiliar `unidad5_control` para no repetir la carga de datos. No uses un nombre de base de producción que contenga `unidad5`.

## 4. Preparar backend (Windows PowerShell)

Abre una terminal dentro de `davincimusic_unidad5/backend`:

```powershell
py -3.13 --version
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

Si PowerShell impide activar scripts, evita cambiar las políticas de seguridad y usa directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Configuración de credenciales**: copia `.env.example` con el nombre `.env` dentro de `backend`. Sustituye solo los datos de conexión:

```dotenv
DATABASE_URL=postgresql://USUARIO:CONTRASENA@HOST/davinci_music_unidad5?sslmode=require
UNIT5_ALLOWED_DATABASE=davinci_music_unidad5
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

**No copies ninguna contraseña real a GitHub ni al frontend.** No hace falta `SECRET_KEY`, SMTP ni cuentas.

Desde la carpeta `backend` inicia:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- API: <http://127.0.0.1:8000/>
- Catálogo: <http://127.0.0.1:8000/api/catalogo>
- Estado DB: <http://127.0.0.1:8000/api/estado>
- Swagger: <http://127.0.0.1:8000/docs>

Si el puerto 8000 está ocupado, cámbialo en el comando y ajusta `frontend/.env.local` (ver siguiente sección).

## 5. Preparar frontend (otra terminal PowerShell)

```powershell
node --version
npm --version
cd frontend
npm ci
npm run build
npm run lint
npm run dev
```

Abre <http://127.0.0.1:5173>. El frontend usa de forma predeterminada `http://127.0.0.1:8000`. Opcionalmente copia `.env.local.example` a `.env.local` y define:

```dotenv
VITE_API_URL=http://127.0.0.1:8000
```

**Atención:** `VITE_*` es público en el navegador; jamás coloques contraseñas, usuario de Neon o `DATABASE_URL` allí.

### Evitar los problemas previos con el frontend

- No ejecutes `npm init` ni `npm create vite`: el proyecto **ya incluye** todos los archivos de configuración.
- Usa **Node 22.23.4** o compatible (`package.json` exige `>=22.12.0`); no intentes Vite 8 con versiones antiguas de Node.
- **Usa `npm ci` desde la primera instalación:** `package-lock.json` ya viene incluido, validado contra `package.json`. No hace falta ejecutar `npm install` ni recrear archivos del frontend.
- No instales Tailwind 3, no uses `npx tailwindcss init -p` y no reconfigures PostCSS manualmente. Tailwind 4 se carga con `@import 'tailwindcss';` y `@tailwindcss/vite`.
- `@base-ui/react` se usa en `button.tsx` (preset `base-nova`); `eslint.config.js` está presente para que `npm run lint` no falle por falta de configuración.
- No muevas la carpeta `src` ni cambies el alias `@` sin modificar simultáneamente `vite.config.ts` y `tsconfig.app.json`.

## 6. Uso de la aplicación

1. Con backend y frontend encendidos, verifica que aparezca la conexión a la base.
2. Pulsa **Preparar base demo** y confirma. Esto es necesario solo inicialmente (repetirlo no duplica registros).
3. Elige cualquiera de las cinco secciones del menú.
4. Selecciona un ejercicio del listado; lee explicación y SQL utilizado.
5. Si aplica, cambia los parámetros y pulsa **Ejecutar ejemplo**.
6. Inspecciona los resultados y toma capturas para la tarea.
7. En `T01` a `T05`, el resultado de la prueba indica si la regla se cumplió. Los cambios de las demostraciones se revierten con `ROLLBACK`, incluso en el caso del descuento de inventario.

Las 55 operaciones de consultas simples, JOIN y agregadas no escriben datos. Las cinco vistas se consultan con `SELECT`. Las cinco funciones y triggers se crean durante la preparación y se prueban dentro de transacciones revertidas.

## 7. Estructura académica

| Apartado | Códigos | Cantidad | Ubicación |
|---|---|---:|---|
| 5.1 Consultas simples | S01–S25 | 25 | `backend/app/catalog.py` |
| 5.2 JOIN | J01–J15 | 15 | `backend/app/catalog.py` |
| 5.3 Funciones agregadas | A01–A15 | 15 | `backend/app/catalog.py` |
| 5.4 Vistas | V01–V05 | 5 | `backend/app/objects.py` y catálogo |
| 5.5 Funciones y disparadores | T01–T05 | 5 pares función+trigger | `backend/app/objects.py` |

El apartado 5.5 contiene **cinco funciones distintas** y **cinco triggers distintos** (cinco pares). Los triggers controlan stock negativo, precios no positivos, descuento de unidades tras una venta, sobrecupo de una clase y recepción de inventario superior a lo solicitado.

## 8. Comprobaciones

```powershell
# Desde backend, con entorno virtual activo
python -m unittest discover -s tests -v

# Desde frontend, después de npm install
npm run build
npm run lint
```

Estas pruebas automatizadas comprueban la estructura del catálogo y parámetros; **no sustituyen las pruebas de integración con PostgreSQL**. Con Neon conectado, utiliza la interfaz para ejecutar los 65 ejercicios y confirmar que los ejemplos devuelven resultados coherentes.

## 9. GitHub: trabajar en una rama aislada

En el repositorio principal, confirma que no tienes cambios sin guardar:

```powershell
git status
git switch bd_experimental_unidad4
git switch -c bd_experimental_unidad5
```

**Importante:** Antes de copiar el contenido, haz un commit o stash de tus cambios existentes. Copia la miniaplicación como una subcarpeta, por ejemplo `practicas/unidad5/`, para no reemplazar el backend y frontend del proyecto real. Desde la raíz del repositorio:

```powershell
git add practicas/unidad5
git commit -m "Implementar laboratorio experimental unidad 5"
git push -u origin bd_experimental_unidad5
```

No se ejecutaron estos comandos sobre tu repositorio; son instrucciones para realizarlos en tu equipo. La carpeta `.gitignore` impide subir `.env`, `.env.local`, `.venv`, `node_modules` y `dist`.

## 10. Alcance y límites

- No se incluye login, registro, roles, pagos reales ni panel comercial.
- No se incluye la implementación adicional para consola SQL pura ni las bases de datos de los otros miniproyectos; esas actividades se realizarán después.
- La base y personas de prueba son sintéticas; los documentos CURP/RFC y correos no son datos reales.
- La API se liga únicamente a `127.0.0.1`; no está diseñada para despliegue público sin autenticación y controles adicionales.
- No se han realizado pruebas contra tu Neon, porque no se han facilitado credenciales y no deben facilitarse por chat.
