"""Catálogo público y administración de categorías e instrumentos."""
from decimal import Decimal
from typing import Annotated

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.config import CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_CLOUD_NAME
from app.core.dependencies import requerir_rol
from app.db.session import obtener_sesion

router = APIRouter(prefix="/catalogo", tags=["Catálogo"])
admin = [Depends(requerir_rol("administrador"))]
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)


class CategoriaDatos(BaseModel):
    nombre_categoria: str = Field(min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=255)


class InstrumentoDatos(BaseModel):
    id_categoria: int = Field(gt=0)
    nombre_instrumento: str = Field(min_length=1, max_length=100)
    marca: str | None = Field(default=None, max_length=100)
    modelo: str | None = Field(default=None, max_length=100)
    tamano: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=50)
    precio_venta: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock_actual: int = Field(ge=0)
    activo: bool = True


def limpiar(valor: str | None) -> str | None:
    return (valor.strip() or None) if valor is not None else None


def categoria_existente(db: Session, id_categoria: int) -> bool:
    return db.execute(text("SELECT 1 FROM categoria_instrumento WHERE id_categoria=:id"), {"id": id_categoria}).first() is not None


def url_imagen(public_id: str | None) -> str | None:
    if not public_id or not CLOUDINARY_CLOUD_NAME:
        return None
    return cloudinary.CloudinaryImage(public_id).build_url(secure=True, quality="auto", fetch_format="auto")


def producto_dict(row) -> dict:
    data = dict(row._mapping)
    data["imagen_url"] = url_imagen(data.get("imagen_public_id"))
    return data


@router.get("/categorias")
def categorias(db: Session = Depends(obtener_sesion)):
    return [dict(r._mapping) for r in db.execute(text(
        "SELECT id_categoria,nombre_categoria,descripcion FROM categoria_instrumento ORDER BY nombre_categoria"))]


@router.post("/categorias", status_code=201, dependencies=admin)
def crear_categoria(datos: CategoriaDatos, db: Session = Depends(obtener_sesion)):
    nombre = limpiar(datos.nombre_categoria)
    if not nombre:
        raise HTTPException(422, "Nombre obligatorio.")
    try:
        row = db.execute(text("INSERT INTO categoria_instrumento (nombre_categoria,descripcion) "
                              "VALUES (:nombre,:descripcion) RETURNING id_categoria,nombre_categoria,descripcion"),
                         {"nombre": nombre, "descripcion": limpiar(datos.descripcion)}).first()
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Ya existe una categoría con ese nombre.") from None
    return dict(row._mapping)


@router.put("/categorias/{id_categoria}", dependencies=admin)
def editar_categoria(id_categoria: int, datos: CategoriaDatos, db: Session = Depends(obtener_sesion)):
    nombre = limpiar(datos.nombre_categoria)
    if not nombre:
        raise HTTPException(422, "Nombre obligatorio.")
    try:
        row = db.execute(text("UPDATE categoria_instrumento SET nombre_categoria=:nombre, descripcion=:descripcion "
                              "WHERE id_categoria=:id RETURNING id_categoria,nombre_categoria,descripcion"),
                         {"id": id_categoria, "nombre": nombre, "descripcion": limpiar(datos.descripcion)}).first()
        if row is None:
            db.rollback()
            raise HTTPException(404, "Categoría no encontrada.")
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Ya existe una categoría con ese nombre.") from None
    return dict(row._mapping)


@router.delete("/categorias/{id_categoria}", dependencies=admin)
def eliminar_categoria(id_categoria: int, db: Session = Depends(obtener_sesion)):
    try:
        row = db.execute(text("DELETE FROM categoria_instrumento WHERE id_categoria=:id RETURNING id_categoria"),
                         {"id": id_categoria}).first()
        if row is None:
            db.rollback()
            raise HTTPException(404, "Categoría no encontrada.")
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "La categoría contiene instrumentos.") from None
    return {"mensaje": "Categoría eliminada."}


BASE = ("SELECT i.id_instrumento,i.id_categoria,c.nombre_categoria,i.nombre_instrumento,"
        "i.marca,i.modelo,i.tamano,i.color,i.precio_venta,i.stock_actual,i.activo,i.imagen_public_id "
        "FROM instrumento i JOIN categoria_instrumento c ON c.id_categoria=i.id_categoria")


@router.get("/instrumentos")
def listar_instrumentos(q: str = Query("", max_length=100), categoria: int | None = None,
                       marca: str = Query("", max_length=100), pagina: int = Query(1, ge=1),
                       limite: int = Query(12, ge=1, le=50), db: Session = Depends(obtener_sesion)):
    where = ["i.activo=TRUE"]
    params: dict = {"offset": (pagina - 1) * limite, "limite": limite}
    if q.strip():
        where.append("(i.nombre_instrumento ILIKE :q ESCAPE '!' OR i.modelo ILIKE :q ESCAPE '!')")
        params["q"] = "%" + q.strip().replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"
    if categoria is not None:
        where.append("i.id_categoria=:categoria")
        params["categoria"] = categoria
    if marca.strip():
        where.append("i.marca ILIKE :marca ESCAPE '!'")
        params["marca"] = "%" + marca.strip().replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"
    filtro = " WHERE " + " AND ".join(where)
    total = db.execute(text("SELECT count(*) FROM instrumento i" + filtro), params).scalar_one()
    rows = db.execute(text(BASE + filtro + " ORDER BY i.id_instrumento DESC LIMIT :limite OFFSET :offset"), params)
    return {"items": [producto_dict(r) for r in rows], "total": total, "pagina": pagina, "limite": limite}


