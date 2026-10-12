
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react"
import { useNavigate } from "react-router-dom"

const CLAVE_TOKEN = "access_token"
const TIEMPO_ADVERTENCIA = 5 * 60 * 1000

interface SesionContexto {
  token: string | null
  autenticado: boolean
  cerrarSesion: () => void
  guardarSesion: (token: string) => void
}

const ContextoSesion = createContext<SesionContexto | undefined>(undefined)

function obtenerExpiracion(token: string): number | null {
  try {
    const parte = token.split(".")[1]
    if (!parte) return null

    const base64 = parte.replace(/-/g, "+").replace(/_/g, "/")
    const datos = JSON.parse(atob(base64)) as { exp?: number }

    return typeof datos.exp === "number" ? datos.exp * 1000 : null
  } catch {
    return null
  }
}

function tokenValido(token: string | null): boolean {
  if (!token) return false

  const expiracion = obtenerExpiracion(token)
  return expiracion !== null && expiracion > Date.now()
}

export function SesionProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()

  const [token, setToken] = useState<string | null>(() => {
    const guardado = sessionStorage.getItem(CLAVE_TOKEN)
    return tokenValido(guardado) ? guardado : null
  })

  const [mostrarAdvertencia, setMostrarAdvertencia] = useState(false)

  const guardarSesion = useCallback((nuevoToken: string) => {
    if (!tokenValido(nuevoToken)) {
      throw new Error("El servidor devolvió un token inválido o vencido.")
    }

    sessionStorage.setItem(CLAVE_TOKEN, nuevoToken)
    setToken(nuevoToken)
    setMostrarAdvertencia(false)
  }, [])

  const cerrarSesion = useCallback(() => {
    sessionStorage.removeItem(CLAVE_TOKEN)
    setToken(null)
    setMostrarAdvertencia(false)
    navigate("/login", { replace: true })
  }, [navigate])

  useEffect(() => {
    if (!token) return

    const expiracion = obtenerExpiracion(token)

    if (expiracion === null || expiracion <= Date.now()) {
      cerrarSesion()
      return
    }

    const restante = expiracion - Date.now()
    const hastaAdvertencia = restante - TIEMPO_ADVERTENCIA

    const temporizadorAdvertencia =
      hastaAdvertencia > 0
        ? window.setTimeout(() => setMostrarAdvertencia(true), hastaAdvertencia)
        : null

    const temporizadorExpiracion = window.setTimeout(
      cerrarSesion,
      restante,
    )

    const comprobarExpiracion = () => {
      if (document.visibilityState !== "visible") return

      const tiempoRestante = expiracion - Date.now()

      if (tiempoRestante <= 0) {
        cerrarSesion()
      } else if (tiempoRestante <= TIEMPO_ADVERTENCIA) {
        setMostrarAdvertencia(true)
      }
    }

    document.addEventListener("visibilitychange", comprobarExpiracion)

    return () => {
      if (temporizadorAdvertencia !== null) {
        window.clearTimeout(temporizadorAdvertencia)
      }

      window.clearTimeout(temporizadorExpiracion)
      document.removeEventListener("visibilitychange", comprobarExpiracion)
    }
  }, [token, cerrarSesion])

  useEffect(() => {
    if (!mostrarAdvertencia) return

    window.alert(
      "Tu sesión está por expirar. Guarda tu trabajo; tendrás que iniciar sesión nuevamente.",
    )

    setMostrarAdvertencia(false)
  }, [mostrarAdvertencia])

  useEffect(() => {
    const manejarSesionExpirada = () => cerrarSesion()

    window.addEventListener("sesion-expirada", manejarSesionExpirada)

    return () => {
      window.removeEventListener("sesion-expirada", manejarSesionExpirada)
    }
  }, [cerrarSesion])

  const valor = useMemo(
    () => ({
      token,
      autenticado: tokenValido(token),
      cerrarSesion,
      guardarSesion,
    }),
    [token, cerrarSesion, guardarSesion],
  )

  return (
    <ContextoSesion.Provider value={valor}>
      {children}
    </ContextoSesion.Provider>
  )
}

export function useSesion() {
  const contexto = useContext(ContextoSesion)

  if (!contexto) {
    throw new Error("useSesion debe utilizarse dentro de SesionProvider.")
  }

  return contexto
}
