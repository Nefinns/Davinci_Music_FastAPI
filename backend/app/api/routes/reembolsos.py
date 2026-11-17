from fastapi import APIRouter,Depends,HTTPException
from pydantic import Field
from sqlalchemy import text
from sqlmodel import Session
from app.api.routes.escuela import Datos,uno
from app.core.dependencies import obtener_usuario_actual,requerir_rol
from app.db.session import obtener_sesion
from app.models.usuario import Usuario
from app.services.reembolsos import venta_bloqueada,procesar

router=APIRouter(tags=['Reembolsos'])

class Motivo(Datos):
    motivo:str=Field(min_length=5,max_length=500)

@router.post('/compras/{id}/reembolso')
def solicitar(id:int,datos:Motivo,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    # No revelar existencia de compras ajenas.
    if not uno(db,'''SELECT 1 FROM venta v JOIN cliente c USING(id_cliente)
        WHERE id_venta=:id AND c.id_usuario=:u''',id=id,u=u.id_usuario):raise HTTPException(404,'Compra no encontrada.')
    v=venta_bloqueada(db,id)
    previo=uno(db,'SELECT estado FROM solicitud_reembolso WHERE id_venta=:id',id=id)
    if previo:return {'mensaje':'La solicitud ya fue registrada. Estado: '+previo['estado']+'.'}
    if v['estado_venta']!='Pagada' or v['estado_entrega']=='Entregada':
        raise HTTPException(409,'Solo puedes solicitar el reembolso de una compra pagada y aún no entregada.')
    db.execute(text('INSERT INTO solicitud_reembolso(id_venta,motivo,solicitado_por) VALUES(:id,:m,:u)'),{'id':id,'m':datos.motivo,'u':u.id_usuario})
    db.execute(text("INSERT INTO historial_venta(id_venta,id_usuario,accion) VALUES(:id,:u,'Reembolso solicitado')"),{'id':id,'u':u.id_usuario})
    db.commit();return {'mensaje':'Solicitud registrada. Un administrador debe revisarla.'}

@router.post('/gestion/ventas/{id}/reembolso/aprobar',dependencies=[Depends(requerir_rol('administrador'))])
def aprobar(id:int,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    procesar(db,id,u.id_usuario);return {'mensaje':'Reembolso consultado en Stripe. Revisa el estado actualizado.'}

@router.post('/gestion/ventas/{id}/reembolso/sincronizar',dependencies=[Depends(requerir_rol('administrador'))])
def actualizar(id:int,db:Session=Depends(obtener_sesion)):
    procesar(db,id);return {'mensaje':'Estado de reembolso actualizado desde Stripe.'}

@router.post('/gestion/ventas/{id}/reembolso/rechazar',dependencies=[Depends(requerir_rol('administrador'))])
def rechazar(id:int,datos:Motivo,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    venta_bloqueada(db,id)
    r=uno(db,'SELECT * FROM solicitud_reembolso WHERE id_venta=:id FOR UPDATE',id=id)
    if not r:raise HTTPException(404,'Solicitud inexistente.')
    if r['estado']=='Rechazado':return {'mensaje':'La solicitud ya estaba rechazada.'}
    if r['estado']!='Solicitado':raise HTTPException(409,'El reembolso ya fue enviado a Stripe y no puede rechazarse aquí.')
    db.execute(text("""UPDATE solicitud_reembolso SET estado='Rechazado',resolucion=:m,resuelto_por=:u,
        actualizado=now() WHERE id_venta=:id"""),{'id':id,'m':datos.motivo,'u':u.id_usuario})
    db.execute(text("INSERT INTO historial_venta(id_venta,id_usuario,accion) VALUES(:id,:u,'Reembolso rechazado')"),{'id':id,'u':u.id_usuario})
    db.commit();return {'mensaje':'Solicitud rechazada y motivo guardado.'}
