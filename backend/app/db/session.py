from sqlmodel import Session, create_engine

from app.core.config import DATABASE_URL

engine = create_engine( 
    DATABASE_URL,
    pool_pre_ping = True
)

def obtener_sesion():
    with Session(engine) as sesion:
        yield sesion