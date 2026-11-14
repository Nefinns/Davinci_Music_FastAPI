import { useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useSesion } from "@/contexts/SesionContext"
import {
  completarRegistroGoogle,
  type RegistroGoogle,
} from "@/services/google"
import { PATRON_CURP, limitesNacimiento } from "@/lib/validaciones"

const inicial: RegistroGoogle = {
  nombre_usuario: "",
  nombre: "",
  apellido_paterno: "",
  apellido_materno: null,
  fecha_nacimiento: "",
  curp: "",
  ine: null,
  telefono: null,
  direccion: null,
}

export default function CompletarPerfilGoogle() {
  const navigate = useNavigate()
  const { autenticado, estadoPerfil, guardarSesion } = useSesion()
  const [datos, setDatos] = useState<RegistroGoogle>(inicial)
  const [error, setError] = useState("")
  const [cargando, setCargando] = useState(false)
  const limites = limitesNacimiento()

  function cambiar(campo: keyof RegistroGoogle, valor: string) {
    setDatos((actual) => ({
      ...actual,
      [campo]: campo === "curp"
        ? valor.toUpperCase().replace(/[^A-Z0-9]/g, "")
        : valor,
    }))
  }

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError("")
    setCargando(true)

    try {
      await completarRegistroGoogle({
        ...datos,
        nombre_usuario: datos.nombre_usuario.trim(),
        nombre: datos.nombre.trim(),
        apellido_paterno: datos.apellido_paterno.trim(),
        curp: datos.curp.trim(),
        apellido_materno: datos.apellido_materno?.trim() || null,
        ine: datos.ine?.trim() || null,
        telefono: datos.telefono?.trim() || null,
        direccion: datos.direccion?.trim() || null,
      })
      const estado = await guardarSesion()
      if (estado.estado !== "completo") {
        throw new Error("El perfil aún no está listo. Inténtalo nuevamente.")
      }
      navigate("/inicio", { replace: true })
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo completar el registro.",
      )
    } finally {
      setCargando(false)
    }
  }

  if (!autenticado) {
    return <main className="p-8">Inicia sesión con Google para continuar. <Link to="/login">Ir a login</Link></main>
  }
  if (estadoPerfil?.estado === "completo") {
    return <main className="p-8">Tu perfil ya está completo. <Link to="/inicio">Ir a inicio</Link></main>
  }
  if (estadoPerfil?.estado === "vincular_cuenta") {
    return <main className="p-8">Ese correo ya pertenece a otra cuenta. Inicia sesión con el método existente y vincula Google desde allí.</main>
  }

  const campos: {
    nombre: keyof RegistroGoogle
    etiqueta: string
    obligatorio?: boolean
    tipo?: string
    maxLength: number
  }[] = [
    { nombre: "nombre_usuario", etiqueta: "Nombre de usuario", obligatorio: true, maxLength: 100 },
    { nombre: "nombre", etiqueta: "Nombre", obligatorio: true, maxLength: 100 },
    { nombre: "apellido_paterno", etiqueta: "Apellido paterno", obligatorio: true, maxLength: 100 },
    { nombre: "apellido_materno", etiqueta: "Apellido materno", maxLength: 100 },
    { nombre: "fecha_nacimiento", etiqueta: "Fecha de nacimiento", obligatorio: true, tipo: "date", maxLength: 10 },
    { nombre: "curp", etiqueta: "CURP", obligatorio: true, maxLength: 18 },
    { nombre: "ine", etiqueta: "INE", maxLength: 20 },
    { nombre: "telefono", etiqueta: "Teléfono", tipo: "tel", maxLength: 20 },
    { nombre: "direccion", etiqueta: "Dirección", maxLength: 255 },
  ]

  return (
    <main className="min-h-screen bg-ivory p-6 md:p-12">
      <div className="mx-auto max-w-2xl rounded-2xl bg-white p-6 md:p-9">
        <h1 className="font-heading text-4xl">Completar mi perfil</h1>
        <p className="mt-3 text-secondary">
          Necesitamos estos datos cuando quieras comprar o inscribirte.
        </p>
        <form onSubmit={enviar} className="mt-8 grid gap-5 sm:grid-cols-2">
          {campos.map(({ nombre, etiqueta, obligatorio, tipo, maxLength }) => (
            <label key={nombre} className="block text-sm font-semibold">
              {etiqueta}
              <input
                type={tipo || "text"}
                required={obligatorio}
                minLength={nombre === "nombre_usuario" ? 3 : nombre === "curp" ? 18 : undefined}
                maxLength={maxLength}
                min={nombre === "fecha_nacimiento" ? limites.min : undefined}
                max={nombre === "fecha_nacimiento" ? limites.max : undefined}
                pattern={nombre === "curp" ? PATRON_CURP : undefined}
                value={datos[nombre] ?? ""}
                onChange={(evento) => cambiar(nombre, evento.target.value)}
                className="mt-2 w-full rounded-xl border border-ebony/15 px-4 py-3"
              />
            </label>
          ))}
          {error && <p role="alert" className="text-red-700 sm:col-span-2">{error}</p>}
          <div className="flex items-center gap-4 sm:col-span-2">
            <button disabled={cargando} className="rounded-xl bg-patina px-5 py-3 text-white disabled:opacity-60">
              {cargando ? "Guardando..." : "Completar registro"}
            </button>
            <Link to="/" className="text-patina underline">Seguir explorando</Link>
          </div>
        </form>
      </div>
    </main>
  )
}