# Diseño previo a implementación — DaVinciMusic Unidad 5

## Propósito
Miniaplicación académica local para 65 ejercicios: 25 consultas simples, 15 JOIN, 15 agregadas, 5 vistas y 5 funciones asociadas a 5 disparadores. Sin cuentas ni permisos.

## Pantalla principal
1. Encabezado compacto con logotipo tipográfico, título y estado de PostgreSQL.
2. Navegación lateral por tema con contador (25, 15, 15, 5, 5).
3. Catálogo filtrable de ejercicios, con código, nombre, dificultad y descripción breve.
4. Zona de detalle: explicación, consulta/código SQL de referencia, parámetros editables y botón de ejecución.
5. Resultados en tabla con nombres de columnas, duración, filas y mensajes de estado; estado vacío y errores comprensibles.
6. Control dedicado de preparación de BD experimental; advertencia de que es una base separada. Vistas y triggers instalados durante preparación.

## Diseño visual
Paleta tomada de DaVinciMusic: verde #0A3D3A, dorado #C8A04A, marfil #F3F5F2, negro #14181B. Tipografía sans accesible, tarjetas de bordes suaves, indicadores neutros y diseño adaptable a escritorio y móvil. Iconos con lucide-react.

## Interacciones
- Selección de un ejercicio actualiza detalles y SQL sin navegación ni recarga.
- Un clic ejecuta una operación predefinida vía FastAPI. No se aceptan SQL arbitrarios desde el cliente.
- Parámetros via inputs tipados; se envían como parámetros enlazados a SQLAlchemy.
- Los cinco ejemplos de trigger se prueban sobre una transacción temporal que se revierte; no persisten sus cambios.
- Preparación inicial por botón crea las tablas solamente en una base vacía y carga registros ficticios.

## Límites deliberados
No se replica el portal real, ni autenticación, ni CRUD de negocio, ni scripts SQL de consultas para el modo consola. El esquema canónico adjunto se conserva como artefacto de preparación. La API exige el nombre explícito de la BD experimental antes de cualquier acceso.
