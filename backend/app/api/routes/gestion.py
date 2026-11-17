"""Sprint 4: gestión de tienda; permisos vigentes y operaciones transaccionales."""
from decimal import Decimal
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field, field_validator
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from app.api.routes.escuela import Datos, uno, filas
from app.core.dependencies import requerir_rol, obtener_usuario_actual
from app.db.session import obtener_sesion
from app.models.usuario import Usuario

router = APIRouter(prefix='/gestion', tags=['Gestión de tienda'],
                   dependencies=[Depends(requerir_rol('administrador'))])

def administrador(db, u):
    # El rol lo verifica la dependencia; nunca aceptar IDs administrativos del navegador.
    return uno(db, '''INSERT INTO administrador(id_usuario,fecha_contratacion)
        VALUES(:u,CURRENT_DATE) ON CONFLICT(id_usuario) DO UPDATE SET id_usuario=EXCLUDED.id_usuario
        RETURNING id_administrador''', u=u.id_usuario)['id_administrador']

class Proveedor(Datos):
    nombre_proveedor: str = Field(min_length=1, max_length=150)
    rfc: str = Field(pattern=r'^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{3}$', max_length=13)
    correo: str | None = Field(default=None, max_length=150)
    telefono: str | None = Field(default=None, max_length=20)
    direccion: str | None = Field(default=None, max_length=255)
    activo: bool = True
    @field_validator('rfc', mode='before')
    @classmethod
    def rfc_mayusculas(cls, v):
        return v.strip().upper() if isinstance(v,str) else v
    @field_validator('correo')
    @classmethod
    def correo_valido(cls,v):
        if v and ('@' not in v or '.' not in v.rsplit('@',1)[-1]):
            raise ValueError('Correo inválido.')
        return v or None

@router.get('/proveedores')
def proveedores(db: Session=Depends(obtener_sesion)):
    return filas(db, 'SELECT * FROM proveedor ORDER BY nombre_proveedor,id_proveedor')

@router.post('/proveedores',status_code=201)
@router.put('/proveedores/{id}')
def guardar_proveedor(datos:Proveedor,id:int|None=None,db:Session=Depends(obtener_sesion)):
    try:
        d=datos.model_dump()
        if id is None:
            r=uno(db,'''INSERT INTO proveedor(nombre_proveedor,rfc,correo,telefono,direccion,activo)
              VALUES(:nombre_proveedor,:rfc,:correo,:telefono,:direccion,:activo) RETURNING *''',**d)
        else:
            r=uno(db,'''UPDATE proveedor SET nombre_proveedor=:nombre_proveedor,rfc=:rfc,correo=:correo,
              telefono=:telefono,direccion=:direccion,activo=:activo WHERE id_proveedor=:id RETURNING *''',id=id,**d)
            if not r:raise HTTPException(404,'Proveedor no encontrado.')
        db.commit();return dict(r)
    except IntegrityError:
        db.rollback();raise HTTPException(409,'El RFC ya está registrado o existe un conflicto en los datos.') from None

@router.delete('/proveedores/{id}')
def desactivar_proveedor(id:int,db:Session=Depends(obtener_sesion)):
    if not uno(db,'UPDATE proveedor SET activo=FALSE WHERE id_proveedor=:id RETURNING id_proveedor',id=id):
        raise HTTPException(404,'Proveedor no encontrado.')
    db.commit();return {'mensaje':'Proveedor desactivado. Su historial permanece.'}

class LineaOrden(Datos):
    id_instrumento: int = Field(gt=0)
    cantidad_solicitada: int = Field(ge=1,le=10000)
    costo_unitario: Decimal = Field(gt=0,max_digits=10,decimal_places=2)

class Orden(Datos):
    id_proveedor: int = Field(gt=0)
    items: list[LineaOrden] = Field(min_length=1,max_length=100)

@router.get('/instrumentos')
def instrumentos(db:Session=Depends(obtener_sesion)):
    return filas(db,'''SELECT id_instrumento,nombre_instrumento,stock_actual,activo
        FROM instrumento ORDER BY nombre_instrumento''')

