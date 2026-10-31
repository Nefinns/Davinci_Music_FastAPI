# Compatibilidad de npm y TypeScript (Unidad 5)

El frontend está configurado tomando como referencia los **seis archivos JSON entregados** del proyecto DaVinciMusic.

## Qué se conserva

- `package.json` y `package-lock.json` copiados como un **par sincronizado**: se respetaron versiones y dependencias completas del entorno que ya funcionó.
- `tsconfig.app.json`: TypeScript 6, `ES2023`, JSX React y alias `@/*` hacia `./src/*`.
- `tsconfig.node.json`: `module: nodenext`, tipos de Node y comprobación de `vite.config.ts`. Los comentarios del original son válidos para TypeScript (`tsconfig` usa JSON con comentarios).
- `tsconfig.json`: referencias a los otros dos proyectos TS, compatibles con `tsc -b`.
- `eslint.config.js`: misma configuración del proyecto de desarrollo, necesaria para el script `npm run lint`.
- `vite.config.ts`: plugins React y Tailwind CSS 4 y alias `@` apuntando a `src`.
- `.nvmrc`: versión Node 22.23.4 utilizada en el proyecto, con npm 10.9.9 documentado.

## Por qué NO se incluye `.package-lock.json`

El archivo proporcionado con punto inicial corresponde al bloqueo **interno** de `node_modules` (`node_modules/.package-lock.json`). No es un sustituto del `package-lock.json` de la raíz del frontend, es información derivada de una instalación local y puede reflejar solo la plataforma Windows. No debe copiarse a la raíz del repositorio ni distribuirse como archivo de instalación.

## Procedimiento en Windows PowerShell

Desde `davincimusic_unidad5\frontend` (donde están ambos archivos `package*.json`):

```powershell
node --version
npm --version
npm ci
npm run build
npm run lint
npm run dev
```

`npm ci` **no modifica** `package-lock.json`, a diferencia de `npm install`, e instala exactamente las versiones resueltas (sin incluir `node_modules` en el ZIP).

En Windows se instalarán de forma automática las dependencias opcionales de plataforma necesarias (como las de Rolldown y Tailwind/Oxide); el archivo `package-lock.json` completo contiene resoluciones multiplataforma. No uses `--omit=optional`, `--legacy-peer-deps`, `--force` ni reinstales manualmente Tailwind 3.

Para problemas de arranque: asegúrate de abrir una terminal nueva después de cambiar Node, comprueba que estés **dentro de `frontend/`** y que las carpetas `frontend/node_modules/` no vengan copiadas de otro equipo. Si `npm ci` falla por red/DNS, es un problema de acceso al registro, no necesariamente del lock.

La miniaplicación **no utiliza** React Router, por ser de una sola página, pero conserva su dependencia en este paquete para mantener el lockfile del proyecto principal sin reconstruirlo. Lo mismo aplica a otras bibliotecas instaladas que no se usan directamente en este ejercicio.

**Límite de verificación de esta entrega:** Se comprobó la correspondencia de dependencias entre `package.json` y el paquete raíz del `package-lock.json`; la descarga `npm ci` intentada en el entorno de generación no se pudo completar por DNS del registro npm (`EAI_AGAIN`). Por eso no se afirma haber ejecutado `npm run build` o `npm run lint` sobre dependencias instaladas. Ejecuta ambas comprobaciones al instalar en tu equipo.
