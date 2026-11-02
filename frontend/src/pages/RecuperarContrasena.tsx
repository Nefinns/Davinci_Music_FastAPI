import { useState, type FormEvent } from "react"
import { Link } from "react-router-dom"
import { solicitarRecuperacion, restablecerContrasena } from "@/services/auth"

export default function RecuperarContrasena({ restablecer = false }: { restablecer?: boolean }) {
  const [correo, setCorreo] = useState("")
  const [clave, setClave] = useState("")
  const [confirmacion, setConfirmacion] = useState("")
  const [mensaje, setMensaje] = useState("")
  const [error, setError] = useState("")
  const [cargando, setCargando] = useState(false)
  const [token] = useState(() => new URLSearchParams(window.location.search).get("token") || "")
  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    setError(""); setMensaje("")
    if (restablecer && (!token || clave !== confirmacion)) {
      setError(!token ? "Falta el enlace de recuperación." : "Las contraseñas no coinciden."); return
    }
    if (restablecer && (!/[A-Za-z]/.test(clave) || !/[0-9]/.test(clave))) {
      setError("La contraseña debe incluir letras y números."); return
    }
    setCargando(true)
    try {
      if (restablecer) {
        await restablecerContrasena(token, clave)
        window.history.replaceState({}, "", window.location.pathname)
        setMensaje("Contraseña actualizada. Ya puedes iniciar sesión.")
      } else {
        await solicitarRecuperacion(correo)
        setMensaje("Si existe una cuenta activa, recibirás un enlace de recuperación.")
      }
    } catch (e) { setError(e instanceof Error ? e.message : "No se pudo completar la solicitud.") }
    finally { setCargando(false) }
  }
  return <main className="min-h-screen bg-ivory px-6 py-16">
    <div className="mx-auto max-w-md rounded-2xl bg-white p-8 shadow-sm">
      <h1 className="font-heading text-4xl">{restablecer ? "Nueva contraseña" : "Recuperar acceso"}</h1>
      <form onSubmit={enviar} className="mt-6 space-y-5">
        {!restablecer ? <label className="block">Correo electrónico
          <input type="email" required maxLength={150} autoComplete="email" value={correo} onChange={e => setCorreo(e.target.value)} className="mt-2 w-full rounded-xl border p-3" />
        </label> : <>
          <label className="block">Nueva contraseña
            <input type="password" required minLength={8} maxLength={128} autoComplete="new-password" value={clave} onChange={e => setClave(e.target.value)} className="mt-2 w-full rounded-xl border p-3" />
          </label>
          <p className="text-sm text-secondary">Entre 8 y 128 caracteres, con letras y números.</p>
          <label className="block">Confirmar contraseña
            <input type="password" required minLength={8} maxLength={128} autoComplete="new-password" value={confirmacion} onChange={e => setConfirmacion(e.target.value)} className="mt-2 w-full rounded-xl border p-3" />
          </label>
        </>}
        {error && <p role="alert" className="text-red-700">{error}</p>}
        {mensaje && <p role="status" className="text-patina">{mensaje}</p>}
        <button disabled={cargando || Boolean(restablecer && mensaje)} className="w-full rounded-xl bg-patina p-3 text-white disabled:opacity-60">{cargando ? "Procesando..." : restablecer ? "Guardar contraseña" : "Enviar enlace"}</button>
      </form>
      <Link to="/login" className="mt-6 block text-patina">Volver a iniciar sesión</Link>
    </div>
  </main>
}
