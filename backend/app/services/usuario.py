"""Adaptadores del perfil local; SuperTokens es el único proveedor de identidad."""
import logging
from fastapi import HTTPException
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from supertokens_python.syncio import delete_user
from supertokens_python.recipe.emailpassword.asyncio import sign_in
from supertokens_python.recipe.emailpassword.syncio import sign_up
from supertokens_python.recipe.emailpassword.interfaces import SignUpOkResult, SignInOkResult
from supertokens_python.recipe.userroles.syncio import add_role_to_user
from supertokens_python.recipe.userroles.interfaces import AddRoleToUserOkResult
from app.core.config import TENANT_ID
from app.core.identity import obtener_por_identidad
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioRegistro

logger = logging.getLogger(__name__)


def buscar_por_correo(sesion: Session, correo: str):
    resultados = sesion.exec(select(Usuario).where(func.lower(func.btrim(Usuario.correo)) == correo.strip().lower())).all()
    if len(resultados) > 1:
        raise HTTPException(409, "Existen cuentas duplicadas; requiere revisión administrativa.")
    return resultados[0] if resultados else None

def registrar_usuario(datos: UsuarioRegistro, sesion: Session) -> Usuario:
    identidad = None
    try:
        correo = str(datos.correo).strip().lower()
        if buscar_por_correo(sesion, correo):
            raise HTTPException(409, "No fue posible registrar esos datos.")
        nuevo = Usuario(**datos.model_dump(exclude={"contrasena", "correo"}),
                        correo=correo, contrasena_hash=None)
        sesion.add(nuevo)
        sesion.flush()  # Las restricciones SQL se validan antes de crear identidad.
        respuesta = sign_up(TENANT_ID, correo, datos.contrasena)
        if not isinstance(respuesta, SignUpOkResult):
            raise HTTPException(409, "No fue posible registrar esos datos.")
        identidad = respuesta.user.id
        nuevo.identidad_externa = identidad
        rol = add_role_to_user(TENANT_ID, identidad, "cliente")
        if not isinstance(rol, AddRoleToUserOkResult):
            raise RuntimeError("Rol cliente no inicializado")
        sesion.execute(text("INSERT INTO cliente (id_usuario) VALUES (:id)"), {"id": nuevo.id_usuario})
        sesion.commit()
    except Exception as error:
        sesion.rollback()
        if identidad:
            try:
                delete_user(identidad)
            except Exception:
                # No registrar correos, hashes, tokens ni detalles de SDK/SQL.
                logger.error("Registro incompleto: revisar identidad huérfana en Core.")
        if isinstance(error, IntegrityError):
            raise HTTPException(409, "No fue posible registrar esos datos.") from None
        raise
    # Una falla de lectura posterior al commit no debe eliminar la identidad.
    sesion.refresh(nuevo)
    return nuevo

async def autenticar_usuario(correo: str, contrasena: str, sesion: Session):
    resultado = await sign_in(TENANT_ID, correo.strip().lower(), contrasena)
    if not isinstance(resultado, SignInOkResult):
        raise HTTPException(401, "Correo o contraseña incorrectos, o cuenta inactiva.")
    usuario = obtener_por_identidad(sesion, resultado.user.id)
    if usuario is None or not usuario.activo:
        raise HTTPException(403, "Cuenta no disponible o inactiva.")
    return resultado
