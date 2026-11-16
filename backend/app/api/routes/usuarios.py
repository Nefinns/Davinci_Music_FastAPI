"""Rutas del perfil y administración de usuarios."""

from asyncio import Semaphore, gather

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pydantic import ConfigDict, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from sqlalchemy.sql.functions import count
from sqlmodel import Session, col, select
from supertokens_python.asyncio import get_user
from supertokens_python.recipe.session.asyncio import revoke_all_sessions_for_user
from supertokens_python.recipe.userroles.asyncio import (
    add_role_to_user,
    get_roles_for_user,
    remove_user_role,
)
from supertokens_python.recipe.userroles.interfaces import (
    AddRoleToUserOkResult,
    RemoveUserRoleOkResult,
)

from app.core.config import TENANT_ID
from app.core.dependencies import (
    obtener_permisos_usuario,
    obtener_roles_usuario,
    obtener_usuario_actual,
    requerir_permiso,
    requerir_rol,
)
from app.core.roles import ROLES
from app.db.session import obtener_sesion
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioPerfil


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


class EdicionPerfil(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre_usuario: str | None = Field(default=None, min_length=3, max_length=100)
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    apellido_paterno: str | None = Field(default=None, min_length=1, max_length=100)
    apellido_materno: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)
    direccion: str | None = Field(default=None, max_length=255)

    @field_validator("nombre_usuario", "nombre", "apellido_paterno")
    @classmethod
    def sin_espacios_vacios(cls, value: str | None) -> str:
        if value is None or not value.strip():
            raise ValueError("No puede estar vacío.")
        return value.strip()


@router.patch("/me", response_model=UsuarioPerfil)
def editar_mi_perfil(
    datos: EdicionPerfil,
    usuario: Usuario = Depends(obtener_usuario_actual),
    sesion: Session = Depends(obtener_sesion),
):
    """Edita datos visibles sin modificar correo, identidad ni privilegios."""
    for nombre, valor in datos.model_dump(exclude_unset=True).items():
        setattr(usuario, nombre, valor.strip() or None if isinstance(valor, str) else valor)
    try:
        sesion.add(usuario)
        sesion.commit()
        sesion.refresh(usuario)
    except IntegrityError:
        sesion.rollback()
        raise HTTPException(409, "Ese nombre de usuario ya está ocupado.") from None
    return usuario


