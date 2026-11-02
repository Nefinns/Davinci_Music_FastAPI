from fastapi import Depends, HTTPException
from sqlmodel import Session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.userroles.asyncio import get_roles_for_user, get_permissions_for_role
from supertokens_python.recipe.userroles.interfaces import GetPermissionsForRoleOkResult
from app.core.config import TENANT_ID
from app.core.identity import obtener_por_identidad
from app.db.session import obtener_sesion
from app.models.usuario import Usuario

# Consulta Core para que logout/revocación invaliden también el access token.
sesion_verificada = verify_session(check_database=True)

async def obtener_usuario_actual(
    autenticacion: SessionContainer = Depends(sesion_verificada),
    sesion: Session = Depends(obtener_sesion),
) -> Usuario:
    if autenticacion.get_tenant_id() != TENANT_ID:
        raise HTTPException(403, "Tenant no permitido.")
    usuario = obtener_por_identidad(sesion, autenticacion.get_user_id())
    if usuario is None or not usuario.activo:
        raise HTTPException(403, "Cuenta no disponible o inactiva.")
    return usuario

async def obtener_roles_usuario(usuario: Usuario = Depends(obtener_usuario_actual)) -> list[str]:
    # Lectura actual en Core: una revocación de rol no espera al refresh del token.
    return (await get_roles_for_user(TENANT_ID, usuario.identidad_externa)).roles

async def obtener_permisos_usuario(roles: list[str] = Depends(obtener_roles_usuario)) -> list[str]:
    permisos = set()
    for rol in roles:
        respuesta = await get_permissions_for_role(rol)
        if isinstance(respuesta, GetPermissionsForRoleOkResult):
            permisos.update(respuesta.permissions)
    return sorted(permisos)

def requerir_rol(*permitidos: str):
    async def verificar(roles: list[str] = Depends(obtener_roles_usuario)):
        if not set(roles).intersection(permitidos):
            raise HTTPException(403, "No tienes permisos para realizar esta operación.")
        return roles
    return verificar

def requerir_permiso(*requeridos: str):
    async def verificar(permisos: list[str] = Depends(obtener_permisos_usuario)):
        if not set(requeridos).issubset(permisos):
            raise HTTPException(403, "No tienes permisos para realizar esta operación.")
        return permisos
    return verificar
