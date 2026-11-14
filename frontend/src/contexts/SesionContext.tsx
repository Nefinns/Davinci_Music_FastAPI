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
import { Session } from "@/lib/supertokens"
import {
  consultarEstadoPerfil,
  type EstadoPerfil,
} from "@/services/google"

interface SesionContexto {
  autenticado: boolean
  cargando: boolean
  error: string
  estadoPerfil: EstadoPerfil | null
  cerrarSesion: () => Promise<void>
  guardarSesion: () => Promise<EstadoPerfil>
}

const ContextoSesion = createContext<SesionContexto | undefined>(undefined)

export function SesionProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const [autenticado, setAutenticado] = useState(false)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")
  const [estadoPerfil, setEstadoPerfil] = useState<EstadoPerfil | null>(null)

  const guardarSesion = useCallback(async (): Promise<EstadoPerfil> => {
    if (!(await Session.doesSessionExist())) {
      throw new Error("No se pudo establecer la sesión.")
    }

    const estado = await consultarEstadoPerfil()
    setEstadoPerfil(estado)
    setAutenticado(true)
    setError("")
    return estado
  }, [])

  const cerrarSesion = useCallback(async () => {
    setError("")
    try {
      await Session.signOut()
      setAutenticado(false)
      setEstadoPerfil(null)
      navigate("/login", { replace: true })
    } catch {
      setError(
        "No se pudo cerrar la sesión en el servidor. Vuelve a intentarlo.",
      )
    }
  }, [navigate])

  useEffect(() => {
    sessionStorage.removeItem("access_token")
    let activo = true

    const restaurar = async () => {
      try {
        const existe = await Session.doesSessionExist()

        if (!existe) {
          if (activo) {
            setAutenticado(false)
            setEstadoPerfil(null)
            setError("")
          }
          return
        }

        const estado = await consultarEstadoPerfil()
        if (activo) {
          setEstadoPerfil(estado)
          setAutenticado(true)
          setError("")
        }
      } catch {
        if (activo) {
          setAutenticado(false)
          setEstadoPerfil(null)
          setError(
            "No se pudo validar tu sesión. Inicia sesión nuevamente.",
          )
        }
      } finally {
        if (activo) setCargando(false)
      }
    }

    void restaurar()

    const expirada = () => {
      setAutenticado(false)
      setEstadoPerfil(null)
      navigate("/login", { replace: true })
    }

    const visible = () => {
      if (document.visibilityState === "visible") {
        void restaurar()
      }
    }

    window.addEventListener("sesion-expirada", expirada)
    document.addEventListener("visibilitychange", visible)

    return () => {
      activo = false
      window.removeEventListener("sesion-expirada", expirada)
      document.removeEventListener("visibilitychange", visible)
    }
  }, [navigate])

  const valor = useMemo(
    () => ({
      autenticado,
      cargando,
      error,
      estadoPerfil,
      cerrarSesion,
      guardarSesion,
    }),
    [
      autenticado,
      cargando,
      error,
      estadoPerfil,
      cerrarSesion,
      guardarSesion,
    ],
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
    throw new Error(
      "useSesion debe utilizarse dentro de SesionProvider.",
    )
  }
  return contexto
}