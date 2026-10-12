
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

import jwt
from app.core.config import SECRET_KEY
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioRegistro
from app.core.security import (ALGORITHM, verificar_password, crear_token_acceso,
                               hash_password, crear_token_recuperacion, verificar_token_recuperacion)


def registrar_usuario(
    datos: UsuarioRegistro,
    sesion: Session
) -> Usuario:
    campos_unicos = {
        "nombre_usuario": datos.nombre_usuario,
        "correo": datos.correo,
        "curp": datos.curp,
    }

    if datos.ine:
        campos_unicos["ine"] = datos.ine

    for campo, valor in campos_unicos.items():
        columna = getattr(Usuario, campo)

        usuario_existente = sesion.exec(
            select(Usuario).where(columna == valor)
        ).first()

        if usuario_existente:
            raise ValueError(
                f"El campo {campo} ya está registrado."
            )

    datos_usuario = datos.model_dump(exclude={"contrasena"})
    datos_usuario["contrasena_hash"] = hash_password(datos.contrasena)

    nuevo_usuario = Usuario(**datos_usuario)

    try:
        sesion.add(nuevo_usuario)
        sesion.commit()
        sesion.refresh(nuevo_usuario)
        return nuevo_usuario

    except IntegrityError as error:
        sesion.rollback()
        raise ValueError(
            "Alguno de los datos únicos ya está registrado."
        ) from error

    except Exception:
        sesion.rollback()
        raise


def autenticar_usuario(
        correo: str,
        contrasena: str,
        sesion: Session,
) -> str | None:
    usuario = sesion.exec(
        select(Usuario).where(
            Usuario.correo == correo
        )
    ).first()

    if not usuario:
        return None

    if not verificar_password(
        contrasena,
        usuario.contrasena_hash,
    ):
        return None

    if not usuario.activo:
        return None

    return crear_token_acceso(usuario.id_usuario)


def generar_token_recuperacion(correo: str, sesion: Session) -> str | None:
    usuario = sesion.exec(
        select(Usuario).where(
            Usuario.correo == correo,
            Usuario.activo == True
        )
    ).first()

    if usuario is None:
        return None

    return crear_token_recuperacion(
        usuario.id_usuario,
        usuario.contrasena_hash
    )


def restablecer_contrasena(
        token: str,
        nueva_contrasena: str,
        sesion: Session
) -> bool:
    try:
        datos_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if datos_token.get("tipo") != "recuperacion":
            return False

        id_usuario = datos_token.get("sub")

        if not id_usuario:
            return False

        usuario = sesion.exec(
            select(Usuario).where(
                Usuario.id_usuario == int(id_usuario)
            )
        ).first()

        if usuario is None or not usuario.activo:
            return False

        id_validado = verificar_token_recuperacion(
            token,
            usuario.contrasena_hash
        )

        if id_validado != usuario.id_usuario:
            return False

        usuario.contrasena_hash = hash_password(nueva_contrasena)

        sesion.add(usuario)
        sesion.commit()
        sesion.refresh(usuario)

        return True

    except (jwt.InvalidTokenError, ValueError, TypeError):
        return False
    except Exception:
        sesion.rollback()
        raise
