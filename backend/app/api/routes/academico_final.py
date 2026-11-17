from uuid import uuid4
from datetime import date,datetime,time,timezone
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import Field
from sqlalchemy import text
from sqlmodel import Session
from app.api.routes.escuela import uno,filas,Datos
from app.core.dependencies import obtener_usuario_actual,requerir_rol,obtener_roles_usuario
from app.db.session import obtener_sesion
from app.models.usuario import Usuario
from app.core.config import FRONTEND_URL
from app.services.pagos_checkout import stripe_api,configuracion
from app.services.mensualidades import sincronizar
router=APIRouter(tags=['Mensualidades y asistencia'])

def acceso(db,id,u,roles):
    x=uno(db,'''SELECT x.*,cl.id_usuario,c.nombre_clase,c.activa,m.id_usuario AS docente,p.fecha_fin,p.estado AS periodo_estado
      FROM inscripcion_clase x JOIN cliente cl USING(id_cliente) JOIN clase c USING(id_clase)
      JOIN maestro m USING(id_maestro) JOIN periodo_academico p USING(id_periodo) WHERE x.id_inscripcion=:id FOR UPDATE OF x''',id=id)
    if not x or (x['id_usuario']!=u.id_usuario and 'administrador' not in roles):raise HTTPException(404,'Inscripción no encontrada.')
    return x

