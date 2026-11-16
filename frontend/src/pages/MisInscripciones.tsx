import { useEffect, useState } from 'react'
import Marco from '@/components/MarcoOperaciones'
import { consultar,dinero,type Inscripcion } from '@/services/operaciones'
export default function MisInscripciones(){
 const [lista,setLista]=useState<Inscripcion[]>([]),[error,setError]=useState(''),[cargando,setCargando]=useState(true)
 useEffect(()=>{let vivo=true;void consultar<Inscripcion[]>('/escuela/mis-inscripciones').then(x=>{if(vivo)setLista(x)}).catch(e=>{if(vivo)setError(String(e))}).finally(()=>{if(vivo)setCargando(false)});return()=>{vivo=false}},[])
 return <Marco titulo="Mis inscripciones"><p className="mb-6">Para solicitar una baja académica comunícate con un administrador. Desactivar tu cuenta no cancela tus inscripciones.</p>{error&&<p role="alert" className="text-red-700">{error}</p>}{cargando?<p role="status">Cargando...</p>:!lista.length&&<p>Aún no tienes inscripciones.</p>}<div className="grid gap-4 md:grid-cols-2">{lista.map(x=><article key={x.id_inscripcion} className="rounded-xl border bg-white p-5"><h2 className="font-heading text-2xl">{x.nombre_clase}</h2><p>Folio {x.id_inscripcion} · {x.estado_inscripcion}</p><p>Costo mensual acordado: {dinero(x.costo_mensual_acordado)}</p><ul className="mt-3">{x.horarios?.map((h,j)=><li key={j}>{h.dia_semana} {h.hora_inicio.slice(0,5)}–{h.hora_fin.slice(0,5)} · {h.salon}</li>)}</ul><p className="mt-3 text-sm text-secondary">El módulo de mensualidades estará disponible en una siguiente etapa.</p></article>)}</div></Marco>
}
