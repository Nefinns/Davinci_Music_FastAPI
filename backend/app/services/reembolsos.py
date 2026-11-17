"""Reembolso total de ventas web no entregadas; Stripe es la autoridad del pago."""
from fastapi import HTTPException
from sqlalchemy import text
from app.api.routes.escuela import uno, filas
from app.services.pagos_checkout import stripe_api

BLOQUEA = ('Solicitado','Procesando','Pendiente','RequiereAccion','Reembolsado')

def venta_bloqueada(db,id):
    v=uno(db,'''SELECT v.*,cc.stripe_session_id,cc.total_centavos FROM venta v
      JOIN compra_checkout cc USING(id_venta) WHERE v.id_venta=:id FOR UPDATE OF v''',id=id)
    if not v:raise HTTPException(404,'Compra web no encontrada.')
    return v

def aplicar(db,v,r,refund):
    if (refund.get('payment_intent')!=r['payment_intent'] or refund.get('amount')!=v['total_centavos']
        or refund.get('currency')!='mxn' or refund.get('metadata',{}).get('id_venta')!=str(v['id_venta'])):
        raise HTTPException(409,'El reembolso no corresponde al importe y pago de esta venta.')
    if r['stripe_refund_id'] and r['stripe_refund_id']!=refund['id']:
        raise HTTPException(409,'Referencia de reembolso inesperada.')
    # Consulta actual al proveedor; un evento viejo nunca revierte un éxito local.
    if r['estado']=='Reembolsado':return
    estados={'succeeded':'Reembolsado','pending':'Pendiente','requires_action':'RequiereAccion',
             'failed':'Fallido','canceled':'Fallido'}
    e=estados.get(refund.get('status'))
    if not e:raise HTTPException(409,'Estado de reembolso desconocido. Revisa Stripe.')
    if e=='Reembolsado':
        if v['estado_entrega']=='Entregada':raise HTTPException(409,'El pedido ya fue entregado; requiere revisión manual.')
        if not r['stock_devuelto']:
            for d in filas(db,'SELECT * FROM detalle_venta WHERE id_venta=:id ORDER BY id_instrumento',id=v['id_venta']):
                db.execute(text('UPDATE instrumento SET stock_actual=stock_actual+:n WHERE id_instrumento=:i'),{'n':d['cantidad'],'i':d['id_instrumento']})
        db.execute(text("UPDATE venta SET estado_venta='Reembolsada' WHERE id_venta=:id"),{'id':v['id_venta']})
    db.execute(text('''UPDATE solicitud_reembolso SET estado=:e,stripe_refund_id=:re,
       stock_devuelto=stock_devuelto OR :devuelto,actualizado=now() WHERE id_venta=:id'''),
       {'e':e,'re':refund['id'],'devuelto':e=='Reembolsado','id':v['id_venta']})

def procesar(db,id,autor=None):
    v=venta_bloqueada(db,id)
    r=uno(db,'SELECT * FROM solicitud_reembolso WHERE id_venta=:id FOR UPDATE',id=id)
    if not r:raise HTTPException(404,'No hay solicitud de reembolso.')
    if r['estado'] in ('Reembolsado','Rechazado'):return
    if r['estado']=='Solicitado':
        if autor is None:raise HTTPException(409,'Un administrador debe aprobar la solicitud.')
        if v['estado_entrega']=='Entregada' or v['estado_venta']!='Pagada':
            raise HTTPException(409,'Solo se reembolsan compras web pagadas y aún no entregadas.')
        s=stripe_api('GET','checkout/sessions/'+v['stripe_session_id'])
        if (s.get('livemode') is not False or s.get('payment_status')!='paid' or
            s.get('metadata',{}).get('id_venta')!=str(id) or s.get('amount_total')!=v['total_centavos'] or s.get('currency')!='mxn'
            or not s.get('payment_intent')):
            raise HTTPException(409,'No se pudo verificar el pago original en Stripe.')
        db.execute(text("""UPDATE solicitud_reembolso SET estado='Procesando',payment_intent=:pi,
          resuelto_por=:u,actualizado=now() WHERE id_venta=:id"""),{'id':id,'pi':s['payment_intent'],'u':autor})
        db.execute(text("INSERT INTO historial_venta(id_venta,id_usuario,accion) VALUES(:id,:u,'Reembolso aprobado')"),{'id':id,'u':autor})
        # Antes del POST remoto: mantener bloqueo de entrega incluso si Stripe acepta y se pierde la respuesta.
        db.commit()
        v=venta_bloqueada(db,id)
        r=uno(db,'SELECT * FROM solicitud_reembolso WHERE id_venta=:id FOR UPDATE',id=id)
    if r['stripe_refund_id']:
        refund=stripe_api('GET','refunds/'+r['stripe_refund_id'])
    else:
        # Recuperar respuesta perdida incluso tras expirar la clave de idempotencia de Stripe.
        pi=r['payment_intent']
        if not pi or not pi.startswith('pi_'):raise HTTPException(409,'Referencia del pago no disponible.')
        lista=stripe_api('GET','refunds?payment_intent='+pi+'&limit=100')
        if lista.get('has_more'):raise HTTPException(409,'Este pago requiere revisión manual en Stripe.')
        existentes=lista.get('data',[])
        propios=[x for x in existentes if x.get('metadata',{}).get('id_venta')==str(id)]
        if len(propios)>1 or any(x not in propios for x in existentes):
            raise HTTPException(409,'Hay reembolsos externos. Revisa el pago en Stripe antes de continuar.')
        if propios:refund=propios[0]
        else:
            refund=stripe_api('POST','refunds',{'payment_intent':pi,'amount':str(v['total_centavos']),
                'reason':'requested_by_customer','metadata[id_venta]':str(id)},'davinci-reembolso-'+str(id))
    aplicar(db,v,r,refund)
    db.commit()
