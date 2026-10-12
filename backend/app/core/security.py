from datetime import datetime, timedelta, timezone
import hashlib
import hmac

import jwt

from pwdlib import PasswordHash

from app.core.config import SECRET_KEY, ACCESS_TOKEN_MINUTES

ALGORITHM = "HS256"
RECOVERY_TOKEN_MINUTES = 15

password_hash = PasswordHash.recommended()

def hash_password(contrasena: str) -> str:
    return password_hash.hash(contrasena)

def verificar_password(
        contrasena: str,
        contrasena_hash: str
) -> bool:
    return password_hash.verify(contrasena,contrasena_hash)

def crear_token_acceso(id_usuario: int) -> str:
    ahora = datetime.now(timezone.utc)
    expiracion = ahora + timedelta(
        minutes = ACCESS_TOKEN_MINUTES
    )

    datos_token = {
        "sub": str(id_usuario),
        "iat": ahora,
        "exp": expiracion,
        "tipo": "acceso"
    }

    return jwt.encode(
        datos_token,
        SECRET_KEY,
        algorithm = ALGORITHM,
    )

def crear_token_recuperacion(
        id_usuario: int,
        contrasena_hash: str,
) -> str:
    ahora = datetime.now(timezone.utc)
    expiracion = ahora + timedelta(
        minutes = RECOVERY_TOKEN_MINUTES
    )

    huella = hmac.new(
        SECRET_KEY.encode("utf-8"),
        contrasena_hash.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    datos_token = {
        "sub": str(id_usuario),
        "iat": ahora,
        "exp": expiracion,
        "tipo": "recuperacion",
        "huella_contrasena": huella
    }

    return jwt.encode(
        datos_token,
        SECRET_KEY,
        algorithm = ALGORITHM,
    )

def verificar_token_recuperacion(
        token: str,
        contrasena_hash_actual: str
) -> int|None:
    try:
        datos_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms = [ALGORITHM]
        )

        if datos_token.get("tipo") != "recuperacion":
            return None

        id_usuario = datos_token.get("sub")
        huella_token = datos_token.get("huella_contrasena")

        if not id_usuario or not huella_token:
            return None

        huella_actual = hmac.new(
            SECRET_KEY.encode("utf-8"),
            contrasena_hash_actual.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(huella_token,huella_actual):
            return None

        return int(id_usuario)

    except(jwt.InvalidTokenError, ValueError, TypeError):
        return None
    