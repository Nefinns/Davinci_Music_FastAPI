from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlmodel import Session
from supertokens_python import get_all_cors_headers
from supertokens_python.framework.fastapi import get_middleware
from app.core.supertokens import configurar_supertokens
from app.core.config import FRONTEND_URL
from app.core.roles import preparar_roles

configurar_supertokens()

from app.db.session import obtener_sesion
from app.api.routes.auth import router as auth_router
from app.api.routes.usuarios import router as usuarios_router

@asynccontextmanager
async def lifespan(app):
    await preparar_roles()
    yield

app = FastAPI(title="DavinciMusic API", version="2.0.0", lifespan=lifespan)
app.add_middleware(get_middleware())
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_URL], allow_credentials=True,
                   allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
                   allow_headers=["Content-Type", "Authorization"] + get_all_cors_headers())
app.include_router(auth_router)
app.include_router(usuarios_router)

@app.get("/")
def inicio():
    return {"mensaje": "DavinciMusic API funcionando"}

@app.get("/db-test")
def probar_conexion(sesion: Session = Depends(obtener_sesion)):
    try:
        return {"conexion": "exitosa", "resultado": sesion.execute(text("SELECT 1")).scalar_one()}
    except Exception:
        raise HTTPException(503, "No se pudo consultar la base de datos") from None
