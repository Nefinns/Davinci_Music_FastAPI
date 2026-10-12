
import os
import smtplib
import ssl

from email.message import EmailMessage
from urllib.parse import urlencode


def enviar_correo_recuperacion(
    destinatario: str,
    token: str
) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)
    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )

    if not all([smtp_host, smtp_user, smtp_password, smtp_from]):
        raise RuntimeError(
            "Falta configurar las variables SMTP en el archivo .env"
        )

    parametros = urlencode({"token": token})

    enlace = (
        f"{frontend_url.rstrip('/')}/restablecer-contrasena?"
        f"{parametros}"
    )

    mensaje = EmailMessage()
    mensaje["Subject"] = "Recuperación de contraseña - DaVinciMusic"
    mensaje["From"] = smtp_from
    mensaje["To"] = destinatario

    mensaje.set_content(
        f"""Hola:

Recibimos una solicitud para restablecer la contraseña de tu cuenta
de DaVinciMusic.

Para continuar, utiliza el siguiente enlace:

{enlace}

Este enlace expira en 15 minutos. Si no solicitaste este cambio,
puedes ignorar este mensaje.

Saludos,
Equipo DaVinciMusic
"""
    )

    contexto_ssl = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        smtp_host,
        smtp_port,
        context=contexto_ssl,
        timeout=15
    ) as servidor:
        servidor.login(smtp_user, smtp_password)
        servidor.send_message(mensaje)
