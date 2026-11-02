
from fastapi import APIRouter, Depends

from app.core.dependencies import obtener_usuario_actual, obtener_roles_usuario, obtener_permisos_usuario
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioPerfil


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/me", response_model=UsuarioPerfil)
def obtener_perfil(
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    return usuario

@router.get("/me/roles",response_model = list[str])
def obtener_mis_roles(
    roles: list[str] = Depends(obtener_roles_usuario),
):
    return roles
@router.get("/me/permisos", response_model=list[str])
async def obtener_mis_permisos(permisos: list[str] = Depends(obtener_permisos_usuario)):
    return permisos

from fastapi import HTTPException
from sqlmodel import Session
from supertokens_python.recipe.userroles.asyncio import add_role_to_user, remove_user_role
from supertokens_python.recipe.userroles.interfaces import AddRoleToUserOkResult, RemoveUserRoleOkResult
from supertokens_python.recipe.session.asyncio import revoke_all_sessions_for_user
from app.core.dependencies import requerir_permiso, requerir_rol
from app.core.config import TENANT_ID
from app.core.roles import ROLES
from app.db.session import obtener_sesion

async def cambiar_rol(id_usuario, rol, agregar, sesion, actor):
    if rol not in ROLES:
        raise HTTPException(422, "Rol no permitido.")
    if not agregar and rol == "administrador" and actor.id_usuario == id_usuario:
        raise HTTPException(409, "No puedes retirar tu propio rol de administrador desde esta API.")
    destino = sesion.get(Usuario, id_usuario)
    if destino is None:
        raise HTTPException(404, "Usuario no encontrado.")
    if agregar and not destino.activo:
        raise HTTPException(409, "No se pueden asignar roles a una cuenta inactiva.")
    if not destino.identidad_externa:
        raise HTTPException(409, "La cuenta no está completamente vinculada.")
    operation = add_role_to_user if agregar else remove_user_role
    result = await operation(TENANT_ID, destino.identidad_externa, rol)
    if not isinstance(result, (AddRoleToUserOkResult, RemoveUserRoleOkResult)):
        raise HTTPException(409, "No se pudo actualizar el rol.")
    await revoke_all_sessions_for_user(destino.identidad_externa)
    return {"mensaje": "Rol actualizado; el usuario debe iniciar sesión nuevamente."}

@router.put("/{id_usuario}/roles/{rol}", dependencies=[Depends(requerir_rol("administrador")), Depends(requerir_permiso("usuarios:roles:administrar"))])
async def asignar_rol(id_usuario: int, rol: str, sesion: Session = Depends(obtener_sesion),
                      actor: Usuario = Depends(obtener_usuario_actual)):
    return await cambiar_rol(id_usuario, rol, True, sesion, actor)

@router.delete("/{id_usuario}/roles/{rol}", dependencies=[Depends(requerir_rol("administrador")), Depends(requerir_permiso("usuarios:roles:administrar"))])
async def retirar_rol(id_usuario: int, rol: str, sesion: Session = Depends(obtener_sesion),
                     actor: Usuario = Depends(obtener_usuario_actual)):
    return await cambiar_rol(id_usuario, rol, False, sesion, actor)

from asyncio import gather, Semaphore
from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlmodel import select
from supertokens_python.recipe.userroles.asyncio import get_roles_for_user

class UsuarioAdministracion(BaseModel):
    id_usuario: int
    nombre_usuario: str
    nombre: str
    correo: str
    activo: bool
    vinculado: bool
    roles: list[str]

class PaginaUsuarios(BaseModel):
    items: list[UsuarioAdministracion]
    total: int
    offset: int
    limit: int
    id_actual: int

@router.get("", response_model=PaginaUsuarios,
    dependencies=[Depends(requerir_rol("administrador")), Depends(requerir_permiso("usuarios:roles:administrar"))])
async def listar_usuarios(
    q: str = Query("", max_length=100), offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=25),
    sesion: Session = Depends(obtener_sesion), actor: Usuario = Depends(obtener_usuario_actual),
):
    # Se consultan sólo las columnas visibles. No se cargan hashes, CURP, INE ni direcciones.
    query = select(Usuario.id_usuario, Usuario.nombre_usuario, Usuario.nombre,
                   Usuario.correo, Usuario.activo, Usuario.identidad_externa)
    total_query = select(func.count()).select_from(Usuario)
    if q.strip():
        literal = q.strip().replace("!", "!!").replace("%", "!%").replace("_", "!_")
        term = "%" + literal + "%"
        condition = or_(Usuario.nombre_usuario.ilike(term, escape="!"),
                        Usuario.nombre.ilike(term, escape="!"), Usuario.correo.ilike(term, escape="!"))
        query = query.where(condition)
        total_query = total_query.where(condition)
    total = sesion.exec(total_query).one()
    rows = sesion.exec(query.order_by(Usuario.id_usuario).offset(offset).limit(limit)).all()
    semaphore = Semaphore(5)
    async def resumen(row):
        roles = []
        if row.identidad_externa:
            async with semaphore:
                roles = (await get_roles_for_user(TENANT_ID, row.identidad_externa)).roles
        return UsuarioAdministracion(id_usuario=row.id_usuario, nombre_usuario=row.nombre_usuario,
            nombre=row.nombre, correo=row.correo, activo=row.activo,
            vinculado=bool(row.identidad_externa), roles=roles)
    return PaginaUsuarios(items=await gather(*(resumen(row) for row in rows)), total=total,
                         offset=offset, limit=limit, id_actual=actor.id_usuario)
