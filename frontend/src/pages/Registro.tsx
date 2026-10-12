
import { useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowLeft, Music2 } from "lucide-react"
import { registrarUsuario } from "@/services/auth"

export default function Registro() {
  const navigate = useNavigate()
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState("")
  const [exito, setExito] = useState("")

  const [formulario, setFormulario] = useState({
    nombre_usuario: "",
    nombre: "",
    apellido_paterno: "",
    apellido_materno: "",
    fecha_nacimiento: "",
    curp: "",
    ine: "",
    correo: "",
    telefono: "",
    direccion: "",
    contrasena: "",
    confirmar_contrasena: "",
  })

  function actualizar(campo: keyof typeof formulario, valor: string) {
    setFormulario((actual) => ({ ...actual, [campo]: valor }))
  }

  async function manejarEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError("")
    setExito("")

    if (formulario.contrasena !== formulario.confirmar_contrasena) {
      setError("Las contraseñas no coinciden.")
      return
    }

    if (formulario.contrasena.length < 8 || formulario.contrasena.length > 128) {
      setError("La contraseña debe tener entre 8 y 128 caracteres.")
      return
    }

    setCargando(true)

    try {
      await registrarUsuario({
        nombre_usuario: formulario.nombre_usuario.trim(),
        nombre: formulario.nombre.trim(),
        apellido_paterno: formulario.apellido_paterno.trim(),
        apellido_materno: formulario.apellido_materno.trim() || null,
        fecha_nacimiento: formulario.fecha_nacimiento,
        curp: formulario.curp.trim().toUpperCase(),
        ine: formulario.ine.trim() || null,
        correo: formulario.correo.trim(),
        telefono: formulario.telefono.trim() || null,
        direccion: formulario.direccion.trim() || null,
        contrasena: formulario.contrasena,
      })

      setExito("Tu cuenta se creó correctamente. Ya puedes iniciar sesión.")
      window.setTimeout(() => navigate("/login"), 1200)
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "No fue posible crear tu cuenta.",
      )
    } finally {
      setCargando(false)
    }
  }

  const campos: {
    campo: keyof typeof formulario
    etiqueta: string
    tipo?: string
    requerido?: boolean
    maxLength?: number
  }[] = [
    { campo: "nombre_usuario", etiqueta: "Nombre de usuario", requerido: true, maxLength: 100 },
    { campo: "nombre", etiqueta: "Nombre(s)", requerido: true, maxLength: 100 },
    { campo: "apellido_paterno", etiqueta: "Apellido paterno", requerido: true, maxLength: 100 },
    { campo: "apellido_materno", etiqueta: "Apellido materno", maxLength: 100 },
    { campo: "fecha_nacimiento", etiqueta: "Fecha de nacimiento", tipo: "date", requerido: true },
    { campo: "curp", etiqueta: "CURP", requerido: true, maxLength: 18 },
    { campo: "ine", etiqueta: "INE (opcional)", maxLength: 20 },
    { campo: "correo", etiqueta: "Correo electrónico", tipo: "email", requerido: true, maxLength: 150 },
    { campo: "telefono", etiqueta: "Teléfono (opcional)", tipo: "tel", maxLength: 20 },
    { campo: "direccion", etiqueta: "Dirección (opcional)", maxLength: 255 },
    { campo: "contrasena", etiqueta: "Contraseña", tipo: "password", requerido: true, maxLength: 128 },
    { campo: "confirmar_contrasena", etiqueta: "Confirmar contraseña", tipo: "password", requerido: true, maxLength: 128 },
  ]

  return (
    <main className="min-h-screen bg-ivory px-5 py-8 md:px-10">
      <div className="mx-auto max-w-3xl">
        <Link to="/" className="inline-flex items-center gap-2 text-sm text-secondary hover:text-patina">
          <ArrowLeft size={16} />
          Volver al inicio
        </Link>

        <header className="mb-8 mt-7">
          <Link to="/" className="mb-5 inline-flex items-center gap-3">
            <span className="flex size-11 items-center justify-center rounded-full bg-patina text-brass">
              <Music2 size={23} />
            </span>
            <span className="font-heading text-2xl font-bold">DaVinciMusic</span>
          </Link>
          <h1 className="font-heading text-5xl font-semibold">Crear una cuenta</h1>
          <p className="mt-2 text-secondary">
            Completa tus datos para formar parte de nuestra comunidad musical.
          </p>
        </header>

        <form onSubmit={manejarEnvio} className="rounded-2xl border border-ebony/10 bg-white p-6 shadow-sm md:p-9">
          <h2 className="mb-5 text-xs font-bold uppercase tracking-[0.2em] text-patina">
            Datos personales y de acceso
          </h2>

          <div className="grid gap-5 sm:grid-cols-2">
            {campos.map(({ campo, etiqueta, tipo, requerido, maxLength }) => (
              <div
                key={campo}
                className={campo === "direccion" ? "sm:col-span-2" : ""}
              >
                <label htmlFor={campo} className="mb-2 block text-sm font-semibold">
                  {etiqueta}
                  {requerido && <span className="ml-1 text-patina">*</span>}
                </label>
                <input
                  id={campo}
                  type={tipo ?? "text"}
                  required={requerido}
                  maxLength={maxLength}
                  minLength={
                    campo === "nombre_usuario" ? 3 :
                    campo === "curp" ? 18 :
                    campo === "contrasena" ? 8 : undefined
                  }
                  autoComplete={
                    campo === "correo" ? "email" :
                    campo === "contrasena" ? "new-password" :
                    campo === "confirmar_contrasena" ? "new-password" :
                    campo === "nombre_usuario" ? "username" : "off"
                  }
                  value={formulario[campo]}
                  onChange={(evento) => actualizar(campo, evento.target.value)}
                  className="w-full rounded-xl border border-ebony/15 bg-ivory/50 px-4 py-3 outline-none transition focus:border-patina focus:ring-2 focus:ring-patina/15"
                />
                {campo === "curp" && (
                  <p className="mt-1 text-xs text-secondary">
                    Debe contener exactamente 18 caracteres.
                  </p>
                )}
              </div>
            ))}
          </div>

          {error && (
            <p role="alert" className="mt-5 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              {error}
            </p>
          )}

          {exito && (
            <p role="status" className="mt-5 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">
              {exito}
            </p>
          )}

          <button
            type="submit"
            disabled={cargando}
            className="mt-7 w-full rounded-xl bg-patina px-5 py-3.5 font-semibold text-white transition hover:bg-sidebar disabled:cursor-not-allowed disabled:opacity-60"
          >
            {cargando ? "Creando cuenta..." : "Crear cuenta"}
          </button>

          <p className="mt-5 text-center text-sm text-secondary">
            ¿Ya tienes una cuenta?{" "}
            <Link to="/login" className="font-semibold text-patina hover:underline">
              Inicia sesión
            </Link>
          </p>
        </form>
      </div>
    </main>
  )
}
