# DaVinciMusic

Plataforma en desarrollo para tienda de instrumentos musicales y escuela de música. Implementación propia con FastAPI, PostgreSQL en Neon y React. SuperTokens gestiona identidad, credenciales y sesiones; Cloudinary almacena imágenes. La compra utiliza Stripe Checkout en modo de prueba.

Este README corresponde al ZIP base `(7)(3)` con el penúltimo parche de correcciones y Sprint 4. Para aplicarlo sigue `README_PARCHE_SPRINT4.md`; no ejecutes el esquema canónico sobre una base existente.

## Estado y alcance actual

| Área | Funciones incluidas |
|---|---|
| Usuarios | Registro, acceso convencional y Google, vinculación de métodos, recuperación de contraseña, logout y sesiones con cookies |
| Perfil | Edición de datos autorizados, foto con Cloudinary y avatar con imagen predeterminada |
| Administración de usuarios | Búsqueda, paginación, roles, baja lógica y reactivación |
| Tienda | Categorías, instrumentos, precios, existencias, imágenes, filtros, paginación y detalle público |
| Escuela — Sprint 5 | Periodos, perfiles docentes de usuarios existentes, clases, niveles, costos, cupos y horarios; catálogo académico público |
| Inscripciones — Sprint 6, primera parte | Inscripción del cliente, rechazo de duplicados y cupo agotado, consulta personal y baja por administrador |
| Gestión de tienda — Sprint 4 | Pedidos y entrega en tienda, solicitudes de reembolso total, proveedores y órdenes de abastecimiento con recepción única |
| Compra — Sprint 3 | Carrito, ventas y detalles, reserva de stock, Checkout de prueba, webhook y conciliación del pago; historial básico |
| Contenido público | Inicio, Nosotros y Contacto con datos e imágenes de la escuela |

Las funciones están implementadas en código; deben probarse con los servicios externos configurados en el entorno donde se presentará el proyecto.

## Stack y dependencias

| Capa | Tecnología |
|---|---|
| API | Python, FastAPI, Uvicorn |
| Persistencia | PostgreSQL, SQLModel, SQLAlchemy, psycopg2 |
| Identidad y sesiones | SuperTokens Core administrado, supertokens_python y supertokens-web-js |
| Frontend | React, TypeScript, Vite y React Router |
| Interfaz | Tailwind CSS, componentes shadcn/ui con Base UI y Lucide |
| Imágenes | Cloudinary |
| Recuperación de contraseña | SMTP SSL con smtplib |
| Compra | Stripe Checkout alojado, API REST mediante requests |

Las dependencias están en `requirements.txt`, `frontend/package.json` y `frontend/package-lock.json`. El parche de sprints 5/6/3 reutiliza las dependencias existentes. Stripe CLI es una herramienta externa adicional para recibir webhooks en localhost. Las dependencias para pruebas automatizadas son opcionales y están en `backend/tests/README.md`.

## Modelo de datos

El esquema conserva las 16 tablas canónicas de negocio: usuario, cliente, administrador, maestro, categoria_instrumento, instrumento, periodo_academico, clase, horario_clase, inscripcion_clase, pago_clase, venta, detalle_venta, proveedor, orden_abastecimiento y detalle_orden.

Se agregan dos tablas auxiliares: `compra_checkout` (solicitud idempotente, sesión de Stripe, snapshot de artículos y total) y `evento_pago` (eventos procesados). El penúltimo parche agrega también `solicitud_reembolso` e `historial_venta`. El total actual es **20 tablas**. Se documentan estas extensiones para mantener consistente el modelo con las otras implementaciones del equipo.

`usuario.id_usuario` es la clave local. `identidad_externa` enlaza con el ID principal de SuperTokens; no es un token ni una contraseña. El esquema actual no incluye `contrasena_hash`. SuperTokens administra las credenciales. Las imágenes se referencian mediante `imagen_perfil_public_id` e `imagen_public_id`.

Los roles se consultan en SuperTokens. Asignar el rol maestro no crea automáticamente su registro local: se completa desde Administrar escuela. Las ventas web permiten `venta.id_administrador=NULL` hasta que exista una asignación; no se inventa un administrador al comprar.

