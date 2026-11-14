"""Configuración de ejecución. Las pruebas deben establecer DAVINCI_LOAD_DOTENV=0."""
import os
from pathlib import Path
from urllib.parse import urlsplit
from dotenv import load_dotenv

if os.getenv("DAVINCI_LOAD_DOTENV", "1") == "1":
    load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)

def required(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Falta configurar {name}")
    return value

DATABASE_URL = required("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

SUPERTOKENS_CONNECTION_URI = required("SUPERTOKENS_CONNECTION_URI").rstrip("/")
SUPERTOKENS_API_KEY = os.getenv("SUPERTOKENS_API_KEY") or None

GOOGLE_CLIENT_ID = required("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = required("GOOGLE_CLIENT_SECRET")

API_DOMAIN = os.getenv("API_DOMAIN", "http://localhost:8000").rstrip("/")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")

TENANT_ID = "public"
for name, value in [("API_DOMAIN", API_DOMAIN), ("FRONTEND_URL", FRONTEND_URL),
                    ("SUPERTOKENS_CONNECTION_URI", SUPERTOKENS_CONNECTION_URI)]:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise RuntimeError(f"URL inválida para {name}")
    if parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise RuntimeError(f"{name} requiere HTTPS fuera de localhost")
if urlsplit(SUPERTOKENS_CONNECTION_URI).hostname not in {"localhost", "127.0.0.1", "::1"} and not SUPERTOKENS_API_KEY:
    raise RuntimeError("SUPERTOKENS_API_KEY es obligatoria para Core remoto")
