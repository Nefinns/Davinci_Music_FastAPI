from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
import os
from dotenv import load_dotenv

# 1. Cargar variables de entorno

load_dotenv()

db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise RuntimeError("No se encontró DATABASE_URL en el archivo .env")

# Corrección para URLs que comienzan con postgres://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)


# 2. Crear conexión con PostgreSQL

engine = create_engine(
    db_url,
    echo=True
)

# 3. Modelo de CATEGORIA_INSTRUMENTO

class CategoriaInstrumento(SQLModel, table=True):
    __tablename__ = "categoria_instrumento"

    id_categoria: int | None = Field(
        default=None,
        primary_key=True
    )

    nombre_categoria: str
    descripcion: str | None = None


# 4. Crear aplicación FastAPI

app = FastAPI(
    title="DaVinci Music API"
)

# 5. Ruta principal

@app.get("/")
def leer_raiz():
    return {
        "mensaje": "DaVinci Music API funcionando correctamente"
    }

# 6. A - ALTA

@app.post("/categorias")
def crear_categoria(categoria: CategoriaInstrumento):
    
    with Session(engine) as session:
        
        # Comprobar que no exista una categoría con el mismo nombre
        statement = select(CategoriaInstrumento).where(
            CategoriaInstrumento.nombre_categoria
            == categoria.nombre_categoria
        )

        categoria_existente = session.exec(statement).first()

        if categoria_existente:
            raise HTTPException(
                status_code=409,
                detail="Ya existe una categoría con ese nombre"
            )

        # Crear la nueva categoría
        session.add(categoria)

        # Guardar cambios en PostgreSQL
        session.commit()

        # Obtener el ID generado por PostgreSQL
        session.refresh(categoria)

        return categoria 

# 7. C - CONSULTA

@app.get("/categorias")
def consultar_categorias():
    
    with Session(engine) as session:
        
        # Obtener todas las categorías
        statement = select(CategoriaInstrumento)
        categorias = session.exec(statement).all()

        return categorias

# 8. D - MODIFICACIÓN

@app.put("/categorias/{id_categoria}")
def modificar_categoria(
    id_categoria: int,
    categoria: CategoriaInstrumento
):
    
    with Session(engine) as session:
        
        # Buscar la categoría por su ID
        categoria_existente = session.get(
            CategoriaInstrumento,
            id_categoria
        )

        if not categoria_existente:
            raise HTTPException(
                status_code=404,
                detail="No se encontró la categoría"
            )

        # Comprobar que el nuevo nombre no pertenezca a otra categoría
        statement = select(CategoriaInstrumento).where(
            CategoriaInstrumento.nombre_categoria
            == categoria.nombre_categoria,
            CategoriaInstrumento.id_categoria
            != id_categoria
        )

        nombre_existente = session.exec(statement).first()

        if nombre_existente:
            raise HTTPException(
                status_code=409,
                detail="Ya existe otra categoría con ese nombre"
            )

        # Modificar los datos de la categoría
        categoria_existente.nombre_categoria = categoria.nombre_categoria
        categoria_existente.descripcion = categoria.descripcion

        # Guardar los cambios en PostgreSQL
        session.add(categoria_existente)
        session.commit()

        # Actualizar el objeto con los datos guardados
        session.refresh(categoria_existente)

        return categoria_existente

# 9. B - BAJA

@app.delete("/categorias/{id_categoria}")
def eliminar_categoria(id_categoria: int):
    
    with Session(engine) as session:
        
        # Buscar la categoría por su ID
        categoria_existente = session.get(
            CategoriaInstrumento,
            id_categoria
        )

        if not categoria_existente:
            raise HTTPException(
                status_code=404,
                detail="No se encontró la categoría"
            )

        # Eliminar la categoría
        session.delete(categoria_existente)

        # Guardar los cambios en PostgreSQL
        session.commit()

        return {
            "mensaje": "Categoría eliminada correctamente",
            "id_categoria": id_categoria
        }
    