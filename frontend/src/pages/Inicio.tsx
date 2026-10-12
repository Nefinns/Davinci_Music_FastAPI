
import { Link } from "react-router-dom"
import { Music2, LogOut } from "lucide-react"
import { useSesion } from "@/contexts/SesionContext"

export default function Inicio() {
  const { cerrarSesion } = useSesion()

  return (
    <main className="min-h-screen bg-ivory p-6 md:p-12">
      <header className="flex items-center justify-between gap-4">
        <Link to="/" className="flex items-center gap-3">
          <Music2 className="text-patina" size={28} />
          <span className="font-heading text-3xl font-bold">
            DaVinciMusic
          </span>
        </Link>

        <button
          onClick={cerrarSesion}
          className="inline-flex items-center gap-2 rounded-full border border-ebony/15 px-4 py-2 text-sm font-semibold transition hover:border-patina hover:text-patina"
        >
          <LogOut size={16} />
          Cerrar sesión
        </button>
      </header>

      <section className="mx-auto mt-20 max-w-3xl">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-patina">
          Tu espacio musical
        </p>
        <h1 className="mt-4 font-heading text-5xl font-semibold md:text-6xl">
          Bienvenido a DaVinciMusic.
        </h1>
        <p className="mt-5 max-w-xl leading-relaxed text-secondary">
          Tu acceso se ha completado. Aquí construiremos el espacio personal
          para las funciones de la tienda y la escuela de música.
        </p>
      </section>
    </main>
  )
}
