import { useEffect, useRef, useState, type FormEvent } from "react"
import { Link } from "react-router-dom"
import { useSesion } from "@/contexts/SesionContext"
import { cambiarRol, listarUsuarios, puedeAdministrar, type PaginaUsuarios, type Rol, type UsuarioAdministracion } from "@/services/usuarios"

const roles: Rol[] = ["cliente", "maestro", "administrador"]
export default function Usuarios() {
  const { autenticado, cargando: restaurando } = useSesion()
  const [acceso, setAcceso] = useState<boolean | null>(null)
  const [datos, setDatos] = useState<PaginaUsuarios | null>(null)
  const [texto, setTexto] = useState("")
  const [consulta, setConsulta] = useState({ q: "", offset: 0, revision: 0 })
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState("")
  const [mensaje, setMensaje] = useState("")
  const [pendiente, setPendiente] = useState<{ usuario: UsuarioAdministracion; rol: Rol; agregar: boolean } | null>(null)
  const [guardando, setGuardando] = useState(false)
  const bloqueo = useRef(false)
  const confirmacion = useRef<HTMLElement | null>(null)
  useEffect(() => { if (pendiente) confirmacion.current?.focus() }, [pendiente])

  useEffect(() => {
    if (restaurando || !autenticado) return

    let vigente = true

    void Promise.resolve().then(async () => {
      if (!vigente) return

      setCargando(true)
      setDatos(null)
      setError("")

      try {
        const permitido = await puedeAdministrar()
        if (!vigente) return

        setAcceso(permitido)

        if (permitido) {
          const pagina = await listarUsuarios(consulta.q, consulta.offset)
          if (vigente) setDatos(pagina)
        }
      } catch (e) {
        if (vigente) {
          setAcceso(false)
          setError(
            e instanceof Error
              ? e.message
              : "No se pudo consultar el acceso.",
          )
        }
      } finally {
        if (vigente) setCargando(false)
      }
    })

    return () => {
      vigente = false
    }
  }, [autenticado, restaurando, consulta])

  function buscar(evento: FormEvent) {
    evento.preventDefault(); setPendiente(null); setMensaje("")
    setConsulta(actual => ({ q: texto.trim(), offset: 0, revision: actual.revision + 1 }))
  }
  async function confirmar() {
    if (!pendiente || bloqueo.current) return
    bloqueo.current = true; setGuardando(true); setError(""); setMensaje("")
    try {
      const respuesta = await cambiarRol(pendiente.usuario.id_usuario, pendiente.rol, pendiente.agregar)
      setMensaje(respuesta.mensaje); setPendiente(null)
      setConsulta(actual => ({ ...actual, revision: actual.revision + 1 }))
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo actualizar el rol.")
      // No se representa el cambio como exitoso si el servidor lo rechazó.
      try {
        if (!await puedeAdministrar()) { setAcceso(false); setDatos(null); setPendiente(null) }
      } catch { setAcceso(false); setDatos(null); setPendiente(null) }
    } finally { bloqueo.current = false; setGuardando(false) }
  }

  if (restaurando) return <p role="status" className="p-8">Verificando sesión...</p>
  if (!autenticado) return <main className="p-8"><p>Inicia sesión para continuar.</p><Link to="/login" className="text-patina underline">Iniciar sesión</Link></main>
  return <main className="min-h-screen bg-ivory p-6 md:p-12">
    <div className="mx-auto max-w-6xl">
      <Link to="/inicio" className="text-patina hover:underline">Volver a mi inicio</Link>
      <h1 className="mt-5 font-heading text-4xl font-semibold">Usuarios y roles</h1>
      {cargando && <p role="status" className="mt-4">Consultando usuarios...</p>}
      {error && <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}
      {mensaje && <p role="status" className="mt-4 rounded-lg bg-emerald-50 p-3 text-patina">{mensaje}</p>}
      {acceso === false && !cargando && <p className="mt-4">Esta sección está disponible únicamente para administradores autorizados.</p>}
      {acceso === true && <>
        <p className="mt-3 text-secondary">Los usuarios pueden tener varios roles. Cada cambio requiere que la cuenta afectada vuelva a iniciar sesión.</p>
        <form onSubmit={buscar} className="my-6 flex flex-wrap items-end gap-3">
          <label className="flex-1">Buscar por nombre, usuario o correo
            <input value={texto} onChange={e => setTexto(e.target.value)} maxLength={100} className="mt-2 block w-full rounded-xl border bg-white p-3" />
          </label>
          <button disabled={guardando || cargando} className="rounded-xl bg-patina px-5 py-3 text-white disabled:opacity-50">Buscar</button>
        </form>
        {datos && <>
          <p className="mb-3 text-sm text-secondary">{datos.total} usuarios encontrados</p>
          <div className="overflow-x-auto rounded-xl border bg-white">
            <table className="w-full text-left text-sm">
              <thead className="bg-sidebar text-white"><tr><th className="p-4">Usuario</th><th className="p-4">Estado</th><th className="p-4">Roles</th></tr></thead>
              <tbody>{datos.items.map(usuario => <tr key={usuario.id_usuario} className="border-t align-top">
                <td className="p-4"><strong>{usuario.nombre}</strong><div>{usuario.nombre_usuario}</div><div className="break-all text-secondary">{usuario.correo}</div>{usuario.id_usuario === datos.id_actual && <span className="text-patina">Tu cuenta</span>}</td>
                <td className="p-4">{!usuario.vinculado ? "Sin acceso vinculado" : usuario.activo ? "Activa" : "Inactiva"}</td>
                <td className="p-4"><div className="flex flex-wrap gap-2">{roles.map(rol => {
                  const tiene = usuario.roles.includes(rol)
                  const propio = usuario.id_usuario === datos.id_actual
                  const disabled = guardando || !usuario.vinculado || (!tiene && !usuario.activo) || (propio && tiene && rol === "administrador")
                  return <button key={rol} disabled={disabled} aria-label={(tiene ? "Retirar " : "Asignar ") + rol + " a " + usuario.nombre_usuario}
                    onClick={() => { setPendiente({ usuario, rol, agregar: !tiene }); setError(""); setMensaje("") }}
                    className={"rounded-lg border px-3 py-2 disabled:opacity-50 " + (tiene ? "border-patina bg-patina/10 text-patina" : "border-ebony/20")}>
                    {tiene ? "Retirar " : "Asignar "}{rol}
                  </button>
                })}</div>{!usuario.vinculado && <p className="mt-2 text-secondary">Esta cuenta anterior todavía no puede recibir roles.</p>}</td>
              </tr>)}</tbody>
            </table>
          </div>
          {datos.items.length === 0 && <p className="p-4">No hay usuarios que coincidan con la búsqueda.</p>}
          <div className="mt-4 flex items-center gap-4">
            <button disabled={guardando || cargando || consulta.offset === 0} onClick={() => { setPendiente(null); setConsulta(v => ({ ...v, offset: Math.max(0, v.offset - 10) })) }} className="rounded-lg border p-2 disabled:opacity-40">Anterior</button>
            <span>Página {Math.floor(consulta.offset / 10) + 1}</span>
            <button disabled={guardando || cargando || consulta.offset + datos.limit >= datos.total} onClick={() => { setPendiente(null); setConsulta(v => ({ ...v, offset: v.offset + 10 })) }} className="rounded-lg border p-2 disabled:opacity-40">Siguiente</button>
          </div>
        </>}
        {pendiente && <section ref={confirmacion} tabIndex={-1} role="region" aria-label="Confirmar cambio de rol" className="mt-6 rounded-xl border border-patina bg-white p-5">
          <h2 className="font-semibold">Confirmar cambio</h2>
          <p className="mt-2">{pendiente.agregar ? "Asignar" : "Retirar"} el rol <strong>{pendiente.rol}</strong> a <strong>{pendiente.usuario.correo}</strong>.</p>
          <p className="mt-2 text-secondary">La cuenta deberá iniciar sesión nuevamente. {pendiente.agregar && pendiente.rol === "administrador" && "Podrá administrar los roles de otros usuarios."}</p>
          <div className="mt-4 flex gap-3"><button disabled={guardando} onClick={() => void confirmar()} className="rounded-lg bg-patina px-4 py-2 text-white disabled:opacity-50">{guardando ? "Guardando..." : "Confirmar"}</button><button disabled={guardando} onClick={() => setPendiente(null)} className="rounded-lg border px-4 py-2">Cancelar</button></div>
        </section>}
      </>}
    </div>
  </main>
}
