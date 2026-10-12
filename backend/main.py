# Importaciones externas
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text
from sqlmodel import Session

# Importaciones de módulos propios del proyecto
from app.db.session import obtener_sesion

from app.api.routes.auth import router as auth_router
from app.api.routes.usuarios import router as usuarios_router

app = FastAPI(
    title="DavinciMusic API",
    description="API para la tienda/escuela de música",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(usuarios_router)


@app.get("/")
def inicio():
    return {"mensaje": "DavinciMusic API funcionando"}


@app.get("/db-test")
def probar_conexion(sesion: Session = Depends(obtener_sesion)):
    try:
        resultado = sesion.exec(text("SELECT 1")).one()

        return {
            "conexion": "exitosa",
            "resultado": resultado[0]
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo consultar la base de datos"
        ) from error