La baja de acceso conserva usuario, relaciones e identidad. Un cliente puede solicitar su propia baja; maestros y administradores requieren otro administrador. La reactivación permite volver a iniciar sesión si la identidad externa sigue disponible. La baja de acceso no cancela una inscripción; la baja académica se gestiona por separado.

## PostgreSQL: instalación nueva o actualización

**Base vacía:** ejecuta `DaVinciMusic_schema_canonico.sql` desde pgAdmin o Neon. El esquema actualizado crea las 20 tablas y los índices del parche dentro de una transacción. No requiere ejecutar después las migraciones ya incorporadas. La API no crea tablas al iniciar.

**Base existente:** conserva todos sus datos y ejecuta únicamente las migraciones que falten:

| Cambio | Script |
|---|---|
| Imagen del instrumento | `backend/sql/sprint2_imagen_instrumento.sql` |
| Imagen de perfil | `backend/sql/perfil_imagen.sql` |
| Escuela/inscripciones y compra web | `backend/sql/sprints_5_6_3.sql` |
| Correcciones, pedidos y reembolsos | `backend/sql/sprint_4_correcciones.sql` |

Si ya ejecutaste esos scripts, reemplazar este README y el archivo canónico es solo una actualización de los archivos del proyecto: **no vuelvas a ejecutar el esquema completo en tu base actual**.

La migración de sprints 5/6/3 crea las dos tablas auxiliares, agrega tres índices y permite administrador nulo en ventas web. No modifica usuarios ni identidades. El índice parcial impide dos inscripciones Activa del mismo cliente en la misma clase; una inscripción dada de baja puede conservarse como historial.

## Instalación local en Windows / PowerShell

Trabaja en tu copia actual del proyecto con los parches aplicados. Para una instalación nueva, prepara el entorno desde la raíz:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si tu entorno existente se llama `venv`, usa ese nombre en los comandos; no es necesario crear otro entorno.

Crea o conserva `.env` en la raíz, junto a `backend` y `frontend`:

```dotenv
DATABASE_URL=postgresql://USUARIO:CONTRASENA@HOST/BASE?sslmode=require
SUPERTOKENS_CONNECTION_URI=https://TU_INSTANCIA_DE_SUPERTOKENS
SUPERTOKENS_API_KEY=REEMPLAZAR
GOOGLE_CLIENT_ID=REEMPLAZAR
GOOGLE_CLIENT_SECRET=REEMPLAZAR
API_DOMAIN=http://localhost:8000
FRONTEND_URL=http://localhost:5173
CLOUDINARY_CLOUD_NAME=REEMPLAZAR
CLOUDINARY_API_KEY=REEMPLAZAR
CLOUDINARY_API_SECRET=REEMPLAZAR
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=REEMPLAZAR
SMTP_PASSWORD=REEMPLAZAR
SMTP_FROM=cuenta@example.com
STRIPE_SECRET_KEY=sk_test_REEMPLAZAR
STRIPE_WEBHOOK_SECRET=whsec_REEMPLAZAR
```

Son marcadores de ejemplo, no credenciales utilizables. DATABASE_URL, URI de SuperTokens y las variables de Google son obligatorias en la configuración actual; Core remoto requiere API key. El tenant es `public`. Sin claves de Cloudinary fallan las subidas de imágenes; sin SMTP no se entregan enlaces de recuperación; sin Stripe las compras muestran un aviso y las funciones académicas siguen disponibles.

No publiques `.env` ni coloques secretos en variables `VITE_*`. PostgreSQL del negocio y SuperTokens tienen responsabilidades distintas. Los antiguos SECRET_KEY y ACCESS_TOKEN_MINUTES del JWT propio no forman parte de la configuración actual.

Inicia FastAPI desde la raíz:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

SuperTokens debe estar disponible al arrancar: la aplicación prepara los roles en Core. Consulta `http://localhost:8000/docs` y `http://localhost:8000/db-test`.

En otra terminal, desde la raíz:

```powershell
cd frontend
npm ci
npm run dev
```

