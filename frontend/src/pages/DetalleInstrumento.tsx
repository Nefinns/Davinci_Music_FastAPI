import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { agregarCarrito } from '@/services/carrito'
import { detalle, type Instrumento } from "@/services/catalogo"

export default function DetalleInstrumento() {
  const { id } = useParams()
  const [instrumento, setInstrumento] = useState<Instrumento | null>(null)
  const [mensaje,setMensaje] = useState('')
  const [error, setError] = useState("")
  useEffect(() => {
    let vigente = true
    void detalle(Number(id)).then(valor => { if (vigente) setInstrumento(valor) })
      .catch(e => { if (vigente) setError(String(e)) })
    return () => { vigente = false }
  }, [id])
  return <main className="min-h-screen bg-ivory p-6 text-ebony">
    <div className="mx-auto max-w-5xl"><Link to="/catalogo" className="text-patina">← Volver al catálogo</Link>
      {error && <p role="alert" className="mt-8">{error}</p>}
      {instrumento && <article className="mt-10 grid gap-10 md:grid-cols-2">
        {instrumento.imagen_url ? <img src={instrumento.imagen_url} alt={instrumento.nombre_instrumento} className="w-full rounded-2xl object-cover" /> : <div className="flex h-80 items-center justify-center bg-slate-100">Sin imagen</div>}
        <div><p>{instrumento.nombre_categoria}</p><h1 className="mt-2 font-heading text-5xl">{instrumento.nombre_instrumento}</h1>
          <p className="mt-6 text-3xl">{Number(instrumento.precio_venta).toLocaleString("es-MX", { style: "currency", currency: "MXN" })}</p>
          <dl className="mt-6 space-y-2">
            <div>Marca: {instrumento.marca || "No especificada"}</div><div>Modelo: {instrumento.modelo || "No especificado"}</div>
            <div>Tamaño: {instrumento.tamano || "No especificado"}</div><div>Color: {instrumento.color || "No especificado"}</div>
            <div>Disponibilidad: {instrumento.stock_actual > 0 ? `${instrumento.stock_actual} en inventario` : "Agotado"}</div>
          </dl>
          <div className="mt-6 flex flex-wrap items-center gap-4"><button disabled={!instrumento.stock_actual} className="rounded-xl bg-patina px-5 py-3 font-semibold text-white disabled:opacity-50" onClick={()=>{try{agregarCarrito(instrumento);setMensaje('Instrumento añadido al carrito.');setError('')}catch(e){setError(String(e))}}}>Añadir al carrito</button><Link to="/carrito" className="text-patina underline">Ver carrito</Link></div>
          {mensaje&&<p role="status" className="mt-3 text-patina">{mensaje}</p>}
        </div>
      </article>}
    </div>
  </main>
}
