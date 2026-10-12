from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
import logging

from app.db.session import obtener_sesion
from app.schemas.usuario import (UsuarioRegistro, UsuarioRespuesta, SolicitudRecuperacionContrasena, RestablecerContrasena, UsuarioLogin, TokenRespuesta)
from app.services.usuario import (autenticar_usuario, generar_token_recuperacion, restablecer_contrasena as servicio_restablecer_contrasena, registrar_usuario)

from app.services.correo import enviar_correo_recuperacion

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = "/auth",
    tags = ["Autenticación"]
)

@router.post(
    "/registro",
    response_model = UsuarioRespuesta,
    status_code = status.HTTP_201_CREATED
)

def registro(
    datos: UsuarioRegistro,
    sesion: Session = Depends(obtener_sesion)
):
    try:
        return registrar_usuario(datos,sesion)

    except ValueError as error:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = str(error)
        ) from error 

@router.post("/login",response_model = TokenRespuesta)
def login(
    datos:UsuarioLogin,
    sesion: Session = Depends(obtener_sesion),
):
    token = autenticar_usuario(
        datos.correo,
        datos.contrasena,
        sesion,
    )

    if token is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Correo o contraseña incorrectos, o cuenta inactiva.",
            headers = {"WWW-Authenticate": "Bearer"}
        )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/recuperar-contrasena")
def solicitar_recuperacion(
    solicitud: SolicitudRecuperacionContrasena,
    sesion: Session = Depends(obtener_sesion)
):
    token = generar_token_recuperacion(
        solicitud.correo,
        sesion
    )

    if token is not None:
        try:
            enviar_correo_recuperacion(
                solicitud.correo,
                token
            )

        except Exception as exc:
            logger.exception(
                "No se pudo enviar el correo de recuperación."
            )

            raise HTTPException(
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
                detail = "No fue posible procesar el envío del correo."
            ) from exc

    return {
        "mensaje":(
            "Si el correo corresponde a una cuenta activa, "
            "la solicitud se ha procesado"
        )
    }

@router.post("/restablecer-contrasena")
def confirmar_restablecimiento(
    solicitud: RestablecerContrasena,
    sesion: Session =  Depends(obtener_sesion)
):
    resultado = servicio_restablecer_contrasena(
        solicitud.token,
        solicitud.nueva_contrasena,
        sesion
    )

    if not resultado:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "El token de recuperación no es válido o ha expirado."
        )

    return {
        "mensaje": "La contraseña se restableció correctamente."
    }