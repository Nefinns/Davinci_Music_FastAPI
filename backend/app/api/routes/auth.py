import logging
from fastapi import APIRouter, Depends, Request, HTTPException
from starlette.concurrency import run_in_threadpool
from sqlmodel import Session, select
from supertokens_python.recipe.session.asyncio import create_new_session, revoke_all_sessions_for_user
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.emailpassword.asyncio import (
    create_reset_password_token, consume_password_reset_token, update_email_or_password,
)
from supertokens_python.recipe.emailpassword.interfaces import (
    CreateResetPasswordOkResult, ConsumePasswordResetTokenOkResult, UpdateEmailOrPasswordOkResult,
)
from app.core.config import TENANT_ID, FRONTEND_URL
from app.core.dependencies import sesion_verificada
from app.db.session import obtener_sesion
from app.models.usuario import Usuario
from app.schemas.usuario import (UsuarioRegistro, UsuarioRespuesta, UsuarioLogin,
                                 SolicitudRecuperacionContrasena, RestablecerContrasena)
from app.services.usuario import registrar_usuario, autenticar_usuario, buscar_por_correo

from supertokens_python.asyncio import get_user
from app.schemas.usuario import UsuarioRegistroGoogle
from app.services.usuario import completar_registro_google
from urllib.parse import urlencode

from supertokens_python.recipe.emailpassword.asyncio import (
    send_email as enviar_email_supertokens,
)
from supertokens_python.recipe.emailpassword.types import (
    PasswordResetEmailTemplateVars,
    PasswordResetEmailTemplateVarsUser,
)

logger = logging.getLogger(__name__)

def metodo_contrasena_de(cuenta, correo: str):
    """Busca el método de contraseña de este correo en el tenant actual."""
    correo = correo.strip().lower()

    return next(
        (
            metodo
            for metodo in cuenta.login_methods
            if metodo.recipe_id == "emailpassword"
            and TENANT_ID in metodo.tenant_ids
            and metodo.email is not None
            and metodo.email.strip().lower() == correo
        ),
        None,
    )


async def verificar_origen(request: Request):
    if request.headers.get("origin") not in {None, FRONTEND_URL}:
        raise HTTPException(403, "Origen no permitido.")
    

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
async def recuperar(
    datos: SolicitudRecuperacionContrasena,
    sesion: Session = Depends(obtener_sesion),
):
    usuario = buscar_por_correo(sesion, datos.correo)

    if usuario and usuario.activo and usuario.identidad_externa:
        cuenta = await get_user(usuario.identidad_externa)

        if cuenta is not None and cuenta.id == usuario.identidad_externa:
            correo = usuario.correo.strip().lower()
            metodo = metodo_contrasena_de(cuenta, correo)

            if metodo is not None:
                resultado = await create_reset_password_token(
                    TENANT_ID,
                    metodo.recipe_user_id.get_as_string(),
                    correo,
                )

                if isinstance(resultado, CreateResetPasswordOkResult):
                    try:
                        enlace = (
                            f"{FRONTEND_URL.rstrip('/')}/restablecer-contrasena?"
                            +urlencode({"token":resultado.token})
                        )

                        await enviar_email_supertokens(
                            PasswordResetEmailTemplateVars(
                                user=PasswordResetEmailTemplateVarsUser(
                                    user_id=cuenta.id,
                                    recipe_user_id=metodo.recipe_user_id,
                                    email=usuario.correo
                                ),
                                password_reset_link=enlace,
                                tenant_id=TENANT_ID,
                            )
                        )
                           
                    except Exception:
                        logger.error(
                            "No se pudo completar el envío del correo de recuperación."
                        )

    # No revela si la cuenta existe o qué métodos de acceso tiene.
    return {
        "mensaje": "Si existe una cuenta activa, recibirás un enlace de recuperación."
    }

@router.post("/restablecer-contrasena")
async def restablecer(
    datos: RestablecerContrasena,
    sesion: Session = Depends(obtener_sesion),
):
    resultado = await consume_password_reset_token(TENANT_ID, datos.token)

    if not isinstance(resultado, ConsumePasswordResetTokenOkResult):
        raise HTTPException(400, "El enlace no es válido o ha expirado.")

    # resultado.user_id ahora es el ID del método emailpassword.
    cuenta = await get_user(resultado.user_id)
    if cuenta is None:
        raise HTTPException(400, "La cuenta no está disponible.")

    correo = resultado.email.strip().lower()
    metodo = metodo_contrasena_de(cuenta, correo)

    if (
        metodo is None
        or metodo.recipe_user_id.get_as_string() != resultado.user_id
    ):
        raise HTTPException(400, "La cuenta no está disponible.")

    # La base local guarda el ID principal, no el ID del método.
    usuario = sesion.exec(
        select(Usuario).where(Usuario.identidad_externa == cuenta.id)
    ).first()

    if (
        usuario is None
        or not usuario.activo
        or usuario.correo.strip().lower() != correo
    ):
        raise HTTPException(400, "La cuenta no está disponible.")

    # Conservamos el orden actual: revocar sesiones antes de cambiar la clave.
    await revoke_all_sessions_for_user(cuenta.id)

    cambio = await update_email_or_password(
        metodo.recipe_user_id,
        password=datos.nueva_contrasena,
        apply_password_policy=True,
        tenant_id_for_password_policy=TENANT_ID,
    )

    if not isinstance(cambio, UpdateEmailOrPasswordOkResult):
        logger.warning(
            "No se completó el cambio de contraseña: %s",
            type(cambio).__name__,
        )
        raise HTTPException(
            400,
            "No se pudo cambiar la contraseña. Solicita otro enlace.",
        )
    
    return {"mensaje": "Contraseña actualizada. Inicia sesión nuevamente."}
