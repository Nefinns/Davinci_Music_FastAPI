import { useEffect, useMemo, useState } from 'react'
import { Activity, ArrowRight, BarChart3, BookOpen, CheckCircle2, ChevronRight, CircleAlert, Clock3,
  Code2, Copy, Database, FileCode2, Filter, Layers3, LoaderCircle, Music2, Play, RefreshCw,
  Search, ShieldCheck, Table2, WandSparkles, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { getCatalog, getState, prepareDb, runExercise } from './api'
import type { Catalog, DbState, Exercise, RunResult } from './types'

const sectionIcons = { simples: Search, joins: Layers3, agregadas: BarChart3, vistas: Table2, triggers: Zap }
const sectionNotes: Record<string,string> = {
  simples: 'Filtros, orden y selección', joins: 'Relaciones entre entidades',
  agregadas: 'Estadísticas y agrupaciones', vistas: 'Consultas guardadas',
  triggers: 'Reglas automáticas de integridad'
}
const defaultState: DbState = { connected:false, ready:false, message:'Verificando conexión…' }

function readable(v: unknown): string {
  if (v === null || v === undefined) return '—'
  if (typeof v === 'boolean') return v ? 'Sí' : 'No'
  if (typeof v === 'number') return Number.isInteger(v) ? v.toLocaleString('es-MX') : v.toLocaleString('es-MX', { maximumFractionDigits: 2 })
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}

export default function App() {
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [status, setStatus] = useState<DbState>(defaultState)
  const [group, setGroup] = useState('simples')
  const [selected, setSelected] = useState('S01')
  const [query, setQuery] = useState('')
  const [params, setParams] = useState<Record<string,string|number>>({})
  const [result, setResult] = useState<RunResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [settingUp, setSettingUp] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    void getCatalog().then(setCatalog).catch(e => setError(e instanceof Error ? e.message : 'Error cargando catálogo'))
    void getState().then(setStatus).catch(() => setStatus({connected:false,ready:false,message:'API desconectada'}))
  }, [])

  const filtered = useMemo(() => (catalog?.exercises || []).filter(x =>
    x.group === group && `${x.code} ${x.title} ${x.description}`.toLowerCase().includes(query.toLowerCase())
  ), [catalog, group, query])
  const active = catalog?.exercises.find(x => x.code === selected && x.group === group)
  const section = catalog?.groups.find(x => x.id === group)
  const completed = catalog?.total || 65

  function choose(ex: Exercise) {
    setSelected(ex.code)
    setParams(Object.fromEntries(ex.params.map(p => [p.name,p.default])))
    setResult(null)
    setError('')
    setNotice('')
  }
  function changeGroup(next: string) {
    setGroup(next)
    setQuery('')
    const first = catalog?.exercises.find(x => x.group === next)
    if (first) choose(first)
  }
  async function refresh() {
    try { setStatus(await getState()) }
    catch { setStatus({connected:false,ready:false,message:'No responde el servidor'}) }
  }
  async function doSetup() {
    if (!window.confirm('Se preparará exclusivamente la base UNIT5_ALLOWED_DATABASE. Debe estar vacía o contener los datos demo previamente instalados. ¿Continuar?')) return
    setSettingUp(true); setError(''); setNotice('')
    try {
      const data = await prepareDb()
      setNotice(`${data.message} ${data.created_now ? 'Se creó el esquema.' : 'Se conservó el esquema existente.'}`)
      await refresh()
    } catch (e) { setError(e instanceof Error ? e.message : 'No se pudo preparar la base de datos') }
    finally { setSettingUp(false) }
  }
  async function execute() {
    if (!active) return
    setBusy(true); setError(''); setNotice(''); setResult(null)
    try { setResult(await runExercise(active.code, params)) }
    catch (e) { setError(e instanceof Error ? e.message : 'Error ejecutando ejemplo') }
    finally { setBusy(false) }
  }
  async function copySql() {
    if (!active) return
    try { await navigator.clipboard.writeText(active.sql); setCopied(true); window.setTimeout(() => setCopied(false), 1500) }
    catch { setError('No fue posible copiar el SQL desde este navegador.') }
  }

  return <div className="min-h-screen bg-[#F3F5F2] text-[#14181B]">
    <header className="topbar">
      <div className="mx-auto flex max-w-[1650px] items-center justify-between gap-4 px-5 py-3 md:px-8">
        <div className="flex items-center gap-3">
          <div className="brandmark"><Music2 size={23} strokeWidth={2.2}/></div>
          <div><div className="text-lg leading-tight font-bold tracking-tight">DaVinci<span className="text-[#AD8730]">Music</span></div>
            <div className="text-[11px] font-medium tracking-[.17em] text-[#5D716B] uppercase">Laboratorio de bases de datos</div></div>
        </div>
        <div className="flex items-center gap-3">
          <div className={`hidden items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold sm:flex ${status.ready ? 'bg-[#E6F3EB] text-[#17613E]' : 'bg-[#FFF4E1] text-[#90651B]'}`}>
            <span className={`h-2 w-2 rounded-full ${status.ready ? 'bg-[#389562]' : 'bg-[#E1A745]'}`}/>{status.ready ? 'Base preparada' : status.connected ? 'Pendiente de preparar' : 'Sin conexión'}
          </div>
          <button className="icon-button" onClick={() => void refresh()} title="Comprobar conexión" aria-label="Comprobar conexión"><RefreshCw size={18}/></button>
          <span className="rounded-lg border border-[#DCE5E0] bg-white px-3 py-2 text-xs font-bold text-[#0A3D3A]">U5 · 2026</span>
        </div>
      </div>
    </header>

    <div className="mx-auto max-w-[1650px] px-4 py-6 md:px-8 md:py-8">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div><div className="mb-2 inline-flex items-center gap-2 text-xs font-bold tracking-[.2em] text-[#937532] uppercase"><BookOpen size={14}/> Práctica académica</div>
          <h1 className="font-display text-4xl font-bold tracking-tight text-[#102E2C] md:text-5xl">Explorador SQL <span className="text-[#9A7A36]">/ Unidad 5</span></h1>
          <p className="mt-2 max-w-2xl text-sm text-[#657670] md:text-base">Consultas, relaciones, estadísticas, vistas y reglas automáticas sobre el esquema de DaVinciMusic.</p>
        </div>
        <div className="flex items-center gap-3 rounded-2xl border border-[#DCE3DE] bg-white px-5 py-3 shadow-sm">
          <div className="rounded-xl bg-[#EDF5F0] p-2 text-[#0A5B51]"><Database size={23}/></div>
          <div><div className="text-2xl leading-none font-bold">{completed}</div><div className="mt-1 text-xs text-[#6B7B75]">ejercicios disponibles</div></div>
        </div>
      </div>

      <div className="layout-grid">
        <aside className="space-y-4">
          <section className="rounded-2xl bg-[#0A3D3A] p-5 text-white shadow-lg shadow-[#0A3D3A]/10">
            <div className="mb-5 flex items-center gap-2 text-xs font-bold tracking-[.14em] text-[#B5D4C8] uppercase"><Activity size={14}/> Temario</div>
            <div className="space-y-1">
              {catalog?.groups.map((topic, index) => {
                const Icon = sectionIcons[topic.id as keyof typeof sectionIcons] || FileCode2
                return <button key={topic.id} onClick={() => changeGroup(topic.id)} className={`w-full rounded-xl px-3 py-3 text-left transition-colors ${group === topic.id ? 'bg-[#17625A] shadow-inner' : 'hover:bg-white/10'}`}>
                  <div className="flex items-center gap-3"><Icon size={18} className={group === topic.id ? 'text-[#E1BE67]' : 'text-[#A3C6BD]'}/>
                    <div className="min-w-0 flex-1"><div className="text-sm font-semibold">5.{index+1} · {topic.title}</div><div className="mt-0.5 text-[11px] text-[#B8D3CB]">{topic.target} ejercicios</div></div>
                    <ChevronRight size={15} className="text-[#B8D3CB]"/>
                  </div>
                </button>
              })}
            </div>
            <div className="mt-6 border-t border-white/15 pt-5 text-xs leading-5 text-[#B6D0C7]"><ShieldCheck size={17} className="mb-2 text-[#E1BE67]"/>
              Solo ejercicios predefinidos. Ningún SQL arbitrario se recibe desde el navegador.</div>
          </section>
          <section className="rounded-2xl border border-[#DCE4DE] bg-white p-4 shadow-sm">
            <div className="flex items-start gap-3"><div className="rounded-xl bg-[#FFF6E4] p-2 text-[#AD8130]"><Database size={19}/></div>
              <div className="min-w-0 flex-1"><div className="text-sm font-bold">Entorno experimental</div>
                <div className="mt-1 break-words text-xs text-[#72817B]">{status.database || status.message}</div></div>
            </div>
            <Button className="mt-4 w-full" variant="outline" onClick={() => void doSetup()} disabled={settingUp || !status.connected}>
              {settingUp ? <LoaderCircle size={16} className="animate-spin"/> : <WandSparkles size={16}/>} {settingUp ? 'Preparando…' : status.ready ? 'Verificar / reinstalar objetos' : 'Preparar base demo'}
            </Button>
            <p className="mt-3 text-[11px] leading-5 text-[#8A9790]">La preparación conserva los datos demo previos. Utiliza una BD exclusiva llamada davinci_music_unidad5.</p>
          </section>
        </aside>

        <section className="min-w-0 rounded-2xl border border-[#DCE4DE] bg-white shadow-sm">
          <div className="border-b border-[#EDF0ED] p-5"><div className="flex items-center justify-between"><div className="text-xs font-bold tracking-[.14em] text-[#9D813F] uppercase">Biblioteca de ejercicios</div>
            <span className="rounded-lg bg-[#F2F5F2] px-2.5 py-1 text-xs font-semibold text-[#61716C]">{filtered.length} resultados</span></div>
            <h2 className="mt-2 text-xl font-bold text-[#183D37]">{section?.title || 'Consultas simples'}</h2>
            <p className="mt-1 text-xs text-[#7D8D86]">{sectionNotes[group]}</p>
            <label className="mt-4 flex items-center gap-2 rounded-xl border border-[#DDE5E0] bg-[#F8FAF8] px-3 py-2.5 text-[#9AA9A2] focus-within:border-[#B1C9BD]">
              <Search size={17}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Buscar por nombre o código…" className="w-full bg-transparent text-sm text-[#183D37] outline-none placeholder:text-[#9AA9A2]" aria-label="Buscar ejercicios"/>
              <Filter size={15}/>
            </label>
          </div>
          <div className="max-h-[740px] space-y-2 overflow-y-auto p-3">
            {filtered.map(ex => <button key={ex.code} onClick={() => choose(ex)} className={`exercise-row w-full rounded-xl border p-3 text-left ${selected === ex.code ? 'border-[#A5C4B6] bg-[#EFF6F0]' : 'border-transparent hover:border-[#E5ECE6] hover:bg-[#FAFCFA]'}`}>
              <div className="flex items-start gap-3"><div className={`code-bubble ${selected === ex.code ? 'bg-[#0A3D3A] text-white' : 'bg-[#EDF2EF] text-[#59756B]'}`}>{ex.code}</div>
                <div className="min-w-0 flex-1"><div className="text-sm font-semibold text-[#203E38]">{ex.title}</div><div className="mt-1 line-clamp-2 text-xs leading-5 text-[#778981]">{ex.description}</div></div>
                <ArrowRight size={15} className={selected === ex.code ? 'text-[#11674E]' : 'text-[#B5C2BA]'}/></div>
            </button>)}
            {filtered.length === 0 && <div className="py-14 text-center text-sm text-[#86948C]">No hay ejercicios que coincidan.</div>}
          </div>
        </section>

        <main className="min-w-0 space-y-5" aria-live="polite">
          {active ? <>
            <section className="overflow-hidden rounded-2xl border border-[#DCE4DE] bg-white shadow-sm">
              <div className="h-1 bg-gradient-to-r from-[#0A3D3A] via-[#389080] to-[#D0AB57]"/>
              <div className="p-5 md:p-6"><div className="flex flex-wrap items-center gap-2"><span className="tag-dark">{active.code}</span><span className="tag-light">{section?.title}</span></div>
                <h2 className="mt-4 font-display text-3xl font-bold text-[#173D37] md:text-4xl">{active.title}</h2>
                <p className="mt-2 max-w-[750px] text-sm leading-6 text-[#61746C]">{active.description}</p>
                {active.group === 'triggers' && <div className="mt-4 flex gap-2 rounded-xl bg-[#FFF8E9] px-4 py-3 text-xs leading-5 text-[#806126]"><ShieldCheck size={18} className="shrink-0"/>Los cambios de esta demostración se revierten automáticamente al terminar la transacción.</div>}
              </div>
            </section>

            <section className="rounded-2xl border border-[#DCE4DE] bg-white p-5 shadow-sm md:p-6">
              <div className="mb-3 flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-2 text-sm font-bold text-[#25443D]"><Code2 size={18} className="text-[#0B6B5B]"/> Código PostgreSQL</div>
                <Button variant="outline" size="sm" onClick={() => void copySql()}><Copy size={14}/>{copied ? 'Copiado' : 'Copiar SQL'}</Button></div>
              <div className="sql-window"><div className="sql-window-top"><span className="h-2 w-2 rounded-full bg-[#DA8378]"/><span className="h-2 w-2 rounded-full bg-[#E9BD70]"/><span className="h-2 w-2 rounded-full bg-[#80BFA6]"/><span className="ml-2 text-[11px] text-[#A8C5BC]">{active.group === 'triggers' ? 'plpgsql · PostgreSQL' : 'consulta.sql · PostgreSQL'}</span></div>
                <pre className="overflow-x-auto p-4 text-[12px] leading-6 text-[#CEE7D9] md:text-[13px]"><code>{active.sql}</code></pre>
              </div>
              {active.params.length > 0 && <div className="mt-5"><div className="mb-3 text-xs font-bold tracking-[.1em] text-[#647970] uppercase">Parámetros de entrada</div>
                <div className="grid gap-3 sm:grid-cols-2">{active.params.map(p => <label key={p.name} className="block"><span className="mb-1.5 block text-xs font-semibold text-[#567068]">{p.label}</span>
                  <input type={p.kind === 'date' ? 'date' : p.kind === 'int' || p.kind === 'float' ? 'number' : 'text'} step={p.kind === 'float' ? '0.01' : undefined}
                    value={params[p.name] ?? p.default} onChange={e => setParams(prev => ({...prev, [p.name]:e.target.value}))}
                    className="w-full rounded-xl border border-[#D4E0D9] bg-[#F9FBF9] px-3 py-2.5 text-sm outline-none focus:border-[#0A5C50]"/></label>)}</div></div>}
              <div className="mt-5 flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-2 text-xs text-[#6B8276]"><ShieldCheck size={15}/> SQL parametrizado y validado</div>
                <Button onClick={() => void execute()} disabled={busy || !status.ready} size="lg" className="min-w-[168px]">
                  {busy ? <LoaderCircle size={17} className="animate-spin"/> : <Play size={17} fill="currentColor"/>} {busy ? 'Ejecutando…' : 'Ejecutar ejemplo'}
                </Button></div>
            </section>
          </> : <div className="rounded-2xl bg-white p-9 text-[#607970]">Selecciona un ejercicio para ver sus detalles.</div>}

          {(error || notice) && <div role={error ? 'alert' : 'status'} className={`flex gap-3 rounded-xl border p-4 text-sm ${error ? 'border-[#EAC5C0] bg-[#FFF1EF] text-[#9B4338]' : 'border-[#BCE1CE] bg-[#EFF9F2] text-[#276646]'}`}>
            {error ? <CircleAlert size={20} className="shrink-0"/> : <CheckCircle2 size={20} className="shrink-0"/>}<span>{error || notice}</span></div>}

          <section className="rounded-2xl border border-[#DCE4DE] bg-white p-5 shadow-sm md:p-6">
            <div className="flex flex-wrap items-center justify-between gap-3"><div><div className="flex items-center gap-2 text-sm font-bold text-[#24443B]"><Table2 size={19} className="text-[#0B6B5B]"/> Resultados</div>
              <p className="mt-1 text-xs text-[#89988F]">La tabla se actualiza después de cada ejecución.</p></div>
              {result && <div className="flex flex-wrap items-center gap-3 text-xs text-[#617970]"><span className="flex items-center gap-1"><Table2 size={14}/>{result.rows.length} filas</span>
                <span className="flex items-center gap-1"><Clock3 size={14}/>{result.duration_ms.toFixed(1)} ms</span></div>}
            </div>
            {result ? <><div className="mt-5 overflow-x-auto rounded-xl border border-[#E0E8E1]"><table className="w-full min-w-max border-collapse text-left text-xs md:text-sm">
              <thead className="bg-[#EFF4EF] text-[#49685C]"><tr>{result.columns.map(c => <th key={c} className="border-b border-[#DFE8E1] px-4 py-3 text-xs font-bold whitespace-nowrap">{c.replace(/_/g,' ')}</th>)}</tr></thead>
              <tbody>{result.rows.map((row,i) => <tr key={i} className="border-b border-[#EFF3EF] last:border-b-0 hover:bg-[#FAFCFA]">{result.columns.map(col => <td key={col} className="max-w-[260px] px-4 py-3 break-words text-[#3D5249]">{readable(row[col])}</td>)}</tr>)}</tbody></table>
              {!result.rows.length && <div className="p-5 text-center text-sm text-[#819189]">La consulta no devolvió registros.</div>}</div>
              <div className="mt-3 flex items-center gap-2 text-xs text-[#4B7D60]"><CheckCircle2 size={15}/>{result.message}</div></>
             : <div className="empty-state mt-5"><div className="mb-3 rounded-2xl bg-[#EFF4F0] p-4 text-[#507D69]"><FileCode2 size={25}/></div>
                <div className="text-sm font-semibold text-[#5A7569]">Todo listo para consultar</div>
                <p className="mt-1 max-w-xs text-center text-xs leading-5 text-[#90A098]">Ejecuta un ejercicio para visualizar el resultado real de tu base experimental.</p></div>}
          </section>
        </main>
      </div>
      <footer className="mt-7 flex flex-wrap items-center justify-between gap-3 border-t border-[#D7E2DB] pt-5 text-xs text-[#829188]">
        <div className="flex items-center gap-2"><Music2 size={14}/> DaVinciMusic · Unidad 5 · Proyecto académico local</div>
        <div className="flex items-center gap-2"><ShieldCheck size={14}/> No modifica la base principal <ChevronRight size={14}/></div>
      </footer>
    </div>
  </div>
}
