"""Escuela e inscripciones sobre las tablas canónicas; sin mensualidades."""
from datetime import date, time
from decimal import Decimal
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict, model_validator
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from supertokens_python.recipe.userroles.asyncio import get_roles_for_user
from app.core.config import TENANT_ID
from app.core.dependencies import obtener_usuario_actual, requerir_rol
from app.db.session import obtener_sesion
from app.models.usuario import Usuario

router = APIRouter(prefix='/escuela', tags=['Escuela'])
admin = [Depends(requerir_rol('administrador'))]

def filas(db, sql, **params):
    return [dict(r) for r in db.execute(text(sql), params).mappings()]

def uno(db, sql, **params):
    return db.execute(text(sql), params).mappings().first()

def guardar(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Los datos entran en conflicto con registros existentes.') from None

class Datos(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Periodo(Datos):
    nombre_periodo: str = Field(min_length=1,max_length=100)
    fecha_inicio: date
    fecha_fin: date
    estado: Literal['Abierto','Cerrado'] = 'Abierto'
    @model_validator(mode='after')
    def fechas(self):
        if self.fecha_fin < self.fecha_inicio: raise ValueError('La fecha final debe ser posterior al inicio.')
        return self

class Maestro(Datos):
    id_usuario: int = Field(gt=0)
    especialidad: str = Field(min_length=1,max_length=100)
    activo: bool = True

class Horario(Datos):
    dia_semana: Literal['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
    hora_inicio: time
    hora_fin: time
    salon: str = Field(default='', max_length=50)
    @model_validator(mode='after')
    def horas(self):
        if self.hora_fin <= self.hora_inicio: raise ValueError('La hora final debe ser posterior al inicio.')
        return self

class Clase(Datos):
    id_maestro: int = Field(gt=0)
    id_instrumento: int = Field(gt=0)
    id_periodo: int = Field(gt=0)
    nombre_clase: str = Field(min_length=1,max_length=100)
    nivel: Literal['Inicial','Intermedio','Avanzado'] = 'Inicial'
    costo_mensual: Decimal = Field(gt=0,max_digits=10,decimal_places=2)
    cupo_maximo: int = Field(ge=1,le=100)
    activa: bool = True
    horarios: list[Horario] = Field(min_length=1,max_length=7)

BASE = '''SELECT c.*, m.id_usuario AS id_usuario_maestro, u.nombre||' '||u.apellido_paterno AS maestro,
 m.especialidad,i.nombre_instrumento,p.nombre_periodo,p.fecha_inicio,p.fecha_fin,p.estado AS estado_periodo,
 (SELECT count(*) FROM inscripcion_clase x WHERE x.id_clase=c.id_clase AND x.estado_inscripcion='Activa') AS inscritos
 FROM clase c JOIN maestro m USING(id_maestro) JOIN usuario u ON u.id_usuario=m.id_usuario
 JOIN instrumento i USING(id_instrumento) JOIN periodo_academico p USING(id_periodo)'''

def clases(db, privada=False):
    lista = filas(db, BASE + ('' if privada else " WHERE c.activa AND m.activo AND u.activo AND p.estado='Abierto' AND p.fecha_fin>=CURRENT_DATE") + ' ORDER BY c.id_clase DESC')
    horarios = filas(db,'SELECT * FROM horario_clase ORDER BY id_horario')
    for c in lista:
        c['horarios']=[h for h in horarios if h['id_clase']==c['id_clase']]
        c['disponibles']=max(0,c['cupo_maximo']-c['inscritos'])
    return lista

@router.get('/clases')
def publicas(db: Session=Depends(obtener_sesion)):
    return clases(db)

@router.get('/administracion',dependencies=admin)
def opciones(db: Session=Depends(obtener_sesion)):
    return {'clases':clases(db,True),
      'periodos':filas(db,'SELECT * FROM periodo_academico ORDER BY fecha_inicio DESC'),
      'maestros':filas(db,"SELECT m.*,u.nombre||' '||u.apellido_paterno AS nombre FROM maestro m JOIN usuario u USING(id_usuario) ORDER BY nombre"),
      'usuarios':filas(db,'SELECT id_usuario,nombre,apellido_paterno,correo FROM usuario WHERE activo AND identidad_externa IS NOT NULL ORDER BY nombre LIMIT 500'),
      'instrumentos':filas(db,'SELECT id_instrumento,nombre_instrumento FROM instrumento WHERE activo ORDER BY nombre_instrumento')}

@router.post('/periodos',dependencies=admin)
def crear_periodo(datos: Periodo, db: Session=Depends(obtener_sesion)):
    try:
        r=uno(db,'''INSERT INTO periodo_academico(nombre_periodo,fecha_inicio,fecha_fin,estado)
          VALUES(:nombre_periodo,:fecha_inicio,:fecha_fin,:estado) RETURNING *''',**datos.model_dump())
        guardar(db)
    except IntegrityError:
        db.rollback(); raise HTTPException(409,'Nombre de periodo duplicado.') from None
    return dict(r)

@router.put('/periodos/{id}',dependencies=admin)
def editar_periodo(id:int,datos:Periodo,db:Session=Depends(obtener_sesion)):
    try:
        r=uno(db,'''UPDATE periodo_academico SET nombre_periodo=:nombre_periodo,fecha_inicio=:fecha_inicio,
          fecha_fin=:fecha_fin,estado=:estado WHERE id_periodo=:id RETURNING *''',id=id,**datos.model_dump())
        if not r: raise HTTPException(404,'Periodo inexistente.')
        guardar(db)
    except IntegrityError:
        db.rollback(); raise HTTPException(409,'Nombre de periodo duplicado.') from None
    return dict(r)

@router.post('/maestros',dependencies=admin)
async def maestro(datos:Maestro,db:Session=Depends(obtener_sesion)):
    u=uno(db,'SELECT * FROM usuario WHERE id_usuario=:id AND activo',id=datos.id_usuario)
    if not u or not u['identidad_externa']: raise HTTPException(422,'Usuario activo vinculado requerido.')
    roles=(await get_roles_for_user(TENANT_ID,u['identidad_externa'])).roles
    if 'maestro' not in roles: raise HTTPException(422,'Primero asigna el rol maestro en Usuarios y roles.')
    r=uno(db,'''INSERT INTO maestro(id_usuario,especialidad,fecha_contratacion,activo)
      VALUES(:id_usuario,:especialidad,CURRENT_DATE,:activo) ON CONFLICT(id_usuario)
      DO UPDATE SET especialidad=EXCLUDED.especialidad,activo=EXCLUDED.activo RETURNING *''',**datos.model_dump())
    guardar(db); return dict(r)

@router.post('/clases',dependencies=admin,status_code=201)
@router.put('/clases/{id}',dependencies=admin)
def guardar_clase(datos:Clase,id:int|None=None,db:Session=Depends(obtener_sesion)):
    # Serializa cambios de horarios y comprobación de choques entre administradores.
    db.execute(text('LOCK TABLE horario_clase IN SHARE ROW EXCLUSIVE MODE'))
    m=uno(db,'SELECT m.* FROM maestro m JOIN usuario u USING(id_usuario) WHERE id_maestro=:id AND m.activo AND u.activo',id=datos.id_maestro)
    p=uno(db,'SELECT * FROM periodo_academico WHERE id_periodo=:id',id=datos.id_periodo)
    if not m or not p or not uno(db,'SELECT 1 FROM instrumento WHERE id_instrumento=:id',id=datos.id_instrumento):
        raise HTTPException(422,'Maestro, instrumento o periodo no disponible.')
    if id:
        if not uno(db,'SELECT 1 FROM clase WHERE id_clase=:id FOR UPDATE',id=id): raise HTTPException(404,'Clase inexistente.')
        n=uno(db,"SELECT count(*) AS n FROM inscripcion_clase WHERE id_clase=:id AND estado_inscripcion='Activa'",id=id)['n']
        if datos.cupo_maximo<n: raise HTTPException(409,'El cupo no puede ser menor a las inscripciones activas.')
    for j,h in enumerate(datos.horarios):
        for anterior in datos.horarios[:j]:
            if anterior.dia_semana==h.dia_semana and anterior.hora_inicio<h.hora_fin and h.hora_inicio<anterior.hora_fin:
                raise HTTPException(422,'Horarios de la misma clase superpuestos.')
        choque=uno(db,'''SELECT 1 FROM horario_clase h JOIN clase c USING(id_clase)
          JOIN periodo_academico p USING(id_periodo) WHERE c.activa AND c.id_clase<>:id
          AND p.fecha_inicio<=:fin AND p.fecha_fin>=:inicio AND h.dia_semana=:dia
          AND h.hora_inicio<:hf AND h.hora_fin>:hi AND (c.id_maestro=:m OR (:salon<>'' AND lower(h.salon)=lower(:salon))) LIMIT 1''',
          id=id or 0,fin=p['fecha_fin'],inicio=p['fecha_inicio'],dia=h.dia_semana,hf=h.hora_fin,hi=h.hora_inicio,m=datos.id_maestro,salon=h.salon)
        if datos.activa and choque: raise HTTPException(409,'El maestro o salón ya tiene una clase en ese horario.')
    if id and uno(db,'''SELECT 1 FROM inscripcion_clase x JOIN cliente cl USING(id_cliente)
        WHERE x.id_clase=:id AND x.estado_inscripcion='Activa' AND cl.id_usuario=:u''',id=id,u=m['id_usuario']):
        raise HTTPException(409,'El profesor asignado tiene una inscripción activa en este grupo. Revisa y da de baja esa inscripción antes de asignarlo.')
    d=datos.model_dump(exclude={'horarios'})
    if id:
        cols=','.join(f'{k}=:{k}' for k in d)
        db.execute(text(f'UPDATE clase SET {cols} WHERE id_clase=:id'),dict(d,id=id))
        db.execute(text('DELETE FROM horario_clase WHERE id_clase=:id'),{'id':id})
    else:
        cols=','.join(d); vals=','.join(':'+k for k in d)
        id=uno(db,f'INSERT INTO clase({cols}) VALUES({vals}) RETURNING id_clase',**d)['id_clase']
    for h in datos.horarios:
        db.execute(text('INSERT INTO horario_clase(id_clase,dia_semana,hora_inicio,hora_fin,salon) VALUES(:id,:dia_semana,:hora_inicio,:hora_fin,:salon)'),dict(h.model_dump(),id=id))
    guardar(db);return {'id_clase':id,'mensaje':'Clase guardada.'}

@router.delete('/clases/{id}',dependencies=admin)
def retirar(id:int,db:Session=Depends(obtener_sesion)):
    if not uno(db,'UPDATE clase SET activa=FALSE WHERE id_clase=:id RETURNING id_clase',id=id):raise HTTPException(404,'Clase inexistente.')
    guardar(db);return {'mensaje':'Clase retirada del catálogo. Las inscripciones permanecen.'}

@router.post('/clases/{id}/inscripciones',dependencies=[Depends(requerir_rol('cliente'))],status_code=201)
def inscribir(id:int,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    c=uno(db,'''SELECT c.*,m.id_usuario AS id_usuario_maestro,p.estado,p.fecha_fin,m.activo AS docente_activo,u.activo AS usuario_activo
      FROM clase c JOIN periodo_academico p USING(id_periodo) JOIN maestro m USING(id_maestro)
      JOIN usuario u ON u.id_usuario=m.id_usuario WHERE id_clase=:id FOR UPDATE OF c''',id=id)
    cliente=uno(db,'SELECT id_cliente FROM cliente WHERE id_usuario=:id',id=u.id_usuario)
    if not cliente:raise HTTPException(409,'No existe tu perfil de cliente.')
    if not c or not c['activa'] or c['estado']!='Abierto' or c['fecha_fin']<date.today() or not c['docente_activo'] or not c['usuario_activo']:
        raise HTTPException(409,'Clase no disponible para inscripción.')
    if c['id_usuario_maestro']==u.id_usuario:
        raise HTTPException(409,'Eres el profesor de esta clase. Consúltala en Área docente; no necesitas inscribirte.')
    if uno(db,"SELECT 1 FROM inscripcion_clase WHERE id_clase=:id AND id_cliente=:cl AND estado_inscripcion='Activa'",id=id,cl=cliente['id_cliente']):
        raise HTTPException(409,'Ya estás inscrito en esta clase.')
    n=uno(db,"SELECT count(*) AS n FROM inscripcion_clase WHERE id_clase=:id AND estado_inscripcion='Activa'",id=id)['n']
    if n>=c['cupo_maximo']:raise HTTPException(409,'No hay cupo disponible.')
    r=uno(db,'''INSERT INTO inscripcion_clase(id_cliente,id_clase,costo_mensual_acordado)
      VALUES(:cl,:id,:costo) RETURNING id_inscripcion''',cl=cliente['id_cliente'],id=id,costo=c['costo_mensual'])
    guardar(db);return {'id_inscripcion':r['id_inscripcion'],'mensaje':'Inscripción registrada. Contrata la mensualidad desde Mis mensualidades.'}

@router.get('/mis-inscripciones')
def mis_inscripciones(u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    lista=filas(db,'''SELECT x.*,c.nombre_clase,(m.id_usuario=cl.id_usuario) AS es_profesor FROM inscripcion_clase x JOIN cliente cl USING(id_cliente)
      JOIN clase c USING(id_clase) JOIN maestro m USING(id_maestro) WHERE cl.id_usuario=:id ORDER BY x.id_inscripcion DESC''',id=u.id_usuario)
    for x in lista:
        x['horarios']=filas(db,'SELECT dia_semana,hora_inicio,hora_fin,salon FROM horario_clase WHERE id_clase=:id ORDER BY id_horario',id=x['id_clase'])
    return lista

@router.get('/inscripciones',dependencies=admin)
def inscripciones(clase:int|None=None,db:Session=Depends(obtener_sesion)):
    return filas(db,'''SELECT x.*,c.nombre_clase,u.nombre||' '||u.apellido_paterno AS alumno,u.correo,(m.id_usuario=cl.id_usuario) AS es_profesor
      FROM inscripcion_clase x JOIN clase c USING(id_clase) JOIN maestro m USING(id_maestro) JOIN cliente cl USING(id_cliente)
      JOIN usuario u ON u.id_usuario=cl.id_usuario WHERE (CAST(:clase AS INTEGER) IS NULL OR x.id_clase=:clase)
      ORDER BY x.id_inscripcion DESC''',clase=clase)

@router.post('/inscripciones/{id}/baja',dependencies=admin)
def baja(id:int,db:Session=Depends(obtener_sesion)):
    r=uno(db,"SELECT id_clase FROM inscripcion_clase WHERE id_inscripcion=:id",id=id)
    if not r:raise HTTPException(404,'Inscripción inexistente.')
    db.execute(text('SELECT id_clase FROM clase WHERE id_clase=:id FOR UPDATE'),{'id':r['id_clase']})
    if uno(db,"SELECT 1 FROM suscripcion_escuela WHERE id_inscripcion=:id AND estado NOT IN ('canceled','incomplete_expired','Expirada')",id=id):
        raise HTTPException(409,'Detén y sincroniza primero el cobro recurrente desde Mensualidades. La baja no debe dejar una suscripción cobrando.')
    db.execute(text("UPDATE inscripcion_clase SET estado_inscripcion='Baja' WHERE id_inscripcion=:id"),{'id':id})
    guardar(db);return {'mensaje':'Baja académica registrada. La cuenta de acceso permanece.'}

@router.get('/docencia',dependencies=[Depends(requerir_rol('maestro'))])
def docencia(u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    # El filtro es obligatorio en servidor, aunque el usuario también sea administrador.
    lista=filas(db,BASE+' WHERE m.id_usuario=:u ORDER BY c.id_clase DESC',u=u.id_usuario)
    for c in lista:
        c['horarios']=filas(db,'SELECT * FROM horario_clase WHERE id_clase=:id ORDER BY id_horario',id=c['id_clase'])
    return lista