En una instalación existente con las dependencias disponibles basta con iniciar Vite. La API predeterminada es `http://localhost:8000`; si necesitas cambiarla configura `VITE_API_URL` en `frontend/.env.local`. Mantén el navegador en `http://localhost:5173` y conserva coherentes API_DOMAIN, FRONTEND_URL y VITE_API_URL. CORS permite el origen exacto de FRONTEND_URL; evita mezclar localhost con 127.0.0.1 en URLs del navegador.

## Proveedores externos

**SuperTokens y Google:** conserva la instancia y configuración existentes. Para una instalación nueva configura un cliente OAuth de aplicación web en Google con la URI de retorno `http://localhost:5173/auth/callback/google` y el origen `http://localhost:5173`; carga su ID y secreto en el backend. Comprueba el flujo contra la configuración del proveedor en `backend/app/core/supertokens.py`. La recuperación de contraseña usa el método emailpassword vinculado; una cuenta solo Google debe agregar contraseña desde su sesión antes de usar ese método.

**Cloudinary:** configura cloud name, API key y secret en el backend. La subida de perfil acepta JPG, PNG o WebP hasta 5 MB. Conserva las imágenes públicas actuales del frontend en `frontend/public/images`.

**Correo:** utiliza un servidor compatible con SMTP SSL y los parámetros anteriores. La recuperación responde de forma genérica aunque el correo no exista o no se pueda enviar; verifica la entrega real.

**Stripe:** sigue `docs/CONFIGURAR_STRIPE_PRUEBAS.md`, incluida en el parche. Usa una clave sk_test_ del mismo entorno que la CLI. No necesitas crear manualmente productos en Stripe ni instalar su SDK Python. Instala Stripe CLI, ejecuta `stripe login` y mantén otra terminal abierta con:

```powershell
stripe listen --events checkout.session.completed,checkout.session.expired,refund.created,refund.updated,refund.failed --forward-to http://localhost:8000/compras/stripe/webhook
```

Copia el whsec_ mostrado por esa terminal a STRIPE_WEBHOOK_SECRET y reinicia FastAPI. La clave de la CLI puede diferir de la del Dashboard. Los pagos están restringidos a pruebas; la integración no habilita cobros de producción. La API REST fija la versión 2025-02-24.acacia.

## Preparación de escuela y datos de demostración

1. Registra las cuentas de prueba mediante la aplicación. Mantén un administrador vinculado y activo; no se incluye un bootstrap público para elevar privilegios.
2. Asigna el rol maestro desde Usuarios y roles. El usuario afectado debe volver a iniciar sesión porque cambiar roles revoca sus sesiones.
3. En Mi cuenta → Administrar escuela → Maestros, completa especialidad y estado del perfil docente.
4. Crea un periodo abierto y vigente; crea clases con maestro, instrumento, nivel, costo mensual, cupo y horarios. El backend rechaza choques de maestro o salón en periodos que coincidan.
5. Opcionalmente ejecuta `backend/sql/datos_demo_escuela.sql` tras preparar un maestro y un instrumento activo. Genera un periodo y tres clases ficticias DEMO sin duplicarlas al repetirlo. Revisa sus horarios antes de la presentación.
6. Crea las inscripciones y compras desde la interfaz; no se inventan usuarios externos ni pagos acreditados mediante SQL.

La referencia a un instrumento en una clase no descuenta inventario. El costo mensual se conserva en la inscripción, pero el cobro de mensualidades aún no está implementado.

## Navegación principal

| Ruta del frontend | Función |
|---|---|
| `/` y `/contacto` | Presentación del negocio y contacto |
| `/inicio` y `/perfil` | Accesos a operaciones y datos personales |
| `/catalogo` y `/catalogo/:id` | Catálogo y detalle para añadir al carrito |
| `/carrito` y `/mis-compras` | Compra y consulta del estado |
| `/escuela` y `/mis-inscripciones` | Oferta académica e inscripciones propias |
| `/administracion/catalogo` | Administración de instrumentos y categorías |
| `/administracion/usuarios` | Roles y estado de cuentas |
| `/administracion/escuela` | Periodos, docentes, clases e inscripciones |

Las operaciones privadas validan sesión con Core, cuenta local activa y permisos en el backend. Conocer una URL no concede autorización. El frontend usa cookies con credentials y el SDK de SuperTokens, no un JWT propio en sessionStorage. La especificación actual de endpoints se consulta en `/docs`.

