from datetime import date, datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class UsuarioRegistro(SQLModel):
    nombre_usuario: str = Field(min_length=3, max_length=100)
    nombre: str = Field(min_length=1, max_length=100)
    apellido_paterno: str = Field(min_length=1, max_length=100)
    apellido_materno: Optional[str] = Field(default=None, max_length=100)
    fecha_nacimiento: date
    curp: str = Field(min_length=18, max_length=18)
    ine: Optional[str] = Field(default=None, max_length=20)
    correo: str = Field(max_length=150)
    telefono: Optional[str] = Field(default=None, max_length=20)
    direccion: Optional[str] = Field(default=None, max_length=255)
    contrasena: str = Field(min_length=8, max_length=128)


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

class TokenRespuesta(SQLModel):
    access_token: str
    token_type: str = "bearer"

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