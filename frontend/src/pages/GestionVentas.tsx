import { useEffect, useState, type FormEvent } from 'react'
import Marco from '@/components/MarcoOperaciones'
import { consultar, operar, dinero } from '@/services/operaciones'
import type { Venta } from '@/services/gestion'
const boton='rounded-lg border border-patina px-4 py-2 text-patina disabled:opacity-50'
const siguiente: Record<string,string>={'Por preparar':'Preparando','Preparando':'Lista para recoger','Lista para recoger':'Entregada'}
export default function GestionVentas() {
  const [pagina,setPagina]=useState({items:[] as Venta[],total:0}),[q,setQ]=useState(''),[estado,setEstado]=useState(''),[entrega,setEntrega]=useState(''),[filtro,setFiltro]=useState(''),[offset,setOffset]=useState(0)
  const [error,setError]=useState(''),[mensaje,setMensaje]=useState(''),[ocupado,setOcupado]=useState(false),[cargando,setCargando]=useState(true),[rechazo,setRechazo]=useState<number|null>(null),[motivo,setMotivo]=useState('')
  const ruta='/gestion/ventas?'+new URLSearchParams({q:filtro,estado,entrega,offset:String(offset)})
  useEffect(()=>{let vivo=true;void consultar<typeof pagina>(ruta).then(x=>{if(vivo){setPagina(x);setError('')}}).catch(e=>{if(vivo)setError(String(e))}).finally(()=>{if(vivo)setCargando(false)});return()=>{vivo=false}},[ruta])
  async function accion(v:Venta,tipo:string,datos?:unknown) {
    if(ocupado)return
    if(tipo==='reembolso/aprobar'&&!window.confirm(`¿Aprobar el reembolso TOTAL de ${dinero(v.total_centavos/100)} para la compra #${v.id_venta}? Se enviará a Stripe en modo de prueba.`))return
    if(tipo==='entrega'&&!window.confirm(`¿Cambiar la entrega a ${siguiente[v.estado_entrega]}?`))return
    setOcupado(true);setError('');setMensaje('')
    try {const r=await operar(`/gestion/ventas/${v.id_venta}/${tipo}`,datos);setMensaje(r.mensaje);setPagina(await consultar(ruta));setRechazo(null);setMotivo('')}
    catch(e){setError(String(e))}finally{setOcupado(false)}
  }
  function buscar(e:FormEvent){e.preventDefault();setFiltro(q.trim());setOffset(0)}
  return <Marco titulo="Pedidos y reembolsos"><p className="mb-5">Compras para recoger en tienda. El pago se confirma con Stripe; aquí gestionas la preparación, la entrega y los reembolsos solicitados.</p>
    <form onSubmit={buscar} className="mb-5 flex flex-wrap gap-3"><input aria-label="Buscar por folio, cliente o correo" placeholder="Nombre completo, correo o #folio" className="rounded-lg border bg-white p-3" value={q} onChange={e=>setQ(e.target.value)}/><button className={boton}>Buscar</button>
      <select aria-label="Estado de pago" className="rounded-lg border bg-white p-3" value={estado} onChange={e=>{setEstado(e.target.value);setOffset(0)}}><option value="">Todos los pagos</option>{['Pendiente','Pagada','Cancelada','Reembolsada','Completada'].map(x=><option key={x}>{x}</option>)}</select>
      <select aria-label="Estado de entrega" className="rounded-lg border bg-white p-3" value={entrega} onChange={e=>{setEntrega(e.target.value);setOffset(0)}}><option value="">Todas las entregas</option>{['Por preparar','Preparando','Lista para recoger','Entregada'].map(x=><option key={x}>{x}</option>)}</select>
    </form>
    {error&&<p role="alert" className="mb-4 text-red-700">{error}</p>}{mensaje&&<p role="status" className="mb-4 text-patina">{mensaje}</p>}{cargando&&<p role="status">Consultando pedidos...</p>}
    <p className="mb-2 text-sm text-secondary">Escribe el nombre o folio y pulsa Buscar. Se ignoran tildes y espacios sobrantes; no se corrigen errores de escritura.</p><p className="mb-4">{pagina.total} pedidos encontrados</p><div className="space-y-4">{pagina.items.map(v=>{
      const bloqueado=v.estado_reembolso&&!['Rechazado','Fallido'].includes(v.estado_reembolso)
      return <article key={v.id_venta} className="rounded-xl border bg-white p-6"><h2 className="text-xl font-semibold">Pedido #{v.id_venta} · {v.cliente}</h2><p className="text-sm">{v.correo} · {new Date(v.fecha_venta).toLocaleString('es-MX')}</p><p className="my-3 font-semibold">Pago: {v.estado_venta} · Entrega: {v.estado_entrega} · {dinero(v.total_centavos/100)}</p>
        <ul>{v.detalles.map(d=><li key={d.id_instrumento}>{d.cantidad} × {d.nombre_instrumento} · {dinero(d.precio_unitario)} c/u</li>)}</ul>
        {['Pagada','Completada'].includes(v.estado_venta)&&siguiente[v.estado_entrega]&&!bloqueado&&<button type="button" disabled={ocupado} className={boton+' mt-4'} onClick={()=>void accion(v,'entrega',{estado:siguiente[v.estado_entrega]})}>Pasar a {siguiente[v.estado_entrega]}</button>}
        {v.estado_reembolso&&<section aria-label="Solicitud de reembolso" className="mt-5 rounded-lg bg-ivory p-4"><h3 className="font-semibold">Reembolso: {v.estado_reembolso}</h3><p className="break-words">Motivo del cliente: {v.motivo}</p>{v.resolucion&&<p>Resolución: {v.resolucion}</p>}{v.stripe_refund_id&&<p className="break-all text-sm">Referencia Stripe: {v.stripe_refund_id}</p>}
          <div className="mt-3 flex flex-wrap gap-3">{v.estado_reembolso==='Solicitado'&&<><button type="button" disabled={ocupado} className={boton} onClick={()=>void accion(v,'reembolso/aprobar')}>Aprobar reembolso total</button><button type="button" disabled={ocupado} className={boton} onClick={()=>{setRechazo(v.id_venta);setMotivo('')}}>Rechazar solicitud</button></>}
          {['Procesando','Pendiente','RequiereAccion','Fallido'].includes(v.estado_reembolso)&&<button type="button" disabled={ocupado} className={boton} onClick={()=>void accion(v,'reembolso/sincronizar')}>Consultar reembolso en Stripe</button>}</div>
          {v.estado_reembolso==='RequiereAccion'&&<p className="mt-2">Revisa la acción pendiente en el panel de Stripe.</p>}
          {rechazo===v.id_venta&&<form onSubmit={e=>{e.preventDefault();void accion(v,'reembolso/rechazar',{motivo})}} className="mt-4"><label>Motivo de rechazo<textarea required minLength={5} maxLength={500} value={motivo} onChange={e=>setMotivo(e.target.value)} className="mt-1 block w-full rounded-lg border bg-white p-3"/></label><button disabled={ocupado} className={boton+' mt-2'}>Confirmar rechazo</button><button type="button" disabled={ocupado} className={boton+' ml-2'} onClick={()=>setRechazo(null)}>Volver</button></form>}
        </section>}
        {!!v.historial?.length&&<details className="mt-4"><summary className="cursor-pointer text-patina">Ver historial</summary><ul className="mt-2 text-sm">{v.historial.map((h,i)=><li key={i}>{new Date(h.fecha).toLocaleString('es-MX')} · {h.accion} · {h.administrador}</li>)}</ul></details>}
      </article>
    })}</div><div className="mt-6 flex items-center gap-4"><button type="button" className={boton} disabled={!offset||ocupado} onClick={()=>setOffset(Math.max(0,offset-20))}>Anterior</button><span>Página {offset/20+1}</span><button type="button" className={boton} disabled={offset+20>=pagina.total||ocupado} onClick={()=>setOffset(offset+20)}>Siguiente</button></div>
  </Marco>
}