@router.get("/me", response_model=UsuarioPerfil)
def obtener_perfil(
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Devuelve el perfil local del usuario autenticado."""
    return usuario


@router.get("/me/metodos-acceso")
async def obtener_mis_metodos_acceso(
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Indica si la identidad actual ya tiene Google asociado."""
    cuenta = await get_user(usuario.identidad_externa)

    if cuenta is None:
        raise HTTPException(
            status_code=404,
            detail="La cuenta de autenticación no está disponible.",
        )

    google_vinculado = any(
        metodo.recipe_id == "thirdparty"
        and metodo.third_party is not None
        and metodo.third_party.id == "google"
        and TENANT_ID in metodo.tenant_ids
        for metodo in cuenta.login_methods
    )

    contrasena_configurada = any(
        metodo.recipe_id == "emailpassword"
        and TENANT_ID in metodo.tenant_ids
        for metodo in cuenta.login_methods
    )

    return {
        "google_vinculado": google_vinculado,
        "contrasena_configurada": contrasena_configurada,
        "correo": usuario.correo,
    }

@router.get("/me/roles", response_model=list[str])
def obtener_mis_roles(
    roles: list[str] = Depends(obtener_roles_usuario),
):
    """Devuelve los roles del usuario autenticado."""
    return roles


@router.get("/me/permisos", response_model=list[str])
async def obtener_mis_permisos(
    permisos: list[str] = Depends(obtener_permisos_usuario),
):
    """Devuelve los permisos del usuario autenticado."""
    return permisos


async def cambiar_rol(
    id_usuario: int,
    rol: str,
    agregar: bool,
    sesion: Session,
    actor: Usuario,
):
    """Agrega o retira un rol y revoca las sesiones anteriores."""
    if rol not in ROLES:
        raise HTTPException(422, "Rol no permitido.")

    if (
        not agregar
        and rol == "administrador"
        and actor.id_usuario == id_usuario
    ):
        raise HTTPException(
            409,
            "No puedes retirar tu propio rol de administrador desde esta API.",
        )

    destino = sesion.get(Usuario, id_usuario)
    if destino is None:
        raise HTTPException(404, "Usuario no encontrado.")

    if agregar and not destino.activo:
        raise HTTPException(
            409,
            "No se pueden asignar roles a una cuenta inactiva.",
        )

    if not destino.identidad_externa:
        raise HTTPException(
            409,
            "La cuenta no está completamente vinculada.",
        )

    operacion = add_role_to_user if agregar else remove_user_role
    resultado = await operacion(TENANT_ID, destino.identidad_externa, rol)

    if not isinstance(
        resultado,
        (AddRoleToUserOkResult, RemoveUserRoleOkResult),
    ):
        raise HTTPException(409, "No se pudo actualizar el rol.")

    await revoke_all_sessions_for_user(destino.identidad_externa)
    return {
        "mensaje": "Rol actualizado; el usuario debe iniciar sesión nuevamente."
    }


@router.put(
    "/{id_usuario}/roles/{rol}",
    dependencies=[
        Depends(requerir_rol("administrador")),
        Depends(requerir_permiso("usuarios:roles:administrar")),
    ],
)
async def asignar_rol(
    id_usuario: int,
    rol: str,
    sesion: Session = Depends(obtener_sesion),
    actor: Usuario = Depends(obtener_usuario_actual),
):
    """Asigna un rol a un usuario."""
    return await cambiar_rol(id_usuario, rol, True, sesion, actor)


@router.delete(
    "/{id_usuario}/roles/{rol}",
    dependencies=[
        Depends(requerir_rol("administrador")),
        Depends(requerir_permiso("usuarios:roles:administrar")),
    ],
)
async def retirar_rol(
    id_usuario: int,
    rol: str,
    sesion: Session = Depends(obtener_sesion),
    actor: Usuario = Depends(obtener_usuario_actual),
):
    """Retira un rol de un usuario."""
    return await cambiar_rol(id_usuario, rol, False, sesion, actor)


class UsuarioAdministracion(BaseModel):
    """Resumen de un usuario para la vista administrativa."""

    id_usuario: int
    nombre_usuario: str
    nombre: str
    correo: str
    activo: bool
    vinculado: bool
    roles: list[str]


class PaginaUsuarios(BaseModel):
    """Página de resultados de usuarios."""

    items: list[UsuarioAdministracion]
    total: int
    offset: int
    limit: int
    id_actual: int


@router.get(
    "",
    response_model=PaginaUsuarios,
    dependencies=[
        Depends(requerir_rol("administrador")),
        Depends(requerir_permiso("usuarios:roles:administrar")),
    ],
)
async def listar_usuarios(
    q: str = Query("", max_length=100),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=25),
    sesion: Session = Depends(obtener_sesion),
    actor: Usuario = Depends(obtener_usuario_actual),
):
    """Busca usuarios y devuelve una página con sus roles."""
    # Se consultan solo las columnas visibles. No se cargan CURP,
    # INE ni direcciones.
    consulta = select(
        Usuario.id_usuario,
        Usuario.nombre_usuario,
        Usuario.nombre,
        Usuario.correo,
        Usuario.activo,
        Usuario.identidad_externa,
    )

    # SQLAlchemy construye count() dinámicamente; Pylint no lo infiere.
    total_consulta = select(count()).select_from(Usuario)

    if q.strip():
        literal = (
            q.strip()
            .replace("!", "!!")
            .replace("%", "!%")
            .replace("_", "!_")
        )
        termino = f"%{literal}%"

        # SQLModel convierte estos campos en columnas SQLAlchemy
        # al construir la consulta; Pylint los ve como FieldInfo.
        condicion = or_(
            col(Usuario.nombre_usuario).ilike(termino, escape="!"),
            getattr(Usuario, "nombre").ilike(termino, escape="!"),
            getattr(Usuario, "correo").ilike(termino, escape="!"),
        )
        consulta = consulta.where(condicion)
        total_consulta = total_consulta.where(condicion)

    total = sesion.exec(total_consulta).one()
    filas = sesion.exec(
        consulta.order_by(Usuario.id_usuario).offset(offset).limit(limit)
    ).all()

    semaforo = Semaphore(5)

    async def resumen(fila):
        """Añade los roles de SuperTokens al resumen local."""
        roles = []
        if fila.identidad_externa:
            async with semaforo:
                roles = (
                    await get_roles_for_user(
                        TENANT_ID,
                        fila.identidad_externa,
                    )
                ).roles

        return UsuarioAdministracion(
            id_usuario=fila.id_usuario,
            nombre_usuario=fila.nombre_usuario,
            nombre=fila.nombre,
            correo=fila.correo,
            activo=fila.activo,
            vinculado=bool(fila.identidad_externa),
            roles=roles,
        )

    return PaginaUsuarios(
        items=await gather(*(resumen(fila) for fila in filas)),
        total=total,
        offset=offset,
        limit=limit,
        id_actual=actor.id_usuario,
    )
