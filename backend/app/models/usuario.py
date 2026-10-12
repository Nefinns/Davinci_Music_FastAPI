from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, text
from sqlmodel import Field, SQLModel


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id_usuario: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )

    nombre_usuario: str = Field(
        sa_column=Column(String(100), nullable=False, unique=True)
    )

    nombre: str = Field(
        sa_column=Column(String(100), nullable=False)
    )

    apellido_paterno: str = Field(
        sa_column=Column(String(100), nullable=False)
    )

    apellido_materno: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True)
    )

    fecha_nacimiento: date = Field(
        sa_column=Column(Date, nullable=False)
    )

    curp: str = Field(
        sa_column=Column(String(18), nullable=False, unique=True)
    )

    ine: Optional[str] = Field(
        default=None,
        sa_column=Column(String(20), nullable=True, unique=True)
    )

    correo: str = Field(
        sa_column=Column(String(150), nullable=False, unique=True)
    )

    telefono: Optional[str] = Field(
        default=None,
        sa_column=Column(String(20), nullable=True)
    )

    direccion: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True)
    )

    contrasena_hash: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    activo: bool = Field(
        default=True,
        sa_column=Column(
            Boolean,
            nullable=False,
            server_default=text("TRUE")
        )
    )

    fecha_registro: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("NOW()")
        )
    )