@router.get("/instrumentos/{id_instrumento}")
def detalle_instrumento(id_instrumento: int, db: Session = Depends(obtener_sesion)):
    row = db.execute(text(BASE + " WHERE i.id_instrumento=:id AND i.activo=TRUE"), {"id": id_instrumento}).first()
    if row is None:
        raise HTTPException(404, "Instrumento no encontrado.")
    return producto_dict(row)


@router.get("/administracion/instrumentos", dependencies=admin)
def instrumentos_admin(db: Session = Depends(obtener_sesion)):
    return [producto_dict(r) for r in db.execute(text(BASE + " ORDER BY i.id_instrumento DESC"))]


@router.post("/instrumentos", status_code=201, dependencies=admin)
def crear_instrumento(datos: InstrumentoDatos, db: Session = Depends(obtener_sesion)):
    if not categoria_existente(db, datos.id_categoria):
        raise HTTPException(422, "Categoría inexistente.")
    if not limpiar(datos.nombre_instrumento):
        raise HTTPException(422, "Nombre obligatorio.")
    valores = datos.model_dump()
    for key in ("nombre_instrumento", "marca", "modelo", "tamano", "color"):
        valores[key] = limpiar(valores[key])
    row = db.execute(text("INSERT INTO instrumento (id_categoria,nombre_instrumento,marca,modelo,tamano,color,precio_venta,stock_actual,activo) "
                          "VALUES (:id_categoria,:nombre_instrumento,:marca,:modelo,:tamano,:color,:precio_venta,:stock_actual,:activo) "
                          "RETURNING id_instrumento"), valores).first()
    db.commit()
    return detalle_instrumento(row.id_instrumento, db) if datos.activo else {"id_instrumento": row.id_instrumento}


@router.put("/instrumentos/{id_instrumento}", dependencies=admin)
def editar_instrumento(id_instrumento: int, datos: InstrumentoDatos, db: Session = Depends(obtener_sesion)):
    if not categoria_existente(db, datos.id_categoria):
        raise HTTPException(422, "Categoría inexistente.")
    valores = datos.model_dump()
    for key in ("nombre_instrumento", "marca", "modelo", "tamano", "color"):
        valores[key] = limpiar(valores[key])
    if not valores["nombre_instrumento"]:
        raise HTTPException(422, "Nombre obligatorio.")
    valores["id"] = id_instrumento
    row = db.execute(text("UPDATE instrumento SET id_categoria=:id_categoria,nombre_instrumento=:nombre_instrumento, "
                          "marca=:marca,modelo=:modelo,tamano=:tamano,color=:color,precio_venta=:precio_venta, "
                          "stock_actual=:stock_actual,activo=:activo WHERE id_instrumento=:id RETURNING id_instrumento"), valores).first()
    if row is None:
        db.rollback()
        raise HTTPException(404, "Instrumento no encontrado.")
    db.commit()
    return {"id_instrumento": id_instrumento, "mensaje": "Instrumento actualizado."}


@router.delete("/instrumentos/{id_instrumento}", dependencies=admin)
def retirar_instrumento(id_instrumento: int, db: Session = Depends(obtener_sesion)):
    row = db.execute(text("UPDATE instrumento SET activo=FALSE WHERE id_instrumento=:id RETURNING id_instrumento"),
                     {"id": id_instrumento}).first()
    if row is None:
        db.rollback()
        raise HTTPException(404, "Instrumento no encontrado.")
    db.commit()
    return {"mensaje": "Instrumento retirado del catálogo."}


@router.post("/instrumentos/{id_instrumento}/imagen", dependencies=admin)
async def subir_imagen(id_instrumento: int, archivo: Annotated[UploadFile, File()],
                      db: Session = Depends(obtener_sesion)):
    actual = db.execute(text("SELECT imagen_public_id FROM instrumento WHERE id_instrumento=:id"),
                        {"id": id_instrumento}).first()
    if actual is None:
        raise HTTPException(404, "Instrumento no encontrado.")
    if archivo.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(422, "Usa una imagen JPG, PNG o WebP.")
    contenido = await archivo.read(5 * 1024 * 1024 + 1)
    if len(contenido) > 5 * 1024 * 1024:
        raise HTTPException(413, "La imagen supera 5 MB.")
    from io import BytesIO
    from PIL import Image, UnidentifiedImageError
    try:
        with Image.open(BytesIO(contenido)) as img:
            if img.format not in {"JPEG", "PNG", "WEBP"}:
                raise HTTPException(422, "Formato de imagen no admitido.")
            img.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(422, "Archivo de imagen inválido.") from None
    if not all((CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)):
        raise HTTPException(503, "Almacenamiento de imágenes no configurado.")
    from starlette.concurrency import run_in_threadpool
    try:
        resultado = await run_in_threadpool(cloudinary.uploader.upload, BytesIO(contenido),
                                            folder="davincimusic/instrumentos", resource_type="image")
        nuevo_id = resultado["public_id"]
    except Exception:
        raise HTTPException(503, "No se pudo subir la imagen.") from None
    try:
        db.execute(text("UPDATE instrumento SET imagen_public_id=:public_id WHERE id_instrumento=:id"),
                   {"public_id": nuevo_id, "id": id_instrumento})
        db.commit()
    except Exception:
        db.rollback()
        await run_in_threadpool(cloudinary.uploader.destroy, nuevo_id)
        raise
    if actual.imagen_public_id:
        try:
            await run_in_threadpool(cloudinary.uploader.destroy, actual.imagen_public_id)
        except Exception:
            pass  # El archivo anterior puede retirarse manualmente en Cloudinary.
    return {"imagen_public_id": nuevo_id, "imagen_url": url_imagen(nuevo_id)}
