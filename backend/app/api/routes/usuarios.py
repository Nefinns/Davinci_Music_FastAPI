
from fastapi import APIRouter, Depends

from app.core.dependencies import obtener_usuario_actual, obtener_roles_usuario
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