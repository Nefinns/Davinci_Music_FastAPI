"""Compras: reserva transaccional, Checkout alojado y conciliación idempotente."""
from uuid import UUID
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import text
from sqlmodel import Session
from app.core.config import FRONTEND_URL
from app.core.dependencies import obtener_usuario_actual, requerir_rol
from app.db.session import obtener_sesion
from app.models.usuario import Usuario
from app.services.pagos_checkout import stripe_api, verificar_evento, configuracion
from app.api.routes.escuela import uno, filas

router=APIRouter(prefix='/compras',tags=['Compras'])

class Linea(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id_instrumento:int=Field(gt=0)
    cantidad:int=Field(ge=1,le=20)

class Carrito(BaseModel):
    model_config=ConfigDict(extra='forbid')
    solicitud:UUID
    items:list[Linea]=Field(min_length=1,max_length=30)

def propia(db,id,u):
    r=uno(db,'''SELECT v.*,cc.solicitud,cc.stripe_session_id,cc.checkout_url,cc.items_json,cc.total_centavos
      FROM venta v JOIN compra_checkout cc USING(id_venta) JOIN cliente c USING(id_cliente)
      WHERE v.id_venta=:id AND c.id_usuario=:u FOR UPDATE OF v''',id=id,u=u.id_usuario)
    if not r:raise HTTPException(404,'Compra no encontrada.')
    return r

def abrir_checkout(db,v):
    if v['stripe_session_id']:return stripe_api('GET','checkout/sessions/'+v['stripe_session_id'])
    items=v['items_json']
    d={'mode':'payment','payment_method_types[0]':'card',
       'success_url':FRONTEND_URL+'/mis-compras?resultado=retorno',
       'cancel_url':FRONTEND_URL+'/mis-compras?resultado=cancelado',
       'metadata[id_venta]':str(v['id_venta']),'client_reference_id':str(v['id_venta'])}
    for j,x in enumerate(items):
        pref=f'line_items[{j}]'
        d.update({pref+'[price_data][currency]':'mxn',pref+'[price_data][unit_amount]':str(x['centavos']),
          pref+'[price_data][product_data][name]':x['nombre_instrumento'],pref+'[quantity]':str(x['cantidad'])})
    s=stripe_api('POST','checkout/sessions',d,'davinci-'+str(v['solicitud']))
    db.execute(text('UPDATE compra_checkout SET stripe_session_id=:sid,checkout_url=:url WHERE id_venta=:id'),{'id':v['id_venta'],'sid':s['id'],'url':s.get('url')})
    return s

def conciliar(db,v,s):
    if s.get('livemode') is not False or s.get('metadata',{}).get('id_venta')!=str(v['id_venta']):
        raise HTTPException(409,'La sesión de pago no corresponde a esta compra.')
    if v['estado_venta']!='Pendiente':return
    if s.get('payment_status')=='paid':
        if s.get('currency')!='mxn' or s.get('amount_total')!=v['total_centavos']:
            raise HTTPException(409,'El importe de pago no coincide con la compra.')
        db.execute(text("UPDATE venta SET estado_venta='Pagada' WHERE id_venta=:id"),{'id':v['id_venta']})
    elif s.get('status')=='expired':
        # La reserva ya descontó disponibilidad; devolver una sola vez bajo bloqueo de venta.
        for d in filas(db,'SELECT * FROM detalle_venta WHERE id_venta=:id ORDER BY id_instrumento',id=v['id_venta']):
            db.execute(text('UPDATE instrumento SET stock_actual=stock_actual+:n WHERE id_instrumento=:i'),{'n':d['cantidad'],'i':d['id_instrumento']})
        db.execute(text("UPDATE venta SET estado_venta='Cancelada' WHERE id_venta=:id"),{'id':v['id_venta']})

@router.post('/checkout',dependencies=[Depends(requerir_rol('cliente'))])
def iniciar(datos:Carrito,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    configuracion()
    ids=[x.id_instrumento for x in datos.items]
    if len(ids)!=len(set(ids)):raise HTTPException(422,'Instrumentos repetidos en el carrito.')
    # Serializa inicios por cliente. Otro cliente nunca puede recuperar una solicitud ajena.
    db.execute(text('SELECT pg_advisory_xact_lock(7363,:u)'),{'u':u.id_usuario})
    cl=uno(db,'SELECT id_cliente FROM cliente WHERE id_usuario=:u',u=u.id_usuario)
    if not cl:raise HTTPException(409,'Se necesita un perfil de cliente para comprar.')
    previo=uno(db,'SELECT v.* FROM compra_checkout cc JOIN venta v USING(id_venta) WHERE cc.solicitud=:s',s=str(datos.solicitud))
    if previo and previo['id_cliente']!=cl['id_cliente']:raise HTTPException(409,'Solicitud de compra no disponible.')
    if previo and previo['estado_venta']!='Pendiente':raise HTTPException(409,'Esta solicitud ya fue procesada. Revisa Mis compras.')
    if not previo:
        previo=uno(db,"SELECT v.* FROM venta v JOIN compra_checkout cc USING(id_venta) WHERE id_cliente=:cl AND estado_venta='Pendiente' LIMIT 1",cl=cl['id_cliente'])
        if previo:raise HTTPException(409,'Tienes una compra pendiente. Continúa o cancélala desde Mis compras antes de crear otra.')
        detalles=[];total=0
        for x in sorted(datos.items,key=lambda x:x.id_instrumento):
            i=uno(db,'SELECT * FROM instrumento WHERE id_instrumento=:id FOR UPDATE',id=x.id_instrumento)
            if not i or not i['activo'] or i['stock_actual']<x.cantidad or i['precio_venta']<=0:
                raise HTTPException(409,'Un artículo no está disponible o no tiene existencias suficientes. Revisa el catálogo.')
            total+=int(i['precio_venta']*100)*x.cantidad
            detalles.append((x,i))
        if total<1000 or total>99999999:
            raise HTTPException(422,'El total debe estar entre $10 y $999,999.99 MXN para este Checkout.')
        id=uno(db,"INSERT INTO venta(id_cliente,metodo_pago,estado_venta) VALUES(:cl,'Stripe prueba','Pendiente') RETURNING id_venta",cl=cl['id_cliente'])['id_venta']
        for x,i in detalles:
            db.execute(text('INSERT INTO detalle_venta(id_venta,id_instrumento,cantidad,precio_unitario) VALUES(:v,:i,:n,:p)'),{'v':id,'i':x.id_instrumento,'n':x.cantidad,'p':i['precio_venta']})
            db.execute(text('UPDATE instrumento SET stock_actual=stock_actual-:n WHERE id_instrumento=:i'),{'n':x.cantidad,'i':x.id_instrumento})
        db.execute(text('INSERT INTO compra_checkout(id_venta,solicitud,total_centavos,items_json) VALUES(:id,:s,:t,CAST(:items AS JSONB))'),{'id':id,'s':str(datos.solicitud),'t':total,'items':json.dumps([{'nombre_instrumento':i['nombre_instrumento'],'cantidad':x.cantidad,'centavos':int(i['precio_venta']*100)} for x,i in detalles])})
        # Reserva durable incluso ante timeout de Stripe. Reintentos reutilizan la misma clave.
        db.commit()
    else:id=previo['id_venta']
    v=propia(db,id,u);s=abrir_checkout(db,v);conciliar(db,v,s);db.commit()
    return {'id_venta':id,'url':s.get('url')}

@router.get('/mias')
def mias(u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    lista=filas(db,'''SELECT v.*,cc.total_centavos FROM venta v JOIN compra_checkout cc USING(id_venta)
      JOIN cliente c USING(id_cliente) WHERE c.id_usuario=:u ORDER BY v.id_venta DESC LIMIT 100''',u=u.id_usuario)
    for v in lista:
        v['reembolso']=dict(r) if (r:=uno(db,'SELECT estado,motivo,resolucion,stripe_refund_id,actualizado FROM solicitud_reembolso WHERE id_venta=:id',id=v['id_venta'])) else None
        v['detalles']=filas(db,'''SELECT d.*,i.nombre_instrumento FROM detalle_venta d JOIN instrumento i USING(id_instrumento) WHERE id_venta=:id''',id=v['id_venta'])
    return lista

@router.post('/{id}/sincronizar')
def sincronizar(id:int,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    v=propia(db,id,u)
    if v['estado_venta']=='Pendiente':s=abrir_checkout(db,v);conciliar(db,v,s)
    db.commit();return {'mensaje':'Estado actualizado.'}

@router.post('/{id}/continuar')
def continuar(id:int,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    v=propia(db,id,u)
    if v['estado_venta']!='Pendiente':raise HTTPException(409,'La compra ya no está pendiente.')
    s=abrir_checkout(db,v);conciliar(db,v,s);db.commit()
    return {'url':s.get('url'),'mensaje':'Consulta el estado actualizado.'}

@router.post('/{id}/cancelar')
def cancelar(id:int,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    v=propia(db,id,u)
    if v['estado_venta']=='Pendiente':
        s=abrir_checkout(db,v)
        if s['status']=='open':s=stripe_api('POST','checkout/sessions/'+s['id']+'/expire')
        conciliar(db,v,s)
    db.commit();return {'mensaje':'Estado actualizado. Una compra ya pagada no se cancela desde esta opción.'}

@router.post('/stripe/webhook')
async def webhook(request:Request,db:Session=Depends(obtener_sesion)):
    body=await request.body()
    if len(body)>1024*1024:raise HTTPException(413,'Evento demasiado grande.')
    evento=verificar_evento(body,request.headers.get('stripe-signature',''))
    # Facturas/suscripciones escolares se concilian por API; no interfieren con ventas.
    tipo=evento.get('type','');obj=evento.get('data',{}).get('object',{})
    escolar=(tipo.startswith('invoice.') or tipo.startswith('customer.subscription.') or
             (tipo.startswith('checkout.session.') and obj.get('metadata',{}).get('id_inscripcion')))
    if escolar:
        from app.services.mensualidades import sincronizar
        sid=(obj.get('subscription') or obj.get('parent',{}).get('subscription_details',{}).get('subscription')) if tipo.startswith('invoice.') else obj.get('id') if tipo.startswith('customer.subscription.') else None
        registro=uno(db,'SELECT id_inscripcion FROM suscripcion_escuela WHERE stripe_subscription_id=:sid',sid=sid) if sid else None
        id=registro['id_inscripcion'] if registro else obj.get('metadata',{}).get('id_inscripcion')
        if id and str(id).isdigit():
            if uno(db,'SELECT 1 FROM suscripcion_escuela WHERE id_inscripcion=:i',i=int(id)):
                sincronizar(db,int(id));db.commit()
        return {'recibido':True}
    if evento.get('type') in {'refund.created','refund.updated','refund.failed'}:
        from app.services.reembolsos import procesar
        refund=evento['data']['object']
        venta=refund.get('metadata',{}).get('id_venta','')
        if str(venta).isdigit():
            r=uno(db,'SELECT estado FROM solicitud_reembolso WHERE id_venta=:id',id=int(venta))
            if r and r['estado'] not in ('Solicitado','Rechazado'):
                # Leer el estado actual evita retroceder por eventos repetidos o desordenados.
                procesar(db,int(venta))
        return {'recibido':True}
    if evento.get('type') not in {'checkout.session.completed','checkout.session.expired'}:return {'recibido':True}
    s=evento['data']['object']
    id=s.get('metadata',{}).get('id_venta','')
    if not str(id).isdigit():return {'recibido':True}
    v=uno(db,'''SELECT v.*,cc.stripe_session_id,cc.total_centavos FROM venta v
      JOIN compra_checkout cc USING(id_venta) WHERE v.id_venta=:id FOR UPDATE OF v''',id=int(id))
    if not v:return {'recibido':True}
    if v['stripe_session_id']!=s['id']:
        # Puede llegar mientras aún se guarda la respuesta de creación: reintentar después.
        raise HTTPException(409,'La sesión todavía no está registrada; reintentar evento.')
    if uno(db,'SELECT 1 FROM evento_pago WHERE id_evento=:id',id=evento['id']):return {'recibido':True}
    conciliar(db,v,s)
    db.execute(text('INSERT INTO evento_pago(id_evento) VALUES(:id) ON CONFLICT DO NOTHING'),{'id':evento['id']})
    db.commit();return {'recibido':True}
