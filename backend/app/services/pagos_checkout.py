"""Stripe REST: una sola moneda, tarjetas y entorno de prueba."""
import hashlib
import hmac
import json
import os
import time
import requests
from fastapi import HTTPException

API_VERSION = '2025-02-24.acacia'

def configuracion():
    clave=os.getenv('STRIPE_SECRET_KEY','').strip()
    if not clave.startswith('sk_test_'):
        raise HTTPException(503,'Configura Stripe con una clave sk_test_ para habilitar las compras de prueba.')
    return clave

def stripe_api(metodo,ruta,datos=None,clave_idempotencia=None):
    headers={'Authorization':'Bearer '+configuracion(),'Stripe-Version':API_VERSION}
    if clave_idempotencia:headers['Idempotency-Key']=clave_idempotencia
    try:
        r=requests.request(metodo,'https://api.stripe.com/v1/'+ruta,headers=headers,data=datos,timeout=20)
        if not r.ok:raise HTTPException(503,'El proveedor no pudo completar la operación. Reintenta desde Mis compras.')
        return r.json()
    except (requests.RequestException,ValueError):
        raise HTTPException(503,'No se pudo contactar con Stripe. La compra pendiente se conserva; reintenta desde Mis compras.') from None

def verificar_evento(body:bytes,firma:str):
    secret=os.getenv('STRIPE_WEBHOOK_SECRET','').strip()
    if not secret:raise HTTPException(503,'Webhook de pagos no configurado.')
    try:
        partes=[x.split('=',1) for x in firma.split(',')]
        ts=next(v for k,v in partes if k=='t')
        if abs(time.time()-int(ts))>300:raise ValueError()
        esperado=hmac.new(secret.encode(),ts.encode()+b'.'+body,hashlib.sha256).hexdigest()
        if not any(k=='v1' and hmac.compare_digest(v,esperado) for k,v in partes):raise ValueError()
        evento=json.loads(body)
        if evento.get('livemode') is not False:raise ValueError()
        return evento
    except (ValueError,StopIteration,TypeError):
        raise HTTPException(400,'Firma o evento de pago inválido.') from None
