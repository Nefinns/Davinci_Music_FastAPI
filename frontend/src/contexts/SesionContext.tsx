import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react"
import { useNavigate } from "react-router-dom"
import { Session } from "@/lib/supertokens"
import { solicitar } from "@/services/auth"

interface SesionContexto {
  autenticado: boolean
  cargando: boolean
  error: string
  cerrarSesion: () => Promise<void>
  guardarSesion: () => Promise<void>
}
const ContextoSesion = createContext<SesionContexto | undefined>(undefined)

export function SesionProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const [autenticado, setAutenticado] = useState(false)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")

  const guardarSesion = useCallback(async () => {
    if (!await Session.doesSessionExist()) throw new Error("No se pudo establecer la sesión.")
    await solicitar("/usuarios/me", { metodo: "GET", requiereSesion: true })
    setAutenticado(true)
    setError("")
  }, [])

  const cerrarSesion = useCallback(async () => {
    setError("")
    try {
      await Session.signOut()
      setAutenticado(false)
      navigate("/login", { replace: true })
    } catch {
      setError("No se pudo cerrar la sesión en el servidor. Vuelve a intentarlo.")
    }
  }, [navigate])

  useEffect(() => {
    sessionStorage.removeItem("access_token")
    let activo = true
    const restaurar = async () => {
      try {
        const existe = await Session.doesSessionExist()
        if (existe) await solicitar("/usuarios/me", { metodo: "GET", requiereSesion: true })
        if (activo) { setAutenticado(existe); setError("") }
      } catch {
        if (activo) { setAutenticado(false); setError("No se pudo validar tu sesión. Inicia sesión nuevamente.") }
      } finally {
        if (activo) setCargando(false)
      }
    }
    void restaurar()
    const expirada = () => { setAutenticado(false); navigate("/login", { replace: true }) }
    const visible = () => { if (document.visibilityState === "visible") void restaurar() }
    window.addEventListener("sesion-expirada", expirada)
    document.addEventListener("visibilitychange", visible)
    return () => { activo = false; window.removeEventListener("sesion-expirada", expirada); document.removeEventListener("visibilitychange", visible) }
  }, [navigate])

  const valor = useMemo(() => ({ autenticado, cargando, error, cerrarSesion, guardarSesion }),
    [autenticado, cargando, error, cerrarSesion, guardarSesion])
  return <ContextoSesion.Provider value={valor}>{children}</ContextoSesion.Provider>
}
export function useSesion() {
  const contexto = useContext(ContextoSesion)
  if (!contexto) throw new Error("useSesion debe utilizarse dentro de SesionProvider.")
  return contexto
}
