import { useEffect, useState, type FormEvent } from "react"
import { Link } from "react-router-dom"
import { solicitar } from "@/services/auth"

interface DatosPerfil {
  nombre_usuario: string
  nombre: string
  apellido_paterno: string
  apellido_materno: string | null
  telefono?: string | null
  direccion?: string | null
  correo: string
}

export default function Perfil() {
  const [perfil, setPerfil] = useState<DatosPerfil | null>(null)
  const [error, setError] = useState("")
  const [guardado, setGuardado] = useState(false)
  useEffect(() => {
    void solicitar<DatosPerfil>("/usuarios/me", { metodo: "GET", requiereSesion: true })
      .then(setPerfil).catch(e => setError(String(e)))
  }, [])
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
    </div>
  </main>
}
