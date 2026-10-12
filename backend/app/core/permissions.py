from fastapi import Depends

from app.core.dependencies import requerir_rol


def requerir_cliente(
    roles: list[str] = Depends(requerir_rol("cliente")),
) -> list[str]:
    return roles


def requerir_maestro(
    roles: list[str] = Depends(requerir_rol("maestro")),
) -> list[str]:
    return roles


def requerir_administrador(
    roles: list[str] = Depends(requerir_rol("administrador")),
) -> list[str]:
    return roles


def requerir_personal_academico(
    roles: list[str] = Depends(requerir_rol("maestro", "administrador")),
) -> list[str]:
    return roles