@router.get('/mensualidades/mias')
def mias(u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    xs=filas(db,'''SELECT x.*,c.nombre_clase,s.estado AS suscripcion,s.cancelar,s.fin
      FROM inscripcion_clase x JOIN cliente cl USING(id_cliente) JOIN clase c USING(id_clase)
      LEFT JOIN suscripcion_escuela s USING(id_inscripcion) WHERE cl.id_usuario=:u ORDER BY x.id_inscripcion DESC''',u=u.id_usuario)
    for x in xs:
        x['pagos']=filas(db,'''SELECT p.*,f.url FROM pago_clase p LEFT JOIN factura_escuela f USING(id_pago_clase)
          WHERE p.id_inscripcion=:i ORDER BY p.periodo_pagado DESC''',i=x['id_inscripcion'])
    return xs

@router.post('/mensualidades/{id}/iniciar',dependencies=[Depends(requerir_rol('cliente'))])
def iniciar(id:int,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    configuracion();x=acceso(db,id,u,[])
    if x['docente']==u.id_usuario:raise HTTPException(409,'Eres el profesor del grupo. Revisa la inscripción anterior con un administrador.')
    if x['estado_inscripcion']!='Activa' or not x['activa'] or x['periodo_estado']!='Abierto' or x['fecha_fin']<date.today():raise HTTPException(409,'Inscripción o clase no disponible.')
    r=uno(db,'SELECT * FROM suscripcion_escuela WHERE id_inscripcion=:id',id=id)
    if not r:
        importe=int(x['costo_mensual_acordado']*100)
        if importe<1000 or importe>99999999:raise HTTPException(422,'La mensualidad debe estar entre $10 y $999,999.99 MXN.')
        db.execute(text('INSERT INTO suscripcion_escuela(id_inscripcion,solicitud,centavos,nombre,fin_ciclo) VALUES(:i,:s,:c,:n,:fin)'),{'i':id,'s':str(uuid4()),'c':importe,'n':x['nombre_clase'],'fin':int(datetime.combine(x['fecha_fin'],time(23,59),tzinfo=timezone.utc).timestamp())})
        db.commit();x=acceso(db,id,u,[]);r=uno(db,'SELECT * FROM suscripcion_escuela WHERE id_inscripcion=:id',id=id)
    if r['stripe_session_id']:
        s=stripe_api('GET','checkout/sessions/'+r['stripe_session_id'])
        sincronizar(db,id);db.commit()
        if s.get('status')!='open':raise HTTPException(409,'Checkout finalizado o expirado. Consulta la suscripción; para reiniciar una cancelada solicita nueva inscripción.')
        return {'url':s['url']}
    s=stripe_api('POST','checkout/sessions',{
      'mode':'subscription','payment_method_types[0]':'card','client_reference_id':str(id),
      'metadata[id_inscripcion]':str(id),'subscription_data[metadata][id_inscripcion]':str(id),
      'subscription_data[metadata][fin_ciclo]':str(r['fin_ciclo']),
      'success_url':FRONTEND_URL+'/mis-pagos','cancel_url':FRONTEND_URL+'/mis-pagos',
      'line_items[0][price_data][currency]':'mxn','line_items[0][price_data][unit_amount]':str(r['centavos']),
      'line_items[0][price_data][recurring][interval]':'month',
      'line_items[0][price_data][product_data][name]':r['nombre'],'line_items[0][quantity]':'1'
    },'escuela-'+str(r['solicitud']))
    db.execute(text('UPDATE suscripcion_escuela SET stripe_session_id=:s,estado=\'Checkout\' WHERE id_inscripcion=:id'),{'id':id,'s':s['id']})
    db.commit();return {'url':s['url']}

@router.post('/mensualidades/{id}/sincronizar')
def actualizar(id:int,u:Usuario=Depends(obtener_usuario_actual),roles:list=Depends(obtener_roles_usuario),db:Session=Depends(obtener_sesion)):
    acceso(db,id,u,roles);sincronizar(db,id);db.commit();return {'mensaje':'Mensualidades actualizadas desde Stripe.'}

@router.post('/mensualidades/{id}/cancelar')
def cancelar(id:int,u:Usuario=Depends(obtener_usuario_actual),roles:list=Depends(obtener_roles_usuario),db:Session=Depends(obtener_sesion)):
    acceso(db,id,u,roles);sincronizar(db,id)
    r=uno(db,'SELECT * FROM suscripcion_escuela WHERE id_inscripcion=:id FOR UPDATE',id=id)
    if r and not r['stripe_session_id']:
        raise HTTPException(409,'La creación del Checkout quedó pendiente. El alumno debe pulsar Continuar mensualidad antes de detener los cobros.')
    if r and r['stripe_subscription_id']:
        if r['estado']!='canceled':stripe_api('DELETE','subscriptions/'+r['stripe_subscription_id'],{'invoice_now':'false','prorate':'false'})
        sincronizar(db,id)
    elif r and r['stripe_session_id']:
        s=stripe_api('GET','checkout/sessions/'+r['stripe_session_id'])
        if s['status']=='open':stripe_api('POST','checkout/sessions/'+s['id']+'/expire')
        sincronizar(db,id)
        # Resolver también el caso de pago completado mientras se cancelaba.
        r=uno(db,'SELECT * FROM suscripcion_escuela WHERE id_inscripcion=:id',id=id)
        if r['stripe_subscription_id']:
            stripe_api('DELETE','subscriptions/'+r['stripe_subscription_id'],{'invoice_now':'false','prorate':'false'});sincronizar(db,id)
    db.commit();return {'mensaje':'Cobro recurrente detenido. No se devuelve lo ya pagado; la baja académica la registra el administrador.'}

@router.get('/docencia/{id}/alumnos',dependencies=[Depends(requerir_rol('maestro'))])
def alumnos(id:int,fecha:date,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    if not uno(db,'SELECT 1 FROM clase c JOIN maestro m USING(id_maestro) WHERE c.id_clase=:i AND m.id_usuario=:u AND m.activo',i=id,u=u.id_usuario):raise HTTPException(404,'Grupo no encontrado.')
    return filas(db,'''SELECT x.id_inscripcion,u.nombre||' '||u.apellido_paterno||' '||COALESCE(u.apellido_materno,'') AS alumno,
      a.estado FROM inscripcion_clase x JOIN cliente cl USING(id_cliente) JOIN usuario u USING(id_usuario)
      LEFT JOIN asistencia_clase a ON a.id_inscripcion=x.id_inscripcion AND a.fecha=:f
      WHERE x.id_clase=:i AND x.estado_inscripcion='Activa' ORDER BY alumno''',i=id,f=fecha)

class MarcaAsistencia(Datos):
    id_inscripcion:int=Field(gt=0)
    estado:Literal['Presente','Ausente','Justificada']

class Asistencia(Datos):
    fecha:date
    alumnos:list[MarcaAsistencia] = Field(max_length=100)

@router.put('/docencia/{id}/asistencia',dependencies=[Depends(requerir_rol('maestro'))])
def asistencia(id:int,datos:Asistencia,u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    from datetime import timedelta
    c=uno(db,'''SELECT c.*,p.fecha_inicio,p.fecha_fin FROM clase c JOIN maestro m USING(id_maestro)
       JOIN periodo_academico p USING(id_periodo) WHERE c.id_clase=:i AND m.id_usuario=:u AND m.activo FOR UPDATE OF c''',i=id,u=u.id_usuario)
    if not c:raise HTTPException(404,'Grupo no encontrado.')
    if not c['activa'] or not c['fecha_inicio']<=datos.fecha<=min(date.today(),c['fecha_fin']):raise HTTPException(422,'Fecha fuera del periodo o futura.')
    dias=['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
    if not uno(db,'SELECT 1 FROM horario_clase WHERE id_clase=:i AND dia_semana=:d',i=id,d=dias[datos.fecha.weekday()]):raise HTTPException(422,'El grupo no tiene clase ese día.')
    marcas=[a.model_dump() for a in datos.alumnos]
    ids=[a.get('id_inscripcion') for a in marcas]
    if len(ids)!=len(set(ids)):raise HTTPException(422,'Alumno repetido.')
    for a in marcas:
        if set(a)!={'id_inscripcion','estado'} or type(a['id_inscripcion']) is not int or a['estado'] not in ('Presente','Ausente','Justificada'):raise HTTPException(422,'Registro de asistencia inválido.')
        if not uno(db,"SELECT 1 FROM inscripcion_clase WHERE id_inscripcion=:i AND id_clase=:c AND estado_inscripcion='Activa' AND fecha_inscripcion<=:f",i=a['id_inscripcion'],c=id,f=datos.fecha):raise HTTPException(409,'Alumno no inscrito para esa fecha.')
        db.execute(text('''INSERT INTO asistencia_clase(id_inscripcion,fecha,estado,registrado_por) VALUES(:i,:f,:e,:u)
         ON CONFLICT(id_inscripcion,fecha) DO UPDATE SET estado=EXCLUDED.estado,registrado_por=EXCLUDED.registrado_por,actualizado=now()'''),{'i':a['id_inscripcion'],'f':datos.fecha,'e':a['estado'],'u':u.id_usuario})
    db.commit();return {'mensaje':'Asistencia guardada.'}

@router.get('/asistencia/mia')
def propia(u:Usuario=Depends(obtener_usuario_actual),db:Session=Depends(obtener_sesion)):
    return filas(db,'''SELECT a.fecha,a.estado,c.nombre_clase FROM asistencia_clase a JOIN inscripcion_clase x USING(id_inscripcion)
     JOIN clase c USING(id_clase) JOIN cliente cl USING(id_cliente) WHERE cl.id_usuario=:u ORDER BY a.fecha DESC LIMIT 200''',u=u.id_usuario)

@router.get('/mensualidades/administracion',dependencies=[Depends(requerir_rol('administrador'))])
def administracion(db:Session=Depends(obtener_sesion)):
    xs=filas(db,'''SELECT x.*,c.nombre_clase,u.nombre||' '||u.apellido_paterno AS alumno,s.estado AS suscripcion,s.cancelar,s.fin
      FROM inscripcion_clase x JOIN cliente cl USING(id_cliente) JOIN usuario u USING(id_usuario) JOIN clase c USING(id_clase)
      LEFT JOIN suscripcion_escuela s USING(id_inscripcion) ORDER BY x.id_inscripcion DESC LIMIT 200''')
    for x in xs:
        x['pagos']=filas(db,'''SELECT p.*,f.url FROM pago_clase p LEFT JOIN factura_escuela f USING(id_pago_clase)
           WHERE p.id_inscripcion=:i ORDER BY periodo_pagado DESC''',i=x['id_inscripcion'])
    return xs
