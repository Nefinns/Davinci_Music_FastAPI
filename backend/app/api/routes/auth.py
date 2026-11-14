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

from supertokens_python.asyncio import get_user
from sqlalchemy import select
from app.schemas.usuario import UsuarioRegistroGoogle
from app.services.usuario import completar_registro_google

logger = logging.getLogger(__name__)


async def verificar_origen(request: Request):
    if request.headers.get("origin") not in {None, FRONTEND_URL}:
        raise HTTPException(403, "Origen no permitido.")
    if request.headers.get("rid") != "session":
        raise HTTPException(403, "Falta el encabezado de sesión.")

router = APIRouter(
    prefix="/auth", tags=["Autenticación"], dependencies=[Depends(verificar_origen)])


async def obtener_google_de_sesion(
    autenticacion: SessionContainer,
) -> tuple[str, str]:
    """Devuelve (ID principal, correo) desde SuperTokens, nunca desde el formulario."""
    if autenticacion.get_tenant_id() != TENANT_ID:
        raise HTTPException(403, "Tenant no permitido.")

    identidad = autenticacion.get_user_id()
    usuario_externo = await get_user(identidad)

    if usuario_externo is None:
        raise HTTPException(401, "La identidad ya no está disponible.")

    recipe_user_id = autenticacion.get_recipe_user_id().get_as_string()

    metodo_google = next(
        (
            metodo
            for metodo in usuario_externo.login_methods
            if metodo.recipe_user_id.get_as_string() == recipe_user_id
            and metodo.recipe_id == "thirdparty"
            and metodo.third_party is not None
            and metodo.third_party.id == "google"
            and TENANT_ID in metodo.tenant_ids
            and metodo.verified
            and metodo.email
        ),
        None,
    )

    if metodo_google is None:
        raise HTTPException(
            403,
            "Esta operación requiere una sesión iniciada con Google.",
        )

    return identidad, metodo_google.email.strip().lower()


@router.get("/estado-perfil")
async def estado_perfil(
    autenticacion: SessionContainer = Depends(sesion_verificada),
    sesion: Session = Depends(obtener_sesion),
):
    if autenticacion.get_tenant_id() != TENANT_ID:
        raise HTTPException(403, "Tenant no permitido.")

    identidad = autenticacion.get_user_id()
    usuario = sesion.exec(
        select(Usuario).where(Usuario.identidad_externa == identidad)
    ).first()

    if usuario is not None:
        if not usuario.activo:
            raise HTTPException(403, "Cuenta no disponible o inactiva.")
        return {
            "estado": "completo",
            "id_usuario": usuario.id_usuario,
        }

    # Solo una identidad Google verificada puede quedar pendiente
    # de completar el registro mediante este flujo.
    _, correo = await obtener_google_de_sesion(autenticacion)

    existente = buscar_por_correo(sesion, correo)
    if existente is not None:
        return {
            "estado": "vincular_cuenta",
            "correo": correo,
        }

    return {
        "estado": "pendiente",
        "correo": correo,
    }


@router.post(
    "/completar-registro-google",
    response_model=UsuarioRespuesta,
    status_code=201,
)
async def completar_registro_con_google(
    datos: UsuarioRegistroGoogle,
    autenticacion: SessionContainer = Depends(sesion_verificada),
    sesion: Session = Depends(obtener_sesion),
):
    identidad, correo = await obtener_google_de_sesion(autenticacion)

    # El servicio y la transacción SQL actuales son síncronos.
    return await run_in_threadpool(
        completar_registro_google,
        datos,
        identidad,
        correo,
        sesion,
    )

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
                    logger.error(
                        "No se pudo enviar un correo de recuperación; comprobar SMTP.")
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
        raise HTTPException(
            400, "No se pudo cambiar la contraseña. Solicita otro enlace y usa letras y números.")
    return {"mensaje": "Contraseña actualizada. Inicia sesión nuevamente."}
