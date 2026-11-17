import {consultar} from '@/services/operaciones'
import {useEffect,useState} from 'react'
export default function MiAsistencia(){
 const [lista,setLista]=useState<{fecha:string;estado:string;nombre_clase:string}[]>([]),[error,setError]=useState('')
 useEffect(()=>{let vivo=true;void consultar<typeof lista>('/asistencia/mia').then(x=>{if(vivo)setLista(x)}).catch(e=>{if(vivo)setError(String(e))});return()=>{vivo=false}},[])
 return <section className="mt-8 rounded-xl border bg-white p-5"><h2 className="mb-3 text-xl font-semibold">Mi asistencia</h2>{error&&<p role="alert">{error}</p>}{!lista.length&&!error&&<p>Aún no hay asistencias registradas.</p>}<ul>{lista.map((x,i)=><li key={i}>{x.fecha} · {x.nombre_clase} · {x.estado}</li>)}</ul><p className="mt-2 text-sm text-secondary">Últimos 200 registros.</p></section>
}
