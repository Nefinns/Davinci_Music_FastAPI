"""Datos 100 % ficticios para demostrar operaciones de la unidad 5."""
from datetime import date, datetime, timedelta
from sqlalchemy import text


def insert(conn, table, values, key):
    cols = ', '.join(values)
    placeholders = ', '.join(':' + col for col in values)
    return conn.execute(text(f'INSERT INTO {table} ({cols}) VALUES ({placeholders}) RETURNING {key}'), values).scalar_one()


def seed_demo(conn):
    today = date.today()
    people = [
        ('Ana','Morales'), ('Bruno','Méndez'), ('Carla','Ríos'), ('Diego','Salas'),
        ('Elena','Vega'), ('Fabio','León'), ('Gabriela','Solís'), ('Hugo','Cruz'),
        ('Inés','Robles'), ('Jorge','Molina'), ('Karen','Díaz'), ('Luis','Soto'),
        ('María','Pérez'), ('Nora','Navarro'), ('Óscar','Romero'), ('Paula','Cano'),
        ('Raúl','Aguilar'), ('Sofía','Gil'), ('Tomás','Luna'), ('Úrsula','Silva'),
        ('Valeria','Campos'), ('Walter','Núñez'), ('Ximena','Reyes'), ('Yahir','Flores')]
    users=[]
    for k, (name, lastname) in enumerate(people, 1):
        user=insert(conn,'usuario',{
            'nombre_usuario':f'u5_demo_{k:02d}', 'nombre': name,
            'apellido_paterno': lastname,'fecha_nacimiento': date(1990+(k%12), 1+(k%12), 1+(k%27)),
            'curp':f'FICTICIO_U5_{k:04d}', 'correo':f'demo{k:02d}@example.invalid',
            'contrasena_hash':'NO_UTILIZABLE_SOLO_PRACTICA_U5',
            'fecha_registro':datetime.combine(today-timedelta(days=k*2), datetime.min.time()),
            'activo': k != 24
        },'id_usuario')
        users.append(user)
    clients = [insert(conn,'cliente',{'id_usuario':u, 'fecha_alta':today-timedelta(days=i*3+10)},'id_cliente') for i,u in enumerate(users[:13])]
    teachers = [insert(conn,'maestro',{'id_usuario':u,'especialidad':sp,'fecha_contratacion':today-timedelta(days=220+i*17)},'id_maestro')
                for i,(u,sp) in enumerate(zip(users[13:19], ['Guitarra','Piano','Batería','Violín','Bajo','Flauta']))]
    admins = [insert(conn,'administrador',{'id_usuario':u,'fecha_contratacion':today-timedelta(days=410)},'id_administrador') for u in users[19:21]]
    periods=[]
    for i,(name,a,b,status) in enumerate([
        ('2026-A',-210,-92,'Finalizado'),('2026-B',-70,90,'Activo'),
        ('2027-A',91,255,'Planeado')]):
        periods.append(insert(conn,'periodo_academico',{'nombre_periodo':name,'fecha_inicio':today+timedelta(days=a),'fecha_fin':today+timedelta(days=b),'estado':status},'id_periodo'))
    cat_names=['Cuerdas','Teclados','Percusión','Viento','Bajos','Arco','Electrónicos','Accesorios']
    categories=[insert(conn,'categoria_instrumento',{'nombre_categoria':name,'descripcion':'Categoría ficticia para la unidad 5'},'id_categoria') for name in cat_names]
    inventory=[
       ('Guitarra acústica','Yamaha','F310',0,3200,12),('Guitarra eléctrica','Fender','Squier',0,5700,8),
       ('Guitarra clásica','Yamaha','C40',0,2850,5),('Ukulele concierto','Kala','KA-C',0,2100,2),
       ('Piano digital','Yamaha','P45',1,12800,4),('Teclado portátil','Casio','CT-S1',1,3600,10),
       ('Batería acústica','Pearl','Roadshow',2,14500,3),('Cajón peruano','Meinl','HCAJ',2,1900,0),
       ('Bongos','Meinl','HB100',2,2350,7),('Flauta traversa','Yamaha','YFL222',3,10400,2),
       ('Saxofón alto','Jupiter','JAS700',3,18900,1),('Clarinete','Yamaha','YCL255',3,14900,3),
       ('Bajo eléctrico','Ibanez','GSR200',4,6500,6),('Bajo de cinco cuerdas','Ibanez','SR305',4,9800,2),
       ('Violín 4/4','Stentor','Student',5,4200,9),('Viola','Stentor','Student II',5,5700,0),
       ('Sintetizador','Roland','JUNO-DS',6,23900,2),('Controlador MIDI','Akai','MPK Mini',6,3150,15)]
    instruments=[]
    for name,brand,model,cat,price,stock in inventory:
        instruments.append(insert(conn,'instrumento',{
            'id_categoria':categories[cat], 'nombre_instrumento':name,'marca':brand,'modelo':model,
            'precio_venta':price,'stock_actual':stock,'activo':True},'id_instrumento'))
    courses=[
        ('Guitarra inicial',0,0,'Principiante',2,650),('Piano básico',1,4,'Principiante',5,780),
        ('Ritmos de batería',2,6,'Intermedio',4,850),('Violín esencial',3,14,'Principiante',4,700),
        ('Bajo moderno',4,12,'Intermedio',4,760),('Flauta para todos',5,9,'Principiante',5,620),
        ('Guitarra avanzada',0,1,'Avanzado',3,950),('Piano intermedio',1,4,'Intermedio',5,890),
        ('Percusión latina',2,7,'Principiante',4,690),('Iniciación musical',1,5,'Principiante',7,500)]
    classes=[]
    for k,(name,maestro,instr,level,cap,price) in enumerate(courses):
        classes.append(insert(conn,'clase',{
            'id_maestro':teachers[maestro],'id_instrumento':instruments[instr],
            'id_periodo':periods[1 if k < 8 else 2], 'nombre_clase':name, 'nivel':level,
            'costo_mensual':price,'cupo_maximo':cap,'activa':True},'id_clase'))
        for d in range(2 if k%3 == 0 else 1):
            insert(conn,'horario_clase',{
                'id_clase':classes[k],'dia_semana':['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'][(k+d)%6],
                'hora_inicio':f'{10+(k%7):02d}:00:00','hora_fin':f'{11+(k%7):02d}:00:00','salon':f'A-{1+k%4}'
            },'id_horario')
    enroll=[]
    for k,course in enumerate(classes):
        n=2 if k in (0,1,2,3,4,5,6) else 1
        for j in range(n):
            enroll.append(insert(conn,'inscripcion_clase',{
                'id_cliente':clients[(k*2+j)%len(clients)],'id_clase':course,
                'fecha_inscripcion':today-timedelta(days=40+k),
                'costo_mensual_acordado':courses[k][5], 'estado_inscripcion':'Activa'
            },'id_inscripcion'))
    for k,enroll_id in enumerate(enroll):
        for mes in range(2):
            paid=(k+mes)%3 != 0
            insert(conn,'pago_clase',{
                'id_inscripcion':enroll_id,'periodo_pagado':today.replace(day=1)-timedelta(days=30*mes),
                'importe':courses[(k if k < 10 else (k-3))%len(courses)][5],
                'fecha_vencimiento':today-timedelta(days=15*mes-7),
                'fecha_pago':datetime.combine(today-timedelta(days=3+mes*20), datetime.min.time()) if paid else None,
                'metodo_pago':'Tarjeta' if paid else None,'estado_pago':'Pagado' if paid else 'Pendiente'
            },'id_pago_clase')
    for k in range(14):
        sale=insert(conn,'venta',{
            'id_cliente':clients[k%len(clients)], 'id_administrador':admins[k%len(admins)],
            'fecha_venta':datetime.combine(today-timedelta(days=5*k), datetime.min.time()),
            'metodo_pago':['Tarjeta','Efectivo','Transferencia'][k%3],
            'estado_venta':'Completada' if k != 13 else 'Cancelada'
        },'id_venta')
        for j in range(2):
            instr_index=(k+j*4)%15
            conn.execute(text('''INSERT INTO detalle_venta(id_venta,id_instrumento,cantidad,precio_unitario)
                VALUES (:v,:i,:c,:p)'''),{
                'v':sale,'i':instruments[instr_index],'c':1+k%2,'p':inventory[instr_index][4]
            })
    providers=[]
    for i,name in enumerate(['Música Distribución','Casa de Cuerdas','Teclados Global','Percusiones Centro','Importadora Armonía']):
        providers.append(insert(conn,'proveedor',{
            'nombre_proveedor':name,'rfc':f'U5DEMO{i:07d}',
            'correo':f'proveedor{i}@example.invalid','activo':True
        },'id_proveedor'))
    for k in range(8):
        order=insert(conn,'orden_abastecimiento',{
            'id_proveedor':providers[k%5], 'id_administrador':admins[k%2],
            'fecha_orden':datetime.combine(today-timedelta(days=6*k), datetime.min.time()),
            'estado_orden':['Pendiente','Parcial','Recibida'][k%3]
        },'id_orden')
        for j in range(2):
            idx=(k*2+j)%len(instruments)
            conn.execute(text('''INSERT INTO detalle_orden(id_orden,id_instrumento,cantidad_solicitada,cantidad_recibida,costo_unitario)
                VALUES (:o,:i,:sol,:rec,:cost)'''), {
                'o':order,'i':instruments[idx],'sol':8+j,'rec':(0 if k%3 == 0 else 3+j),
                'cost':inventory[idx][4]*0.65
            })
    return {'usuarios':len(users),'clientes':len(clients),'maestros':len(teachers),'instrumentos':len(instruments),
            'clases':len(classes),'inscripciones':len(enroll),'pagos':len(enroll)*2,'ventas':14,'proveedores':len(providers),'ordenes':8}
