from datetime import date, datetime
import re
from pydantic import field_validator, EmailStr, ConfigDict
from typing import Optional

from sqlmodel import SQLModel, Field


class UsuarioRegistro(SQLModel):
    model_config = ConfigDict(extra="forbid")
    nombre_usuario: str = Field(min_length=3, max_length=100)
    nombre: str = Field(min_length=1, max_length=100)
    apellido_paterno: str = Field(min_length=1, max_length=100)
    apellido_materno: Optional[str] = Field(default=None, max_length=100)
    fecha_nacimiento: date
    curp: str = Field(min_length=18, max_length=18)
    ine: Optional[str] = Field(default=None, max_length=20)
    correo: EmailStr = Field(max_length=150)
    telefono: Optional[str] = Field(default=None, max_length=20)
    direccion: Optional[str] = Field(default=None, max_length=255)
    contrasena: str = Field(min_length=8, max_length=128)


    @field_validator("curp", mode="before")
    @classmethod
    def validar_curp(cls, value):
        value = value.strip().upper()
        if not re.fullmatch(r"[A-Z][AEIOUX][A-Z]{2}[0-9]{6}[HM][A-Z]{5}[A-Z0-9][0-9]", value):
            raise ValueError("La CURP debe tener un formato válido de 18 caracteres en mayúsculas.")
        return value

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha(cls, value):
        hoy = date.today()
        minimo = date(hoy.year - 120, hoy.month, min(hoy.day, 28))
        if not minimo <= value <= hoy:
            raise ValueError("La fecha de nacimiento debe estar entre hoy y hace 120 años.")
        return value

    @field_validator("nombre_usuario", "nombre", "apellido_paterno")
    @classmethod
    def limpiar_requeridos(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("El campo no puede estar vacío.")
        return value

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, value):
        if not re.search(r"[A-Za-z]", value) or not re.search(r"[0-9]", value):
            raise ValueError("La contraseña debe incluir letras y números.")
        return value

class UsuarioRespuesta(SQLModel):
    id_usuario: int
    nombre_usuario: str
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    fecha_nacimiento: date
    curp: str
    ine: Optional[str]
    correo: str
    telefono: Optional[str]
    direccion: Optional[str]
    activo: bool
    fecha_registro: Optional[datetime]


class UsuarioLogin(SQLModel):
    correo: str = Field(min_length=1, max_length=150)
    contrasena: str = Field(min_length=1, max_length=128)


class UsuarioPerfil(SQLModel):
    id_usuario: int
    nombre_usuario: str
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    correo: str
    activo: bool

class SolicitudRecuperacionContrasena(SQLModel):
    correo: str = Field(min_length = 1, max_length = 150)

class RestablecerContrasena(SQLModel):
    token: str = Field(min_length = 1)
    nueva_contrasena: str = Field(min_length = 8, max_length = 128)
    _validar_contrasena = field_validator("nueva_contrasena")(UsuarioRegistro.validar_contrasena.__func__)
