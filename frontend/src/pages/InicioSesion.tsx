
import { useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowLeft, Eye, EyeOff, Music2 } from "lucide-react"
import { iniciarSesion } from "@/services/auth"
import { useSesion } from "@/contexts/SesionContext"

export default function InicioSesion() {
  const navigate = useNavigate()
  const { guardarSesion } = useSesion()

  const [correo, setCorreo] = useState("")
  const [contrasena, setContrasena] = useState("")
  const [mostrarContrasena, setMostrarContrasena] = useState(false)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState("")

  async function manejarEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError("")
    setCargando(true)

    try {
      const respuesta = await iniciarSesion({ correo, contrasena })

      guardarSesion(respuesta.access_token)
      navigate("/inicio", { replace: true })
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "No fue posible iniciar sesión.",
      )
    } finally {
      setCargando(false)
    }
  }

  return (
    <main className="grid min-h-screen bg-ivory md:grid-cols-2">
      <section className="flex flex-col justify-between bg-sidebar p-8 text-white md:p-12">
        <Link to="/" className="flex items-center gap-3">
          <Music2 className="text-brass" size={30} />
          <span className="font-heading text-3xl font-semibold">
            DaVinciMusic
          </span>
        </Link>

        <div className="my-16 max-w-lg">
          <p className="mb-5 text-xs uppercase tracking-[0.25em] text-brass">
            Tu mundo musical
          </p>
          <h1 className="font-heading text-5xl leading-tight md:text-6xl">
            Cada nota te acerca a algo extraordinario.
          </h1>
          <p className="mt-6 max-w-md leading-relaxed text-white/70">
            Accede a tu espacio para aprender, descubrir instrumentos y
            continuar tu camino musical.
          </p>
        </div>

        <p className="text-sm text-white/50">
          Arte · Música · Aprendizaje
        </p>
      </section>

      <section className="flex items-center justify-center px-6 py-12 md:px-12">
        <div className="w-full max-w-md">
          <Link
            to="/"
            className="mb-10 inline-flex items-center gap-2 text-sm text-secondary hover:text-patina"
          >
            <ArrowLeft size={16} />
            Volver al inicio
          </Link>

          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-patina">
            Bienvenido de nuevo
          </p>
          <h2 className="mt-3 font-heading text-5xl font-semibold">
            Iniciar sesión
          </h2>
          <p className="mt-3 text-secondary">
            Ingresa tus datos para continuar.
          </p>

          <form onSubmit={manejarEnvio} className="mt-9 space-y-5">
            <div>
              <label htmlFor="correo" className="mb-2 block text-sm font-semibold">
                Correo electrónico
              </label>
              <input
                id="correo"
                type="email"
                autoComplete="email"
                required
                maxLength={150}
                value={correo}
                onChange={(evento) => setCorreo(evento.target.value)}
                className="w-full rounded-xl border border-ebony/15 bg-white px-4 py-3 outline-none transition focus:border-patina focus:ring-2 focus:ring-patina/15"
                placeholder="tu@correo.com"
              />
            </div>

            <div>
              <label htmlFor="contrasena" className="mb-2 block text-sm font-semibold">
                Contraseña
              </label>
              <div className="relative">
                <input
                  id="contrasena"
                  type={mostrarContrasena ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  maxLength={128}
                  value={contrasena}
                  onChange={(evento) => setContrasena(evento.target.value)}
                  className="w-full rounded-xl border border-ebony/15 bg-white px-4 py-3 pr-12 outline-none transition focus:border-patina focus:ring-2 focus:ring-patina/15"
                  placeholder="Tu contraseña"
                />
                <button
                  type="button"
                  aria-label={
                    mostrarContrasena
                      ? "Ocultar contraseña"
                      : "Mostrar contraseña"
                  }
                  onClick={() => setMostrarContrasena(!mostrarContrasena)}
                  className="absolute inset-y-0 right-0 flex items-center px-4 text-secondary"
                >
                  {mostrarContrasena ? <EyeOff size={19} /> : <Eye size={19} />}
                </button>
              </div>
            </div>

            <div className="text-right">
              <Link
                to="/recuperar-contrasena"
                className="text-sm font-semibold text-patina hover:underline"
              >
                ¿Olvidaste tu contraseña?
              </Link>
            </div>

            {error && (
              <p
                role="alert"
                className="rounded-lg bg-red-50 p-3 text-sm text-red-700"
              >
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={cargando}
              className="w-full rounded-xl bg-patina px-5 py-3.5 font-semibold text-white transition hover:bg-sidebar disabled:cursor-not-allowed disabled:opacity-60"
            >
              {cargando ? "Ingresando..." : "Iniciar sesión"}
            </button>
          </form>

          <p className="mt-7 text-center text-sm text-secondary">
            ¿Todavía no tienes cuenta?{" "}
            <Link
              to="/registro"
              className="font-semibold text-patina hover:underline"
            >
              Crear cuenta
            </Link>
          </p>
        </div>
      </section>
    </main>
  )
}
