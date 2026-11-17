import { useEffect, useState } from 'react'
import AsistenciaGrupo from '@/components/AsistenciaGrupo'
import Marco from '@/components/MarcoOperaciones'
import { consultar, type Clase } from '@/services/operaciones'
export default function Docencia() {
  const [clases,setClases]=useState<Clase[]|null>(null),[error,setError]=useState('')
  useEffect(()=>{let vivo=true;void consultar<Clase[]>('/escuela/docencia').then(x=>{if(vivo)setClases(x)}).catch(e=>{if(vivo)setError(String(e))});return()=>{vivo=false}},[])
  return <Marco titulo="Área docente"><p className="mb-6">Tus grupos como profesor. No necesitas inscribirte para impartirlos.</p>{error&&<p role="alert" className="text-red-700">{error}</p>}{!clases&&!error&&<p role="status">Consultando grupos...</p>}{clases?.length===0&&<p>Aún no tienes grupos asignados. Solicita al administrador completar tu perfil docente y asignar tus clases.</p>}<div className="grid gap-4 md:grid-cols-2">{clases?.map(c=><article key={c.id_clase} className="rounded-xl border bg-white p-5"><p className="text-sm text-patina">Profesor · {c.activa?'Activa':'Retirada'}</p><h2 className="my-2 text-xl font-semibold">{c.nombre_clase}</h2><p>{c.nombre_periodo} · {c.nivel}</p><p>{c.inscritos} alumnos de {c.cupo_maximo}</p><ul className="mt-3">{c.horarios.map((h,j)=><li key={j}>{h.dia_semana} {h.hora_inicio.slice(0,5)}–{h.hora_fin.slice(0,5)} · {h.salon}</li>)}</ul><AsistenciaGrupo id={c.id_clase}/></article>)}</div></Marco>
}
