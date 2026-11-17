import { useEffect, useState } from "react"
import { consultarMetodosAcceso } from "@/services/usuarios"
import { Link } from "react-router-dom"
import { useSesion } from "@/contexts/SesionContext"
import BotonGoogle from "@/components/BotonGoogle"
import AgregarContrasena from "@/components/AgregarContrasena"

export default function Inicio() {
  const { error } = useSesion()
  const [googleVinculado, setGoogleVinculado] = useState<boolean | null>(null)
  useEffect(() => {
    let vigente = true

    void consultarMetodosAcceso()
      .then(({ google_vinculado }) => {
        if (vigente) setGoogleVinculado(google_vinculado)
      })
      .catch(() => {
        if (vigente) setGoogleVinculado(null)
      })

    return () => {
      vigente = false
    }
  }, [])
  return (
    <main className="min-h-screen bg-ivory p-6 md:p-12">

      {error && <p role="alert" className="mt-4 text-red-700">{error}</p>}

      <section className="mx-auto mt-20 max-w-3xl">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-patina">
          Tu espacio musical
        </p>
        <h1 className="mt-4 font-heading text-5xl font-semibold md:text-6xl">
          Mi cuenta
        </h1>
        <p className="mt-5 max-w-xl leading-relaxed text-secondary">
          Administra tus datos personales y tus métodos de acceso. Encontrarás tus compras, clases y áreas de trabajo en la navegación superior.
        </p>

        {googleVinculado === false && (
          <BotonGoogle vincular className="mt-8 max-w-sm" />
        )}
        <AgregarContrasena />
        <div className="mt-8 flex flex-wrap gap-4">
          <Link to="/perfil" className="rounded-xl border border-patina px-5 py-3 text-patina">Editar mi perfil</Link>
          <Link to="/catalogo" className="rounded-xl border border-patina px-5 py-3 text-patina">Ver catálogo</Link>
        </div>

      </section>
    </main>
  )
}
