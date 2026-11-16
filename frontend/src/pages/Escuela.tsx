import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Marco from '@/components/MarcoOperaciones'
import { useSesion } from '@/contexts/SesionContext'
import { consultar, operar, dinero, type Clase } from '@/services/operaciones'
export default function Escuela() {
  const { autenticado } = useSesion()
  const [lista,setLista]=useState<Clase[]>([]), [error,setError]=useState(''),[mensaje,setMensaje]=useState(''),[cargando,setCargando]=useState(true),[ocupado,setOcupado]=useState(false),[busqueda,setBusqueda]=useState('')
  function cargar() { return consultar<Clase[]>('/escuela/clases',false).then(setLista) }
  useEffect(()=>{let vivo=true; void consultar<Clase[]>('/escuela/clases',false).then(x=>{if(vivo)setLista(x)}).catch(e=>{if(vivo)setError(String(e))}).finally(()=>{if(vivo)setCargando(false)});return()=>{vivo=false}},[])
  async function inscribir(c:Clase) {
    if(ocupado || !window.confirm(`¿Inscribirte en ${c.nombre_clase}? Costo mensual acordado: ${dinero(c.costo_mensual)}. Esta operación registra la inscripción; aún no cobra mensualidades.`)) return
    setOcupado(true);setError('');setMensaje('')
    try {const r=await operar(`/escuela/clases/${c.id_clase}/inscripciones`);setMensaje(r.mensaje);await cargar()}catch(e){setError(String(e))}finally{setOcupado(false)}
  }
  const visibles=lista.filter(c=>(c.nombre_clase+' '+c.maestro+' '+c.nivel+' '+c.nombre_instrumento).toLowerCase().includes(busqueda.toLowerCase()))
  return <Marco titulo="Escuela de música"><p className="mb-6 text-secondary">Clases presenciales. Elige un grupo, consulta su horario y reserva tu lugar mediante la inscripción.</p>
    <label className="block">Buscar clase, instrumento, nivel o maestro<input className="mt-2 mb-6 block w-full rounded-xl border bg-white p-3" value={busqueda} onChange={e=>setBusqueda(e.target.value)} /></label>
    {cargando&&<p role="status">Consultando clases...</p>}{error&&<p role="alert" className="mb-5 text-red-700">{error}</p>}{mensaje&&<p role="status" className="mb-5 rounded-xl bg-white p-4 text-patina">{mensaje} <Link to="/mis-inscripciones" className="underline">Ver mis clases</Link></p>}
    {!cargando&&!visibles.length&&<p>No hay clases disponibles con estos criterios.</p>}
    <div className="grid gap-5 md:grid-cols-2">{visibles.map(c=><article key={c.id_clase} className="rounded-2xl border border-ebony/10 bg-white p-6 shadow-sm"><p className="text-sm text-patina">{c.nombre_instrumento} · {c.nivel}</p><h2 className="mt-2 font-heading text-2xl">{c.nombre_clase}</h2><p className="mt-3">Maestro: {c.maestro}</p><p>{c.nombre_periodo}: {c.fecha_inicio} — {c.fecha_fin}</p><ul className="my-4 space-y-1">{c.horarios.map((h,j)=><li key={j}>{h.dia_semana} {h.hora_inicio.slice(0,5)}–{h.hora_fin.slice(0,5)} · {h.salon||'Salón por confirmar'}</li>)}</ul><p className="font-semibold">{dinero(c.costo_mensual)} / mes</p><p className="my-3 text-sm">{c.disponibles} lugares disponibles de {c.cupo_maximo}</p>{autenticado?<button disabled={ocupado||!c.disponibles} className="rounded-xl bg-patina px-5 py-3 font-semibold text-white disabled:opacity-50" onClick={()=>void inscribir(c)}>{c.disponibles?'Inscribirme':'Grupo lleno'}</button>:<Link to="/login" className="inline-block rounded-xl bg-patina px-5 py-3 text-white">Iniciar sesión para inscribirme</Link>}</article>)}</div>
  </Marco>
}
