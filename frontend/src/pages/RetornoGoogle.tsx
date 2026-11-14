import { useEffect, useRef, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useSesion } from "@/contexts/SesionContext"
import { finalizarAccesoGoogle } from "@/services/google"

export default function RetornoGoogle() {
  const navigate = useNavigate()
  const { guardarSesion, cerrarSesion } = useSesion()
  const [error, setError] = useState("")
  const iniciado = useRef(false)

  useEffect(() => {
    if (iniciado.current) return
    iniciado.current = true

    async function finalizar() {
      try {
        await finalizarAccesoGoogle()
        const estado = await guardarSesion()

        if (estado.estado === "completo") {
          navigate("/inicio", { replace: true })
        } else if (estado.estado === "pendiente") {
          navigate("/", { replace: true })
        } else {
          setError(
            "Ya existe un perfil con ese correo. Inicia sesión con tu método actual y vincula Google desde tu cuenta.",
          )
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "No se pudo completar el acceso con Google.",
        )
      }
    }

    void finalizar()
  }, [guardarSesion, navigate])

  return (
    <main className="flex min-h-screen items-center justify-center bg-ivory p-6">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center">
        {error ? (
          <>
            <h1 className="font-heading text-3xl">
              No se completó el acceso
            </h1>
            <p role="alert" className="mt-4 text-red-700">
              {error}
            </p>
            <button
              type="button"
              onClick={() => void cerrarSesion()}
              className="mt-6 text-patina underline"
            >
              Cerrar esta sesión e iniciar con mi cuenta existente
            </button>
            <p className="mt-3">
              <Link to="/" className="text-secondary underline">
                Volver al inicio
              </Link>
            </p>
          </>
        ) : (
          <p role="status">Terminando el acceso con Google...</p>
        )}
      </div>
    </main>
  )
}