import logging
from fastapi import APIRouter, Depends, Request, HTTPException
from starlette.concurrency import run_in_threadpool
from sqlmodel import Session
from supertokens_python.recipe.session.asyncio import create_new_session, revoke_all_sessions_for_user
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.emailpassword.asyncio import (
    create_reset_password_token, consume_password_reset_token, update_email_or_password,
)
from supertokens_python.recipe.emailpassword.interfaces import (
    CreateResetPasswordOkResult, ConsumePasswordResetTokenOkResult, UpdateEmailOrPasswordOkResult,
)
from supertokens_python.types import RecipeUserId
from app.core.config import TENANT_ID, FRONTEND_URL
from app.core.identity import obtener_por_identidad
from app.core.dependencies import sesion_verificada
from app.db.session import obtener_sesion
from app.models.usuario import Usuario
from app.schemas.usuario import (UsuarioRegistro, UsuarioRespuesta, UsuarioLogin,
    SolicitudRecuperacionContrasena, RestablecerContrasena)
from app.services.usuario import registrar_usuario, autenticar_usuario, buscar_por_correo
from app.services.correo import enviar_correo_recuperacion

logger = logging.getLogger(__name__)
async def verificar_origen(request: Request):
    if request.headers.get("origin") not in {None, FRONTEND_URL}:
        raise HTTPException(403, "Origen no permitido.")
    if request.headers.get("rid") != "session":
        raise HTTPException(403, "Falta el encabezado de sesión.")

router = APIRouter(prefix="/auth", tags=["Autenticación"], dependencies=[Depends(verificar_origen)])

@router.post("/registro", response_model=UsuarioRespuesta, status_code=201)
async def registro(datos: UsuarioRegistro, sesion: Session = Depends(obtener_sesion)):
    # La transacción PostgreSQL y SDK syncio comparten un worker; esperar un lock
    # de unicidad no bloquea el event loop de otras solicitudes.
    return await run_in_threadpool(registrar_usuario, datos, sesion)

@router.post("/login")
async def login(request: Request, datos: UsuarioLogin, sesion: Session = Depends(obtener_sesion)):
    resultado = await autenticar_usuario(datos.correo, datos.contrasena, sesion)
    await create_new_session(request, TENANT_ID, resultado.recipe_user_id)
    return {"mensaje": "Sesión iniciada."}

@router.post("/logout")
async def logout(autenticacion: SessionContainer = Depends(sesion_verificada)):
    await autenticacion.revoke_session()
    return {"mensaje": "Sesión cerrada."}

@router.post("/recuperar-contrasena")
async def recuperar(datos: SolicitudRecuperacionContrasena, sesion: Session = Depends(obtener_sesion)):
    usuario = buscar_por_correo(sesion, datos.correo)
    if usuario and usuario.activo:
        if usuario.identidad_externa:
            resultado = await create_reset_password_token(TENANT_ID, usuario.identidad_externa, usuario.correo.strip().lower())
            if isinstance(resultado, CreateResetPasswordOkResult):
                try:
                    await run_in_threadpool(enviar_correo_recuperacion, usuario.correo, resultado.token)
                except Exception:
                    logger.error("No se pudo enviar un correo de recuperación; comprobar SMTP.")
    # Misma respuesta para cuentas inexistentes, inactivas y errores de entrega.
    return {"mensaje": "Si existe una cuenta activa, recibirás un enlace de recuperación."}

@router.post("/restablecer-contrasena")
async def restablecer(datos: RestablecerContrasena, sesion: Session = Depends(obtener_sesion)):
    resultado = await consume_password_reset_token(TENANT_ID, datos.token)
    if not isinstance(resultado, ConsumePasswordResetTokenOkResult):
        raise HTTPException(400, "El enlace no es válido o ha expirado.")
    usuario = obtener_por_identidad(sesion, resultado.user_id)
    if usuario is None or not usuario.activo:
        raise HTTPException(400, "La cuenta no está disponible.")
    # Si Core no puede revocar, no cambiar todavía la contraseña.
    await revoke_all_sessions_for_user(usuario.identidad_externa)
    cambio = await update_email_or_password(RecipeUserId(resultado.user_id), password=datos.nueva_contrasena,
                                           apply_password_policy=True, tenant_id_for_password_policy=TENANT_ID)
    if not isinstance(cambio, UpdateEmailOrPasswordOkResult):
        raise HTTPException(400, "No se pudo cambiar la contraseña. Solicita otro enlace y usa letras y números.")
    return {"mensaje": "Contraseña actualizada. Inicia sesión nuevamente."}