@router.get('/ordenes')
def ordenes(db:Session=Depends(obtener_sesion)):
    lista=filas(db,'''SELECT o.*,p.nombre_proveedor,u.nombre||' '||u.apellido_paterno AS administrador,
       COALESCE((SELECT sum(d.cantidad_solicitada*d.costo_unitario) FROM detalle_orden d WHERE d.id_orden=o.id_orden),0) AS total
       FROM orden_abastecimiento o JOIN proveedor p USING(id_proveedor)
       JOIN administrador a USING(id_administrador) JOIN usuario u USING(id_usuario)
       ORDER BY o.id_orden DESC LIMIT 200''')
    for o in lista:
        o['detalles']=filas(db,'''SELECT d.*,i.nombre_instrumento FROM detalle_orden d JOIN instrumento i USING(id_instrumento)
            WHERE id_orden=:id ORDER BY id_instrumento''',id=o['id_orden'])
    return lista

@router.post('/ordenes',status_code=201)
def crear_orden(datos:Orden,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    ids=[i.id_instrumento for i in datos.items]
    if len(ids)!=len(set(ids)):raise HTTPException(422,'No repitas instrumentos en una orden.')
    if not uno(db,'SELECT 1 FROM proveedor WHERE id_proveedor=:id AND activo FOR SHARE',id=datos.id_proveedor):
        raise HTTPException(409,'El proveedor no está disponible.')
    for i in sorted(datos.items,key=lambda x:x.id_instrumento):
        if not uno(db,'SELECT 1 FROM instrumento WHERE id_instrumento=:id AND activo FOR SHARE',id=i.id_instrumento):
            raise HTTPException(409,'Instrumento inexistente o inactivo.')
    a=administrador(db,u)
    o=uno(db,'''INSERT INTO orden_abastecimiento(id_proveedor,id_administrador)
      VALUES(:p,:a) RETURNING id_orden''',p=datos.id_proveedor,a=a)['id_orden']
    for i in datos.items:
        db.execute(text('''INSERT INTO detalle_orden(id_orden,id_instrumento,cantidad_solicitada,costo_unitario)
            VALUES(:o,:id_instrumento,:cantidad_solicitada,:costo_unitario)'''),dict(i.model_dump(),o=o))
    db.commit();return {'mensaje':'Orden registrada. El inventario se incrementará al recibirla.','id_orden':o}

@router.post('/ordenes/{id}/{accion}')
def procesar_orden(id:int,accion:Literal['recibir','cancelar'],db:Session=Depends(obtener_sesion)):
    o=uno(db,'SELECT * FROM orden_abastecimiento WHERE id_orden=:id FOR UPDATE',id=id)
    if not o:raise HTTPException(404,'Orden no encontrada.')
    destino='Recibida' if accion=='recibir' else 'Cancelada'
    if o['estado_orden']==destino:return {'mensaje':'La orden ya está '+destino.lower()+'.'}
    if o['estado_orden']!='Pendiente':raise HTTPException(409,'Solo se puede procesar una orden pendiente.')
    if accion=='recibir':
        detalles=filas(db,'SELECT * FROM detalle_orden WHERE id_orden=:id ORDER BY id_instrumento',id=id)
        if not detalles or any(d['cantidad_recibida'] for d in detalles):
            raise HTTPException(409,'La orden está vacía o tiene recepciones anteriores. Revísala manualmente.')
        for d in detalles:
            db.execute(text('UPDATE instrumento SET stock_actual=stock_actual+:n WHERE id_instrumento=:i'),{'n':d['cantidad_solicitada'],'i':d['id_instrumento']})
        db.execute(text('UPDATE detalle_orden SET cantidad_recibida=cantidad_solicitada WHERE id_orden=:id'),{'id':id})
    db.execute(text('UPDATE orden_abastecimiento SET estado_orden=:e WHERE id_orden=:id'),{'id':id,'e':destino})
    db.commit();return {'mensaje':'Orden '+destino.lower()+'.'}

@router.get('/ventas')
def ventas(q:str=Query('',max_length=100),estado:str=Query('',max_length=30),entrega:str=Query('',max_length=30),
           offset:int=Query(0,ge=0),db:Session=Depends(obtener_sesion)):
    import unicodedata
    q=' '.join(q.split())
    folio=q.lstrip('#').strip()
    # Cada palabra debe aparecer en nombre completo o correo. Normalizar tildes sin extensión SQL.
    normal=lambda v: ''.join(c for c in unicodedata.normalize('NFD',v.lower()) if unicodedata.category(c)!='Mn')
    tokens=normal(q).split()
    nombre="translate(lower(concat_ws(' ',u.nombre,u.apellido_paterno,u.apellido_materno,u.correo)), 'áéíóúüñ', 'aeiouun')"
    condiciones=[];args=dict(e=estado,entrega=entrega)
    for j,t in enumerate(tokens):
        args['t'+str(j)]='%'+t.replace('!','!!').replace('%','!%').replace('_','!_')+'%'
        condiciones.append(nombre+f" LIKE :t{j} ESCAPE '!' ")
    texto=' AND '.join(condiciones) if condiciones else 'TRUE'
    args['folio']=folio if folio.isdigit() else ''
    where=""" FROM venta v JOIN cliente c USING(id_cliente) JOIN usuario u USING(id_usuario)
      LEFT JOIN compra_checkout cc USING(id_venta) LEFT JOIN solicitud_reembolso r USING(id_venta)
      WHERE (:e='' OR v.estado_venta=:e) AND (:entrega='' OR v.estado_entrega=:entrega)
      AND (CAST(v.id_venta AS TEXT)=:folio OR ("""+texto+"))"
    total=uno(db,'SELECT count(*) AS n'+where,**args)['n']
    lista=filas(db,'''SELECT v.*,concat_ws(' ',u.nombre,u.apellido_paterno,u.apellido_materno) AS cliente,u.correo,
      COALESCE(cc.total_centavos,(SELECT sum(d.cantidad*d.precio_unitario*100) FROM detalle_venta d WHERE d.id_venta=v.id_venta)) AS total_centavos,
      r.estado AS estado_reembolso,r.motivo,r.resolucion,r.stripe_refund_id'''+where+' ORDER BY v.id_venta DESC LIMIT 20 OFFSET :offset',offset=offset,**args)
    for v in lista:
        v['detalles']=filas(db,'''SELECT d.*,i.nombre_instrumento FROM detalle_venta d JOIN instrumento i USING(id_instrumento) WHERE id_venta=:id''',id=v['id_venta'])
        v['historial']=filas(db,'''SELECT h.accion,h.fecha,u.nombre AS administrador FROM historial_venta h JOIN usuario u USING(id_usuario)
          WHERE id_venta=:id ORDER BY id_historial''',id=v['id_venta'])
    return {'items':lista,'total':total}

class Entrega(Datos):
    estado: Literal['Preparando','Lista para recoger','Entregada']

@router.post('/ventas/{id}/entrega')
def entregar(id:int,datos:Entrega,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    v=uno(db,'SELECT * FROM venta WHERE id_venta=:id FOR UPDATE',id=id)
    if not v:raise HTTPException(404,'Venta inexistente.')
    if v['estado_venta'] not in ('Pagada','Completada'):raise HTTPException(409,'La venta no tiene un pago confirmado.')
    r=uno(db,'SELECT estado FROM solicitud_reembolso WHERE id_venta=:id',id=id)
    if r and r['estado'] not in ('Rechazado','Fallido'):
        raise HTTPException(409,'Resuelve la solicitud de reembolso antes de preparar o entregar.')
    if v['estado_entrega']==datos.estado:return {'mensaje':'El pedido ya tiene ese estado.'}
    siguientes={'Por preparar':'Preparando','Preparando':'Lista para recoger','Lista para recoger':'Entregada'}
    if siguientes.get(v['estado_entrega'])!=datos.estado:raise HTTPException(409,'Avanza un paso a la vez en la preparación del pedido.')
    a=administrador(db,u)
    db.execute(text('UPDATE venta SET estado_entrega=:e,id_administrador=:a WHERE id_venta=:id'),{'id':id,'e':datos.estado,'a':a})
    db.execute(text('INSERT INTO historial_venta(id_venta,id_usuario,accion) VALUES(:id,:u,:e)'),{'id':id,'u':u.id_usuario,'e':datos.estado})
    db.commit();return {'mensaje':'Pedido actualizado: '+datos.estado+'.'}
