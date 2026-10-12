
import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from sqlalchemy import text

from app.core.config import SECRET_KEY
from app.core.security import ALGORITHM
from app.db.session import obtener_sesion
from app.models.usuario import Usuario

bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="JWT",
)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    sesion: Session = Depends(obtener_sesion),
) -> Usuario:
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la autenticación.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credenciales is None:
        raise credenciales_invalidas

    token = credenciales.credentials

    try:
        datos_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        id_usuario = datos_token.get("sub")
        tipo_token = datos_token.get("tipo")

        if not id_usuario or tipo_token != "acceso":
            raise credenciales_invalidas

        id_usuario = int(id_usuario)

    except (jwt.InvalidTokenError, ValueError, TypeError) as error:
        raise credenciales_invalidas from error

    usuario = sesion.exec(
        select(Usuario).where(Usuario.id_usuario == id_usuario)
    ).first()

    if usuario is None or not usuario.activo:
        raise credenciales_invalidas

    return usuario


def obtener_roles_usuario(
    usuario: Usuario = Depends(obtener_usuario_actual),
    sesion: Session = Depends(obtener_sesion),
) -> list[str]:
    roles = []

    cliente_existe = sesion.execute(
        text("""
            SELECT EXISTS (
                SELECT 1
                FROM cliente
                WHERE id_usuario = :id_usuario
            )
        """),
        {"id_usuario": usuario.id_usuario},
    ).scalar_one()

    if cliente_existe:
        roles.append("cliente")

    maestro_activo = sesion.execute(
        text("""
            SELECT EXISTS (
                SELECT 1
                FROM maestro
                WHERE id_usuario = :id_usuario
                  AND activo = TRUE
            )
        """),
        {"id_usuario": usuario.id_usuario},
    ).scalar_one()

    if maestro_activo:
        roles.append("maestro")

    administrador_existe = sesion.execute(
        text("""
            SELECT EXISTS (
                SELECT 1
                FROM administrador
                WHERE id_usuario = :id_usuario
            )
        """),
        {"id_usuario": usuario.id_usuario},
    ).scalar_one()

    if administrador_existe:
        roles.append("administrador")

    return roles


def requerir_rol(*roles_permitidos: str):
    def verificar_roles(
        roles: list[str] = Depends(obtener_roles_usuario),
    ) -> list[str]:
        if not any(rol in roles for rol in roles_permitidos):
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para realizar esta operación.",
            )

        return roles

    return verificar_roles
