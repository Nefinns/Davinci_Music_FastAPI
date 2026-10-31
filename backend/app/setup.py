
"""Preparación de la base de datos experimental de la Unidad 5."""

from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import text

from .database import connect_checked
from .objects import install_objects
from .seed import seed_demo


TABLES = {
    "usuario",
    "cliente",
    "administrador",
    "maestro",
    "periodo_academico",
    "categoria_instrumento",
    "instrumento",
    "clase",
    "horario_clase",
    "inscripcion_clase",
    "pago_clase",
    "venta",
    "detalle_venta",
    "proveedor",
    "orden_abastecimiento",
    "detalle_orden",
}

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "sql"
    / "esquema_canonico.sql"
)


def current_tables(conn):
    """Obtiene los nombres de las tablas del esquema actual."""

    query = text(
        """
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = current_schema()
        """
    )

    return set(conn.execute(query).scalars())


def is_ready(conn):
    """Comprueba que la base experimental esté preparada."""

    tables = current_tables(conn)

    if not TABLES.issubset(tables):
        return False

    if "unidad5_control" not in tables:
        return False

    query = text(
        """
        SELECT EXISTS (
            SELECT 1
            FROM unidad5_control
            WHERE clave = 'datos_demo_v1'
        )
        """
    )

    return bool(conn.execute(query).scalar())


def read_schema():
    """Lee el esquema y prepara las instrucciones SQL."""

    script = SCRIPT.read_text(encoding="utf-8-sig")

    # El archivo canónico usa comentarios SQL de línea (--).
    # Los retiramos antes de dividir las instrucciones.
    lines = [
        line.split("--", 1)[0]
        for line in script.splitlines()
    ]

    clean_script = "\n".join(lines)

    statements = [
        statement.strip()
        for statement in clean_script.split(";")
        if statement.strip()
    ]

    return [
        statement
        for statement in statements
        if statement.upper() not in ("BEGIN", "COMMIT")
    ]


def prepare():
    """Crea el esquema y prepara los datos de demostración."""

    conn = connect_checked()

    try:
        with conn.begin():
            current = current_tables(conn)
            existing = TABLES & current

            if existing and existing != TABLES:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "El esquema está incompleto. "
                        "Utiliza una base de datos nueva y vacía "
                        "para la Unidad 5."
                    ),
                )

            created_now = not bool(existing)

            if created_now:
                if current:
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "La base de datos contiene tablas ajenas. "
                            "Utiliza una base completamente vacía."
                        ),
                    )

                statements = read_schema()

                if not statements:
                    raise HTTPException(
                        status_code=500,
                        detail="El archivo del esquema SQL está vacío.",
                    )

                for statement in statements:
                    conn.exec_driver_sql(statement)

            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS unidad5_control (
                        clave TEXT PRIMARY KEY,
                        valor TEXT NOT NULL
                    )
                    """
                )
            )

            seeded = conn.execute(
                text(
                    """
                    SELECT valor
                    FROM unidad5_control
                    WHERE clave = 'datos_demo_v1'
                    """
                )
            ).scalar_one_or_none()

            if not seeded:
                tables_to_check = (
                    "usuario",
                    "instrumento",
                    "clase",
                    "venta",
                    "inscripcion_clase",
                    "proveedor",
                )

                for table_name in tables_to_check:
                    query = text(
                        f"SELECT EXISTS (SELECT 1 FROM {table_name})"
                    )

                    has_data = conn.execute(query).scalar()

                    if has_data:
                        raise HTTPException(
                            status_code=409,
                            detail=(
                                "Hay datos preexistentes no identificados "
                                "como datos de demostración. "
                                "No se añadirán nuevos registros."
                            ),
                        )

                counters = seed_demo(conn)

                conn.execute(
                    text(
                        """
                        INSERT INTO unidad5_control (clave, valor)
                        VALUES ('datos_demo_v1', 'instalado')
                        """
                    )
                )

            else:
                counters = {
                    "mensaje": (
                        "Los datos de demostración ya existían; "
                        "no se duplicaron."
                    )
                }

            install_objects(conn)

        return {
            "ok": True,
            "message": "La base experimental está preparada.",
            "created_now": created_now,
            "seed": counters,
            "views": 5,
            "functions": 5,
            "triggers": 5,
        }

    finally:
        conn.close()
