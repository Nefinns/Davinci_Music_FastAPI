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
from app.schemas.usuario import UsuarioRegistro, UsuarioRegistroGoogle

logger = logging.getLogger(__name__)


def buscar_por_correo(sesion: Session, correo: str):
    resultados = sesion.exec(select(Usuario).where(func.lower(
        func.btrim(Usuario.correo)) == correo.strip().lower())).all()
    if len(resultados) > 1:
        raise HTTPException(
            409, "Existen cuentas duplicadas; requiere revisión administrativa.")
    return resultados[0] if resultados else None


def registrar_usuario(datos: UsuarioRegistro, sesion: Session) -> Usuario:
    identidad = None
    try:
        correo = str(datos.correo).strip().lower()
        if buscar_por_correo(sesion, correo):
            raise HTTPException(409, "No fue posible registrar esos datos.")
        nuevo = Usuario(**datos.model_dump(exclude={"contrasena", "correo"}),
                        correo=correo)
        sesion.add(nuevo)
        # Las restricciones SQL se validan antes de crear identidad.
        sesion.flush()
        respuesta = sign_up(TENANT_ID, correo, datos.contrasena)
        if not isinstance(respuesta, SignUpOkResult):
            raise HTTPException(409, "No fue posible registrar esos datos.")
        identidad = respuesta.user.id
        nuevo.identidad_externa = identidad
        rol = add_role_to_user(TENANT_ID, identidad, "cliente")
        if not isinstance(rol, AddRoleToUserOkResult):
            raise RuntimeError("Rol cliente no inicializado")
        sesion.execute(text("INSERT INTO cliente (id_usuario) VALUES (:id)"), {
                       "id": nuevo.id_usuario})
        sesion.commit()
    except Exception as error:
        sesion.rollback()
        if identidad:
            try:
                delete_user(identidad)
            except Exception:
                # No registrar correos, hashes, tokens ni detalles de SDK/SQL.
                logger.error(
                    "Registro incompleto: revisar identidad huérfana en Core.")
        if isinstance(error, IntegrityError):
            raise HTTPException(
                409, "No fue posible registrar esos datos.") from None
        raise
    # Una falla de lectura posterior al commit no debe eliminar la identidad.
    sesion.refresh(nuevo)
    return nuevo


def completar_registro_google(
    datos: UsuarioRegistroGoogle,
    identidad: str,
    correo_verificado: str,
    sesion: Session,
) -> Usuario:
    """
    Crea el perfil local de una identidad Google ya autenticada.

    identidad y correo_verificado deben proceder de SuperTokens en la ruta;
    nunca de campos enviados por el navegador.
    """
    if not identidad or len(identidad) > 128:
        raise HTTPException(400, "Identidad externa inválida.")

    correo = correo_verificado.strip().lower()
    if not correo or len(correo) > 150:
        raise HTTPException(400, "Correo de la cuenta no disponible.")

    try:
        existente = sesion.exec(
            select(Usuario).where(Usuario.identidad_externa == identidad)
        ).first()

        if existente:
            if not existente.activo:
                raise HTTPException(403, "Cuenta no disponible o inactiva.")
            # Hace seguro reintentar la petición después de perder la respuesta.
            rol = add_role_to_user(TENANT_ID, identidad, "cliente")
            if not isinstance(rol, AddRoleToUserOkResult):
                raise HTTPException(
                    503, "No se pudo verificar el rol de cliente.")
            return existente

        # Un correo perteneciente a otro perfil requiere vinculación de
        # cuentas; este servicio no se apropia de ese perfil.
        if buscar_por_correo(sesion, correo):
            raise HTTPException(
                409,
                "Ese correo ya pertenece a una cuenta. Inicia sesión con "
                "su método actual y vincula Google desde esa cuenta.",
            )

        nuevo = Usuario(
            **datos.model_dump(),
            correo=correo,
            identidad_externa=identidad,
        )
        sesion.add(nuevo)
        sesion.flush()  # Comprueba UNIQUE antes de modificar el rol externo.

        rol = add_role_to_user(TENANT_ID, identidad, "cliente")
        if not isinstance(rol, AddRoleToUserOkResult):
            raise HTTPException(503, "No se pudo asignar el rol de cliente.")

        sesion.execute(
            text("INSERT INTO cliente (id_usuario) VALUES (:id)"),
            {"id": nuevo.id_usuario},
        )
        sesion.commit()

    except IntegrityError:
        sesion.rollback()
        raise HTTPException(
            409, "No se pudo registrar el perfil; revisa los datos únicos."
        ) from None
    except Exception:
        sesion.rollback()
        raise

    sesion.refresh(nuevo)
    return nuevo

async def autenticar_usuario(correo: str, contrasena: str, sesion: Session):
    resultado = await sign_in(TENANT_ID, correo.strip().lower(), contrasena)
    if not isinstance(resultado, SignInOkResult):
        raise HTTPException(
            401, "Correo o contraseña incorrectos, o cuenta inactiva.")
    usuario = obtener_por_identidad(sesion, resultado.user.id)
    if usuario is None or not usuario.activo:
        raise HTTPException(403, "Cuenta no disponible o inactiva.")
    return resultado
