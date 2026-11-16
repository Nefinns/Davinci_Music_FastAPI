import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { puedeAdministrar } from "@/services/usuarios"
import {
  borrarCategoria, categorias, guardarCategoria, guardarInstrumento,
  retirarInstrumento, subirImagen, todosInstrumentos,
  type Categoria, type DatosInstrumento, type Instrumento,
} from "@/services/catalogo"

const vacio: DatosInstrumento = {
  id_categoria: 0, nombre_instrumento: "", marca: "", modelo: "", tamano: "",
  color: "", precio_venta: 0, stock_actual: 0, activo: true,
}

export default function AdministrarCatalogo() {
  const [autorizado, setAutorizado] = useState<boolean | null>(null)
  const [tipos, setTipos] = useState<Categoria[]>([])
  const [productos, setProductos] = useState<Instrumento[]>([])
  const [form, setForm] = useState<DatosInstrumento>(vacio)
  const [edicion, setEdicion] = useState<number | undefined>()
  const [categoria, setCategoria] = useState("")
  const [descripcion, setDescripcion] = useState("")
  const [categoriaId, setCategoriaId] = useState<number | undefined>()
  const [error, setError] = useState("")
  const [aviso, setAviso] = useState("")
  const [filtros, setFiltros] = useState({ q: "", categoria: "", marca: "", activo: "", existencias: "todas" })
  const [aplicados, setAplicados] = useState(new URLSearchParams())

  async function recargar(params = aplicados) {
    const [c, i] = await Promise.all([categorias(), todosInstrumentos(params)])
    setTipos(c); setProductos(i)
  }
  useEffect(() => {
    let vigente = true
    void puedeAdministrar().then(async permitido => {
      if (vigente) setAutorizado(permitido)
      if (permitido && vigente) {
        const [c, i] = await Promise.all([categorias(), todosInstrumentos()])
        if (vigente) { setTipos(c); setProductos(i) }
      }
    }).catch(e => { if (vigente) { setAutorizado(false); setError(String(e)) } })
    return () => { vigente = false }
  }, [])

  async function ejecutar(accion: () => Promise<unknown>) {
    try {
      setError(""); setAviso("")
      await accion()
      await recargar()
      setAviso("Cambios guardados.")
    } catch (e) { setError(e instanceof Error ? e.message : String(e)) }
  }

  if (autorizado === null) return <p role="status">Verificando permisos...</p>
  if (!autorizado) return <p className="p-8">Acceso restringido. <Link to="/">Volver</Link> {error}</p>
  return <main className="min-h-screen bg-ivory p-6 text-ebony">
    <div className="mx-auto max-w-6xl">
      <Link to="/inicio" className="text-patina">← Mi cuenta</Link>
      <h1 className="mt-6 font-heading text-4xl">Administrar catálogo</h1>
      {error && <p role="alert" className="my-4 text-red-700">{error}</p>}
      {aviso && <p role="status" className="my-4 text-green-700">{aviso}</p>}
      <section className="mt-8 rounded-xl bg-white p-6">
        <h2 className="font-heading text-2xl">Categorías</h2>
        <form className="mt-4 flex flex-wrap gap-2" onSubmit={e => {
          e.preventDefault()
          void ejecutar(async () => {
            await guardarCategoria({ nombre_categoria: categoria, descripcion: descripcion || null }, categoriaId)
            setCategoria(""); setDescripcion(""); setCategoriaId(undefined)
          })
        }}>
          <input required maxLength={100} aria-label="Nombre de categoría" placeholder="Nombre de categoría" className="rounded border p-2" value={categoria} onChange={e => setCategoria(e.target.value)} />
          <input maxLength={255} aria-label="Descripción de categoría" placeholder="Descripción opcional" className="rounded border p-2" value={descripcion} onChange={e => setDescripcion(e.target.value)} />
          <button className="rounded bg-patina px-4 text-white">{categoriaId ? "Guardar categoría" : "Agregar categoría"}</button>
          {categoriaId && <button type="button" onClick={() => { setCategoria(""); setDescripcion(""); setCategoriaId(undefined) }}>Cancelar</button>}
        </form>
        <ul className="mt-4 space-y-2">{tipos.map(t => <li key={t.id_categoria} className="flex flex-wrap items-center gap-3">
          <span>{t.nombre_categoria}{t.descripcion ? ` — ${t.descripcion}` : ""}</span>
          <button className="text-patina" onClick={() => { setCategoriaId(t.id_categoria); setCategoria(t.nombre_categoria); setDescripcion(t.descripcion || "") }}>Editar</button>
          <button className="text-red-700" onClick={() => { if (window.confirm("¿Eliminar esta categoría?")) void ejecutar(() => borrarCategoria(t.id_categoria)) }}>Eliminar</button>
        </li>)}</ul>
      </section>
      <section className="mt-8 rounded-xl bg-white p-6">
        <h2 className="font-heading text-2xl">{edicion ? "Editar instrumento" : "Nuevo instrumento"}</h2>
        <form className="mt-5 grid gap-3 sm:grid-cols-2" onSubmit={e => {
          e.preventDefault()
          void ejecutar(async () => {
            await guardarInstrumento(form, edicion)
            setForm(vacio); setEdicion(undefined)
          })
        }}>
          <select required aria-label="Categoría del instrumento" className="rounded border p-2" value={form.id_categoria || ""} onChange={e => setForm({ ...form, id_categoria: Number(e.target.value) })}>
            <option value="">Categoría</option>
            {tipos.map(t => <option key={t.id_categoria} value={t.id_categoria}>{t.nombre_categoria}</option>)}
          </select>
          {(["nombre_instrumento", "marca", "modelo", "tamano", "color"] as const).map(k =>
            <input key={k} required={k === "nombre_instrumento"} maxLength={k === "tamano" || k === "color" ? 50 : 100}
              aria-label={k} placeholder={k.replace("_", " ")} className="rounded border p-2"
              value={form[k] || ""} onChange={e => setForm({ ...form, [k]: e.target.value })} />)}
          <label>Precio (MXN)<input type="number" step="0.01" min="0.01" required className="block w-full rounded border p-2" value={form.precio_venta || ""} onChange={e => setForm({ ...form, precio_venta: Number(e.target.value) })} /></label>
          <label>Existencias<input type="number" step="1" min="0" required className="block w-full rounded border p-2" value={form.stock_actual} onChange={e => setForm({ ...form, stock_actual: Number(e.target.value) })} /></label>
          <label><input type="checkbox" checked={form.activo} onChange={e => setForm({ ...form, activo: e.target.checked })} /> Activo en el catálogo</label>
          <div className="flex gap-3"><button className="rounded bg-patina px-4 py-2 text-white">Guardar</button>
            {edicion && <button type="button" onClick={() => { setEdicion(undefined); setForm(vacio) }}>Cancelar</button>}</div>
        </form>
      </section>
      <section className="mt-8 rounded-xl bg-white p-6">
        <h2 className="font-heading text-2xl">Inventario</h2>
        <form className="mt-4 grid gap-3 sm:grid-cols-3" onSubmit={e => {
          e.preventDefault()
          const params = new URLSearchParams()
          Object.entries(filtros).forEach(([clave, valor]) => { if (valor && valor !== "todas") params.set(clave, valor) })
          setAplicados(params)
          void recargar(params).catch(e => setError(String(e)))
        }}>
          <input aria-label="Buscar instrumento" placeholder="Nombre o modelo" value={filtros.q} onChange={e => setFiltros({ ...filtros, q: e.target.value })} className="rounded border p-2" />
          <input aria-label="Filtrar marca" placeholder="Marca" value={filtros.marca} onChange={e => setFiltros({ ...filtros, marca: e.target.value })} className="rounded border p-2" />
          <select aria-label="Filtrar categoría" value={filtros.categoria} onChange={e => setFiltros({ ...filtros, categoria: e.target.value })} className="rounded border p-2"><option value="">Todas las categorías</option>{tipos.map(t => <option value={t.id_categoria} key={t.id_categoria}>{t.nombre_categoria}</option>)}</select>
          <select aria-label="Filtrar estado" value={filtros.activo} onChange={e => setFiltros({ ...filtros, activo: e.target.value })} className="rounded border p-2"><option value="">Todos los estados</option><option value="true">Activos</option><option value="false">Inactivos</option></select>
          <select aria-label="Filtrar existencias" value={filtros.existencias} onChange={e => setFiltros({ ...filtros, existencias: e.target.value })} className="rounded border p-2"><option value="todas">Todas las existencias</option><option value="agotados">Agotados</option><option value="disponibles">Con existencias</option></select>
          <button className="rounded bg-patina px-4 py-2 text-white">Aplicar filtros</button>
        </form>
        <p className="mt-4 text-sm text-secondary">{productos.length} instrumentos encontrados</p>
        <ul className="mt-4 space-y-4">{productos.map(p => <li key={p.id_instrumento} className="flex flex-wrap items-center gap-4 border-b pb-4">
          {p.imagen_url && <img src={p.imagen_url} alt="" className="h-16 w-16 object-cover" />}
          <span className="min-w-36">{p.nombre_instrumento} · {p.stock_actual} unidades {p.activo ? "" : "(inactivo)"}</span>
          <button className="text-patina" onClick={() => {
            setEdicion(p.id_instrumento)
            setForm({ id_categoria: p.id_categoria, nombre_instrumento: p.nombre_instrumento,
              marca: p.marca, modelo: p.modelo, tamano: p.tamano, color: p.color,
              precio_venta: Number(p.precio_venta), stock_actual: p.stock_actual, activo: p.activo })
            window.scrollTo({ top: 0, behavior: "smooth" })
          }}>Editar</button>
          {p.activo && <button className="text-red-700" onClick={() => { if (window.confirm("¿Retirar del catálogo?")) void ejecutar(() => retirarInstrumento(p.id_instrumento)) }}>Retirar</button>}
          <label className="cursor-pointer text-patina">Subir imagen
            <input type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" onChange={e => {
              const archivo = e.target.files?.[0]
              if (archivo) void ejecutar(() => subirImagen(p.id_instrumento, archivo))
              e.target.value = ""
            }} />
          </label>
        </li>)}</ul>
      </section>
    </div>
  </main>
}
