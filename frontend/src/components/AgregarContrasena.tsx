import { useEffect, useState, type FormEvent } from "react"
import {
  agregarContrasena,
  obtenerMetodosAcceso,
  type MetodosAcceso,
} from "@/services/usuarios"

export default function AgregarContrasena() {
  const [metodos, setMetodos] = useState<MetodosAcceso | null>(null)
  const [clave, setClave] = useState("")
  const [confirmacion, setConfirmacion] = useState("")
  const [error, setError] = useState("")
  const [ocupado, setOcupado] = useState(false)

  useEffect(() => {
    let activo = true

    void obtenerMetodosAcceso()
      .then(datos => {
        if (activo) setMetodos(datos)
      })
      .catch(() => {
        if (activo) {
          setError("No se pudieron consultar los métodos de acceso.")
        }
      })

    return () => {
      activo = false
    }
  }, [])

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError("")

    if (
      !metodos
      || clave !== confirmacion
      || clave.length < 8
      || clave.length > 128
      || !/[A-Za-z]/.test(clave)
      || !/[0-9]/.test(clave)
    ) {
      setError(
        "Las contraseñas deben coincidir y tener entre 8 y 128 caracteres, con letras y números.",
      )
      return
    }

    setOcupado(true)

    try {
      await agregarContrasena(metodos.correo, clave)

      const actualizado = await obtenerMetodosAcceso()
      if (!actualizado.contrasena_configurada) {
        throw new Error(
          "No se confirmó la vinculación. Inténtalo nuevamente.",
        )
      }

      setMetodos(actualizado)
      setClave("")
      setConfirmacion("")
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo agregar la contraseña.",
      )
    } finally {
      setOcupado(false)
    }
  }

  if (!metodos?.google_vinculado || metodos.contrasena_configurada) {
    return null
  }

  return (
    <form onSubmit={enviar} className="mt-8 max-w-sm space-y-3">
      <h2 className="font-heading text-2xl">
        Agregar acceso con contraseña
      </h2>
      <p className="text-sm">
        Después podrás entrar con {metodos.correo} y tu contraseña.
      </p>

      <input
        type="password"
        required
        minLength={8}
        maxLength={128}
        autoComplete="new-password"
        value={clave}
        onChange={e => setClave(e.target.value)}
        placeholder="Contraseña"
        aria-label="Contraseña nueva"
        className="w-full rounded-xl border p-3"
      />

      <input
        type="password"
        required
        minLength={8}
        maxLength={128}
        autoComplete="new-password"
        value={confirmacion}
        onChange={e => setConfirmacion(e.target.value)}
        placeholder="Confirmar contraseña"
        aria-label="Confirmar contraseña nueva"
        className="w-full rounded-xl border p-3"
      />

      {error && (
        <p role="alert" className="text-red-700">
          {error}
        </p>
      )}

      <button
        disabled={ocupado}
        className="rounded-xl bg-patina px-5 py-3 text-white disabled:opacity-50"
      >
        {ocupado ? "Guardando..." : "Agregar contraseña"}
      </button>
    </form>
  )
}