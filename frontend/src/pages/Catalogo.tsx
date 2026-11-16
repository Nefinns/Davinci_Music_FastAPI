import { useEffect, useState } from "react"
import { Link, useSearchParams } from "react-router-dom"
import { categorias, instrumentos, type Categoria, type Instrumento } from "@/services/catalogo"

export default function Catalogo() {
  const [params, setParams] = useSearchParams()
  const [lista, setLista] = useState<Instrumento[]>([])
  const [tipos, setTipos] = useState<Categoria[]>([])
  const [total, setTotal] = useState(0)
  const [error, setError] = useState("")
  const [busqueda, setBusqueda] = useState(params.get("q") || "")
  const pagina = Math.max(1, Number(params.get("pagina")) || 1)
  useEffect(() => { void categorias().then(setTipos).catch(e => setError(String(e))) }, [])
  useEffect(() => {
    let vigente = true
    void instrumentos(params).then(r => {
      if (vigente) { setLista(r.items); setTotal(r.total); setError("") }
    }).catch(e => { if (vigente) setError(String(e)) })
    return () => { vigente = false }
  }, [params])
  function cambiar(campo: string, valor: string) {
    const nuevos = new URLSearchParams(params)
    if (valor) nuevos.set(campo, valor)
    else nuevos.delete(campo)
    if (campo !== "pagina") nuevos.delete("pagina")
    setParams(nuevos)
  }
  return <main className="min-h-screen bg-ivory px-6 py-10 text-ebony">
    <div className="mx-auto max-w-6xl">
      <Link to="/" className="text-patina">← DaVinciMusic</Link>
      <nav className="mt-4 flex gap-5 text-patina"><Link to="/carrito">Ver carrito</Link><Link to="/mis-compras">Mis compras</Link><Link to="/escuela">Escuela</Link></nav>
      <h1 className="mt-8 font-heading text-5xl">Catálogo de instrumentos</h1>
      <form onSubmit={e => { e.preventDefault(); cambiar("q", busqueda) }} className="mt-8 flex flex-wrap gap-3">
        <input aria-label="Buscar instrumentos" className="rounded-lg border p-3" placeholder="Buscar por nombre o modelo" value={busqueda} onChange={e => setBusqueda(e.target.value)} />
        <button className="rounded-lg bg-patina px-5 py-3 text-white">Buscar</button>
        <select aria-label="Categoría" className="rounded-lg border p-3" value={params.get("categoria") || ""} onChange={e => cambiar("categoria", e.target.value)}>
          <option value="">Todas las categorías</option>
          {tipos.map(t => <option key={t.id_categoria} value={t.id_categoria}>{t.nombre_categoria}</option>)}
        </select>
        <input aria-label="Marca" className="rounded-lg border p-3" placeholder="Marca" value={params.get("marca") || ""} onChange={e => cambiar("marca", e.target.value)} />
      </form>
      {error && <p role="alert" className="mt-5 text-red-700">{error}</p>}
      <p className="mt-7">{total} instrumentos encontrados</p>
      <div className="mt-5 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {lista.map(i => <Link key={i.id_instrumento} to={`/catalogo/${i.id_instrumento}`} className="overflow-hidden rounded-2xl bg-white shadow-sm">
          {i.imagen_url ? <img src={i.imagen_url} alt={i.nombre_instrumento} className="h-56 w-full object-cover" /> : <div className="flex h-56 items-center justify-center bg-slate-100 text-secondary">Sin imagen</div>}
          <div className="p-5"><p className="text-sm text-patina">{i.nombre_categoria} · {i.marca || "Sin marca"}</p>
            <h2 className="mt-2 font-heading text-2xl">{i.nombre_instrumento}</h2>
            <p className="mt-1 text-sm">{i.modelo || "Sin modelo"} · {i.stock_actual > 0 ? `${i.stock_actual} disponibles` : "Agotado"}</p>
            <p className="mt-3 font-semibold">${Number(i.precio_venta).toLocaleString("es-MX", { style: "currency", currency: "MXN" })}</p>
          </div>
        </Link>)}
      </div>
      <div className="mt-8 flex gap-4">
        <button disabled={pagina <= 1} onClick={() => cambiar("pagina", String(pagina - 1))} className="disabled:opacity-40">Anterior</button>
        <span>Página {pagina} de {Math.max(1, Math.ceil(total / 12))}</span>
        <button disabled={pagina * 12 >= total} onClick={() => cambiar("pagina", String(pagina + 1))} className="disabled:opacity-40">Siguiente</button>
      </div>
    </div>
  </main>
}
