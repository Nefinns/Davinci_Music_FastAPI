import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")

ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES","30"))

if not DATABASE_URL:
    raise RuntimeError("No se encontró la variable DATABASE_URL en el archivo .env")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://","postgresql://",1)

if not SECRET_KEY:
    raise RuntimeError("No se encontró la variable SECRET_KEY en el archivo .env")