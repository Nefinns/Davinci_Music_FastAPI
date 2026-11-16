import { useEffect, useState, type FormEvent } from "react"
import { Link } from "react-router-dom"
import { solicitar } from "@/services/auth"
import { API_URL, Session } from "@/lib/supertokens"

interface DatosPerfil {
  nombre_usuario: string
  nombre: string
  apellido_paterno: string
  apellido_materno: string | null
  telefono?: string | null
  direccion?: string | null
  correo: string
  imagen_url: string | null
}

export default function Perfil() {
  const [perfil, setPerfil] = useState<DatosPerfil | null>(null)
  const [error, setError] = useState("")
  const [guardado, setGuardado] = useState(false)
  const [subiendo, setSubiendo] = useState(false)
  const [bajaPendiente, setBajaPendiente] = useState(false)
  const [bajaEnCurso, setBajaEnCurso] = useState(false)
  const [puedeDarBaja, setPuedeDarBaja] = useState(false)
  useEffect(() => {
    void solicitar<DatosPerfil>("/usuarios/me", { metodo: "GET", requiereSesion: true })
      .then(setPerfil).catch(e => setError(String(e)))
    void solicitar<string[]>("/usuarios/me/roles", { metodo: "GET", requiereSesion: true })
      .then(roles => setPuedeDarBaja(!roles.some(rol => rol === "administrador" || rol === "maestro")))
      .catch(e => setError(String(e)))
  }, [])
  async function subirFoto(archivo: File) {
    setSubiendo(true); setError("")
    try {
      if (!await Session.doesSessionExist()) throw new Error("Tu sesión ha terminado.")
      const datos = new FormData()
      datos.append("archivo", archivo)
      const respuesta = await fetch(`${API_URL}/usuarios/me/imagen`, {
        method: "POST", credentials: "include", headers: { rid: "session" }, body: datos,
      })
      const contenido = await respuesta.json()
      if (!respuesta.ok) throw new Error(contenido.detail || "No se pudo subir la foto.")
      setPerfil(contenido as DatosPerfil)
      window.dispatchEvent(new Event("davincimusic:perfil-actualizado"))
    } catch (e) { setError(e instanceof Error ? e.message : String(e)) }
    finally { setSubiendo(false) }
  }
  async function darBaja() {
    setBajaEnCurso(true); setError("")
    try {
      await solicitar("/usuarios/me/baja", {
        metodo: "POST", requiereSesion: true, datos: { confirmar: true },
      })
      window.location.assign("/")
    } catch (e) { setError(e instanceof Error ? e.message : String(e)); setBajaEnCurso(false) }
  }
  async function guardar(e: FormEvent) {
    e.preventDefault()
    if (!perfil) return
    setError(""); setGuardado(false)
    try {
      const actualizado = await solicitar<DatosPerfil>("/usuarios/me", {
        metodo: "PATCH", requiereSesion: true,
        datos: {
          nombre_usuario: perfil.nombre_usuario,
          nombre: perfil.nombre,
          apellido_paterno: perfil.apellido_paterno,
          apellido_materno: perfil.apellido_materno,
          telefono: perfil.telefono,
          direccion: perfil.direccion,
        },
      })
      setPerfil({ ...perfil, ...actualizado }); setGuardado(true)
    } catch (e) { setError(e instanceof Error ? e.message : String(e)) }
  }
  return <main className="min-h-screen bg-ivory p-6 text-ebony">
    <div className="mx-auto max-w-xl">
      <Link to="/inicio" className="text-patina">← Mi cuenta</Link>
      <h1 className="mt-8 font-heading text-4xl">Mi perfil</h1>
      {error && <p role="alert" className="mt-4 text-red-700">{error}</p>}
      {guardado && <p role="status" className="mt-4 text-green-700">Perfil actualizado.</p>}
      {perfil && <section className="mt-8 rounded-xl bg-white p-6">
        <h2 className="font-heading text-2xl">Foto de perfil</h2>
        {perfil.imagen_url && <img src={perfil.imagen_url} alt="Tu foto de perfil" className="mt-4 h-32 w-32 rounded-full object-cover" />}
        <div className="mt-4">
          <input
            id="foto-perfil"
            className="peer sr-only"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            disabled={subiendo}
            onChange={e => {
              const archivo = e.target.files?.[0]
              if (archivo) void subirFoto(archivo)
              e.target.value = ""
            }}
          />
          <label
            htmlFor="foto-perfil"
            className="inline-flex cursor-pointer items-center rounded-lg bg-patina px-5 py-3 font-semibold text-white shadow-sm transition hover:bg-sidebar peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-patina peer-disabled:cursor-not-allowed peer-disabled:opacity-50"
          >
            {subiendo ? "Subiendo foto..." : perfil.imagen_url ? "Cambiar foto" : "Seleccionar foto"}
          </label>
          <p className="mt-2 text-sm text-secondary">
            JPG, PNG o WebP · máximo 5 MB
          </p>
        </div>
        {subiendo && <p role="status">Subiendo foto...</p>}
      </section>}
      {perfil && <form onSubmit={guardar} className="mt-8 space-y-4 rounded-xl bg-white p-6">
        <p>Correo: {perfil.correo}</p>
        {(["nombre_usuario", "nombre", "apellido_paterno", "apellido_materno", "telefono", "direccion"] as const).map(campo =>
          <label key={campo} className="block capitalize">{campo.replace("_", " ")}
            <input value={perfil[campo] || ""} required={["nombre_usuario", "nombre", "apellido_paterno"].includes(campo)}
              maxLength={campo === "direccion" ? 255 : campo === "telefono" ? 20 : 100}
              className="mt-1 block w-full rounded-lg border p-3"
              onChange={e => setPerfil({ ...perfil, [campo]: e.target.value })} />
          </label>)}
        <button className="rounded-lg bg-patina px-5 py-3 text-white">Guardar cambios</button>
      </form>}
      {puedeDarBaja && <section className="mt-8 rounded-xl border border-red-200 bg-white p-6">
        <h2 className="font-heading text-2xl">Dar de baja mi cuenta</h2>
        <p className="mt-3 text-secondary">Se desactivará tu acceso y se conservarán tus registros. Esto no te da de baja de una clase: solicita la baja de clases a un administrador.</p>
        {!bajaPendiente ? <button className="mt-4 rounded-lg border border-red-700 px-4 py-2 text-red-700" onClick={() => setBajaPendiente(true)}>Dar de baja mi cuenta</button>
          : <div className="mt-4 flex flex-wrap gap-3"><button disabled={bajaEnCurso} className="rounded-lg bg-red-700 px-4 py-2 text-white disabled:opacity-50" onClick={() => void darBaja()}>Confirmar baja de cuenta</button><button disabled={bajaEnCurso} onClick={() => setBajaPendiente(false)}>Cancelar</button></div>}
      </section>}
    </div>
  </main>
}

