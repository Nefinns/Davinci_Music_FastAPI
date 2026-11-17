from decimal import Decimal
from datetime import datetime,timezone
from fastapi import HTTPException
from sqlalchemy import text
from app.api.routes.escuela import uno
from app.services.pagos_checkout import stripe_api

def fecha(ts):
    return datetime.fromtimestamp(ts,tz=timezone.utc)

def sincronizar(db,id):
    r=uno(db,'SELECT * FROM suscripcion_escuela WHERE id_inscripcion=:id FOR UPDATE',id=id)
    if not r:return
    sid=r['stripe_subscription_id']
    if not sid and r['stripe_session_id']:
        s=stripe_api('GET','checkout/sessions/'+r['stripe_session_id'])
        if s.get('livemode') is not False or s.get('metadata',{}).get('id_inscripcion')!=str(id):
            raise HTTPException(409,'La sesión no corresponde a esta inscripción.')
        sid=s.get('subscription')
        if not sid:
            if s.get('status')=='expired':
                db.execute(text("UPDATE suscripcion_escuela SET estado='Expirada',actualizado=now() WHERE id_inscripcion=:id"),{'id':id})
            return
    if not sid:return
    s=stripe_api('GET','subscriptions/'+sid)
    if s.get('livemode') is not False or s.get('metadata',{}).get('id_inscripcion')!=str(id):
        raise HTTPException(409,'Suscripción no válida para esta inscripción.')
    limite=s.get('metadata',{}).get('fin_ciclo')
    if limite and s['status'] not in ('canceled','incomplete_expired') and not s.get('cancel_at'):
        limite=int(limite)
        if limite>datetime.now(timezone.utc).timestamp():
            s=stripe_api('POST','subscriptions/'+sid,{'cancel_at':str(limite),'proration_behavior':'none'},'fin-ciclo-'+sid)
        else:
            s=stripe_api('DELETE','subscriptions/'+sid,{'invoice_now':'false','prorate':'false'})
    items=s.get('items',{}).get('data',[])
    if len(items)!=1 or items[0].get('price',{}).get('unit_amount')!=r['centavos'] or items[0].get('price',{}).get('currency')!='mxn' or items[0].get('quantity')!=1 or items[0].get('price',{}).get('recurring',{}).get('interval')!='month':
        raise HTTPException(409,'El precio de la suscripción no coincide con el acordado.')
    fin=s.get('current_period_end') or items[0].get('current_period_end')
    db.execute(text('''UPDATE suscripcion_escuela SET stripe_subscription_id=:sid,estado=:e,
        cancelar=:c,fin=:fin,actualizado=now() WHERE id_inscripcion=:id'''),
        {'id':id,'sid':sid,'e':s['status'],'c':s.get('cancel_at_period_end',False),'fin':fecha(fin) if fin else None})
    # Recuperar también eventos perdidos; todas las páginas, sin inventar pagos locales.
    cursor=''
    while True:
        pagina=stripe_api('GET','invoices?subscription='+sid+'&limit=100'+cursor)
        for f in pagina.get('data',[]):
            if f.get('status')=='draft':continue
            if f.get('livemode') is not False or f.get('subscription')!=sid or f.get('currency')!='mxn' or f.get('amount_due')!=r['centavos']:
                raise HTTPException(409,'Factura no compatible con el importe mensual acordado. Revisa Stripe.')
            if f.get('status') not in ('paid','open','uncollectible','void'):continue
            periodo=f.get('lines',{}).get('data',[])
            inicio=periodo[0].get('period',{}).get('start') if periodo else None
            if not inicio:raise HTTPException(409,'Factura sin periodo de servicio.')
            estado='Pagado' if f['status']=='paid' else 'Cancelado' if f['status']=='void' else 'Vencido' if s['status']=='past_due' or f['status']=='uncollectible' else 'Pendiente'
            if estado=='Pagado' and f.get('amount_paid')!=r['centavos']:raise HTTPException(409,'Importe pagado diferente al esperado.')
            pago=uno(db,'SELECT id_pago_clase FROM factura_escuela WHERE stripe_invoice_id=:f',f=f['id'])
            pagado=fecha(f['status_transitions']['paid_at']) if estado=='Pagado' and f.get('status_transitions',{}).get('paid_at') else None
            params={'i':id,'periodo':fecha(inicio).date(),'importe':Decimal(r['centavos'])/100,'vence':fecha(f.get('due_date') or inicio).date(),'pagado':pagado,'e':estado}
            if not pago:
                p=uno(db,'''INSERT INTO pago_clase(id_inscripcion,periodo_pagado,importe,fecha_vencimiento,fecha_pago,metodo_pago,estado_pago)
                  VALUES(:i,:periodo,:importe,:vence,:pagado,'Stripe prueba',:e) RETURNING id_pago_clase''',**params)['id_pago_clase']
                db.execute(text('INSERT INTO factura_escuela VALUES(:f,:p,:i,:url)'),{'f':f['id'],'p':p,'i':id,'url':f.get('hosted_invoice_url')})
            else:
                db.execute(text('UPDATE pago_clase SET estado_pago=:e,fecha_pago=:pagado WHERE id_pago_clase=:p'),{'p':pago['id_pago_clase'],'e':estado,'pagado':pagado})
                db.execute(text('UPDATE factura_escuela SET url=:url WHERE stripe_invoice_id=:f'),{'f':f['id'],'url':f.get('hosted_invoice_url')})
        if not pagina.get('has_more'):break
        if not pagina.get('data'):raise HTTPException(503,'No se pudo paginar las facturas.')
        cursor='&starting_after='+pagina['data'][-1]['id']