## Reglas de compra y límites del corte

- Una compra pendiente por cliente. Se continúa, concilia o cancela desde Mis compras.
- El servidor valida stock y precios reales; el total del carrito es estimado. Los detalles conservan los precios de la venta y Checkout conserva un snapshot para reintentos.
- La venta pendiente reserva existencias descontando disponibilidad bajo bloqueo. El pago no descuenta de nuevo; la expiración/cancelación devuelve la reserva una sola vez.
- Mientras hay reservas, stock_actual expresa disponibilidad libre; antes de ajustar manualmente existencias físicas, resuelve las compras pendientes para no sobrescribir reservas.
- El webhook verifica firma, venta, moneda e importe. Los eventos repetidos no acreditan dos veces. Visitar la página de retorno no acredita el pago.
- Si se interrumpió el reenvío de eventos, Actualizar estado consulta Stripe y concilia. No hay un conciliador periódico propio. Un timeout conserva la reserva hasta poder continuar o cancelar.
- Checkout utiliza MXN, tarjetas y recogida en tienda. Se admiten entre $10 y $999,999.99 MXN por compra, hasta 30 productos diferentes y 20 unidades por producto. El historial muestra las últimas 100 compras.
- Cancelar pendiente no equivale a reembolsar una venta pagada. Envíos, reembolsos y facturación fiscal quedan fuera de este corte.

## Verificación

```powershell
# Desde la raíz, usando el entorno correspondiente
.\.venv\Scripts\python.exe -m pip check

# Desde frontend
npm run build
npm run lint
```

El penúltimo parche pasó compilación, lint, sintaxis Python y 20 pruebas con SQL PostgreSQL embebido y proveedores simulados. Las instrucciones de reproducción están en `backend/tests/README.md`; el alcance de esas pruebas está en `docs/VERIFICACION.md`. No equivalen a probar Neon, SuperTokens y Checkout en el entorno final ni a pruebas de carga concurrente.

Antes de presentar: verifica acceso convencional y Google, recuperación, perfil, baja/reactivación; inscripción y rechazo de duplicados/cupo; baja académica; compra con tarjeta de prueba, confirmación por webhook y cancelación sin devolver stock dos veces. Usa el recorrido de `README_PARCHE_SPRINT4.md`.

## Pendientes acordados

- **Ampliar el catálogo de instrumentos**, seleccionando imágenes reutilizables y registrando procedencia/licencia. El sembrado opcional agrega 20 artículos ficticios DEMO sin fotos; no sustituye la ampliación del catálogo comercial.
- Segunda parte del Sprint 6: mensualidades, cobros recurrentes y sincronización de suscripciones.
- Sprint 7 reducido: asistencia y panel docente; ampliar los accesos básicos del alumno cuando corresponda.
- Sprint 8 reducido: conteos del administrador y exportaciones CSV.
- Pospuestos: cupones, reportes detallados, calendario interactivo, reprogramaciones, seguimiento avanzado y producción.

La tabla pago_clase sigue pendiente de integración con mensualidades. Proveedores y abastecimiento ya están disponibles en Administración. Las ramas de prácticas de Bases de Datos son trabajos separados y no se integran automáticamente en la aplicación principal.


## Navegación y operación del Sprint 4

Mi cuenta conserva perfil y métodos de acceso. La cabecera común incluye Mi cuenta junto al avatar y el menú Mi espacio: Mi aprendizaje, Mis compras, Área docente y Administración según roles. Administración agrupa usuarios, catálogo, escuela, pedidos y proveedores/abastecimiento.

La entrega se sigue en `venta.estado_entrega` y no cambia el estado del pago. Las compras siguen siendo para recoger en tienda. Un cliente puede cancelar un pendiente o solicitar reembolso completo de una compra pagada aún no entregada; un administrador debe aprobarlo. Solo la confirmación de Stripe cambia el pago a Reembolsada y restituye inventario. Consulta límites, recuperación, datos demo y pasos completos en `README_PARCHE_SPRINT4.md`.

Los usuarios existentes se conservan. La nueva migración agrega columnas/tablas, sin tocar identidades externas. Las inscripciones anteriores del propio profesor se señalan para revisión administrativa y no se eliminan automáticamente.
