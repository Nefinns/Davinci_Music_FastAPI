"""Vínculo local: sólo IDs de usuario de SuperTokens, nunca IDs de sesión."""
from fastapi import HTTPException
from sqlmodel import select
from app.models.usuario import Usuario

def obtener_por_identidad(sesion, identity: str) -> Usuario:
    usuario = sesion.exec(select(Usuario).where(Usuario.identidad_externa == identity)).first()
    if usuario is None or not usuario.activo:
        raise HTTPException(403, "Cuenta no vinculada o inactiva.")
    return usuario
