import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  ArrowRight, BadgeCheck, BookOpen, ChartNoAxesColumn, Check, ChevronRight,
  CircleAlert, CodeXml, Copy, Database, Eye, FileCode2, FlaskConical,
  Guitar, Layers, Music2, Play, RefreshCcw, Search, ShieldCheck, Table2, WandSparkles
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Results } from '@/components/Results'
import { api, type Category, type DatabaseStatus, type Exercise, type QueryResponse } from '@/lib/api'

const sections: { id: Category; label: string; caption: string; Icon: typeof Search }[] = [
  { id: 'simples', label: 'Consultas simples', caption: 'find y filtros', Icon: Search },
  { id: 'joins', label: 'Operaciones JOIN', caption: '$lookup y relaciones', Icon: Layers },
  { id: 'agregadas', label: 'Funciones agregadas', caption: '$group, $sum, $avg', Icon: ChartNoAxesColumn },
  { id: 'vistas', label: 'Vistas MongoDB', caption: 'Consultas reutilizables', Icon: Table2 },
]

function getError(error: unknown): string {
  return error instanceof Error ? error.message : 'No se pudo completar la operación.'
}

export default function App() {
  const [catalog, setCatalog] = useState<Exercise[]>([])
  const [category, setCategory] = useState<Category>('simples')
  const [active, setActive] = useState('S01')
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<DatabaseStatus | null>(null)
  const [connected, setConnected] = useState(false)
  const [result, setResult] = useState<QueryResponse | null>(null)
  const [attempted, setAttempted] = useState(false)
  const [busy, setBusy] = useState<'run' | 'seed' | 'views' | null>(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [copied, setCopied] = useState(false)

  const refresh = useCallback(async () => {
    const [health, state] = await Promise.all([api.health(), api.status()])
    setConnected(health.ok)
    setStatus(state)
  }, [])

  useEffect(() => {
    let activeRequest = true
    Promise.all([api.catalog(), api.health(), api.status()])
      .then(([list, health, state]) => {
        if (!activeRequest) return
        setCatalog(list.ejercicios)
        setConnected(health.ok)
        setStatus(state)
      })
      .catch((err: unknown) => { if (activeRequest) setError(getError(err)) })
    return () => { activeRequest = false }
  }, [])

  const filtered = useMemo(() => catalog.filter((e) =>
    e.categoria === category && `${e.id} ${e.titulo} ${e.descripcion}`.toLowerCase().includes(search.toLowerCase())
  ), [catalog, category, search])
  const selected = catalog.find((e) => e.id === active) ?? filtered[0]
  const categoryInfo = sections.find((item) => item.id === category) ?? sections[0]

  function changeSection(next: Category) {
    setCategory(next)
    setSearch('')
    setActive(catalog.find((e) => e.categoria === next)?.id ?? '')
    setResult(null)
    setAttempted(false)
    setError('')
    setNotice('')
  }

  function changeExercise(id: string) {
    setActive(id)
    setResult(null)
    setAttempted(false)
    setError('')
  }

  async function run() {
    if (!selected) return
    setBusy('run')
    setAttempted(true)
    setResult(null)
    setError('')
    setNotice('')
    try { setResult(await api.execute(selected.id)) }
    catch (err) { setError(getError(err)) }
    finally { setBusy(null) }
  }

  async function prepare(kind: 'seed' | 'views') {
    setBusy(kind)
    setError('')
    setNotice('')
    try {
      if (kind === 'seed') {
        const answer = await api.seed()
        setNotice(`${answer.mensaje} Nuevos documentos: ${answer.total_nuevos}.`)
      } else {
        const answer = await api.views()
        setNotice(`${answer.mensaje} ${answer.vistas.join(', ')}`)
      }
      await refresh()
    } catch (err) { setError(getError(err)) }
    finally { setBusy(null) }
  }

  async function copyCode() {
    if (!selected) return
    try {
      await navigator.clipboard.writeText(selected.codigo)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1800)
    } catch { setError('No se pudo copiar el código; selecciónalo manualmente.') }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="logo-line">
          <div className="logo-symbol"><Music2 size={25} /></div>
          <div><h1 className="font-heading text-[25px] font-bold leading-none">DaVinciMusic</h1><p className="text-[10px] tracking-[.17em] uppercase text-white/60 mt-1">Tienda y escuela musical</p></div>
        </div>
        <div className="sidebar-heading"><span className="sidebar-kicker">Laboratorio documental</span><h2>Unidad 6 · NoSQL</h2><p>Implementación de consultas sobre MongoDB Atlas con FastAPI y React.</p></div>
        <nav aria-label="Categorías de ejercicios" className="nav-sections">
          {sections.map(({ id, label, caption, Icon }) => {
            const total = catalog.filter((e) => e.categoria === id).length
            return <button type="button" key={id} className={`nav-button ${category === id ? 'nav-active' : ''}`} onClick={() => changeSection(id)}>
              <Icon size={19} /><span className="flex-1 text-left"><strong>{label}</strong><small>{caption}</small></span>
              <span className="count-chip">{total}</span><ChevronRight size={15} />
            </button>
          })}
        </nav>
        <div className="sidebar-note"><ShieldCheck size={18} /><span>Solo consultas predefinidas. El navegador nunca recibe la cadena de Atlas.</span></div>
        <div className="environment-card">
          <div className="flex items-start gap-3"><div className="icon-soft-gold"><Database size={20} /></div><div className="min-w-0"><strong>Entorno experimental</strong><p className="break-all">davincimusic_nosql_dev</p></div></div>
          <div className="mt-4 flex items-center gap-2"><span className={`status-dot ${connected ? 'online' : ''}`} /><span className="text-xs text-slate-600">{connected ? 'Atlas conectado' : 'Sin conexión'}</span></div>
          <p className="text-xs text-muted mt-2">{status?.total_demo ?? '—'} documentos de demostración en 9 colecciones.</p>
          <Button variant="outline" className="utility-btn w-full mt-4" disabled={!!busy || !status?.escritura_demo_habilitada} onClick={() => prepare('seed')}>
            <WandSparkles size={16} />{busy === 'seed' ? 'Preparando…' : 'Preparar datos demo'}
          </Button>
          <Button variant="outline" className="utility-btn w-full mt-2" disabled={!!busy || !status?.escritura_demo_habilitada} onClick={() => prepare('views')}>
            <Eye size={16} />{busy === 'views' ? 'Creando vistas…' : 'Crear / actualizar vistas'}
          </Button>
          {!status?.escritura_demo_habilitada && <p className="mt-2 text-[11px] leading-4 text-muted">Para habilitar botones de escritura: <code>DEMO_WRITE_ENABLED=true</code> en el backend.</p>}
          <button type="button" className="refresh-link" onClick={() => void refresh().catch((err: unknown) => setError(getError(err)))}><RefreshCcw size={13} /> Actualizar estado</button>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar"><div className="text-xs font-semibold text-muted">Unidad 6 <ChevronRight size={13} className="inline" /> Base de datos documental</div><div className="flex items-center gap-2"><span className="pill"><Database size={13} /> MongoDB Atlas</span><span className="pill desktop-only"><CodeXml size={14} /> FastAPI + React</span></div></header>
        <div className="workspace-content">
          <div className="hero-panel"><div className="relative z-10"><span className="hero-eyebrow"><FlaskConical size={15} /> IMPLEMENTACIÓN PRÁCTICA</span><h2 className="font-heading">Explora los datos.<br/><em>Comprende las relaciones.</em></h2><p>Ejecuta operaciones NoSQL, compara sus equivalentes SQL y visualiza los resultados reales de Atlas.</p></div><Guitar className="hero-guitar" size={200} strokeWidth={.7}/></div>
          <div className="section-title-row"><div><div className="section-eyebrow">{categoryInfo.label}</div><h2 className="font-heading section-heading">{category === 'simples' ? 'Consultas documentales' : category === 'joins' ? 'Relaciones entre colecciones' : category === 'agregadas' ? 'Analiza tus datos' : 'Vistas reutilizables'}</h2><p className="text-muted text-sm">Selecciona un ejercicio de la lista y ejecuta su consulta en el backend.</p></div><div className="exercise-summary"><BookOpen size={18} /> {filtered.length} ejercicios</div></div>
          {error && <div role="alert" className="alert-box"><CircleAlert size={18} /><span>{error}</span><button onClick={() => setError('')} aria-label="Cerrar alerta">×</button></div>}
          {notice && <div role="status" className="notice-box"><BadgeCheck size={17} /><span>{notice}</span><button onClick={() => setNotice('')} aria-label="Cerrar aviso">×</button></div>}
          <div className="content-grid">
            <section className="exercise-panel"><div className="exercise-header"><h3>Explorar ejercicios</h3><small>Consultas guardadas</small></div><label className="search-box"><Search size={16} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar nombre o código..." aria-label="Buscar ejercicios" /></label>
              <div className="exercise-list">{filtered.map((e) => <button type="button" key={e.id} className={`exercise-option ${selected?.id === e.id ? 'exercise-selected' : ''}`} onClick={() => changeExercise(e.id)}><span className="exercise-badge">{e.id}</span><span className="min-w-0 flex-1 text-left"><strong>{e.titulo}</strong><small>{e.descripcion}</small></span><ArrowRight size={16}/></button>)}{!filtered.length && <p className="p-5 text-sm text-muted">No hay ejercicios con ese filtro.</p>}</div>
            </section>
            <div className="right-stack">{selected ? <>
              <section className="query-info"><div className="flex items-center justify-between"><span className="section-eyebrow">EJERCICIO {selected.id}</span><span className="query-chip">{selected.tipo === 'view' ? 'VISTA' : selected.tipo === 'aggregate' ? 'PIPELINE' : 'FIND'}</span></div><h2 className="font-heading query-heading">{selected.titulo}</h2><p>{selected.descripcion}</p><div className="query-meta"><Database size={14} /> Colección: <code>{selected.coleccion}</code></div></section>
              <section className="code-card"><div className="card-heading"><div className="flex items-center gap-2"><CodeXml size={17}/><h3>Código MongoDB</h3></div><button type="button" className="copy-button" onClick={() => void copyCode()}>{copied ? <Check size={15}/> : <Copy size={15}/>} {copied ? 'Copiado' : 'Copiar código'}</button></div><div className="terminal-panel"><div className="terminal-header"><div className="terminal-dots"><i/><i/><i/></div><span>mongosh · JavaScript</span><span className="ml-auto text-xs text-white/50">Solo lectura</span></div><pre className="terminal-code"><code>{selected.codigo}</code></pre></div><div className="code-footer"><p><ShieldCheck size={14}/> Consulta predefinida y validada por FastAPI</p><Button onClick={() => void run()} disabled={!!busy || !connected} className="run-btn">{busy === 'run' ? <RefreshCcw size={17} className="animate-spin"/> : <Play size={17} fill="currentColor"/>}{busy === 'run' ? 'Consultando…' : 'Ejecutar ejemplo'}</Button></div></section>
              <Results data={result} loading={busy === 'run'} attempted={attempted}/>
              <div className="footnote"><ShieldCheck size={15} /> Los datos provienen de MongoDB Atlas; únicamente se muestran los campos definidos por cada ejercicio.</div>
            </> : <div className="query-info text-muted">Selecciona un ejercicio para ver su código y resultados.</div>}</div>
          </div>
          <footer className="page-footer"><span>DaVinciMusic · Unidad 6</span><span><FileCode2 size={14} /> Backend: FastAPI · Frontend: React/Vite/TS</span></footer>
        </div>
      </main>
    </div>
  )
}
