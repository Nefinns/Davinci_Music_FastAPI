import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { Session } from "@/lib/supertokens"
import { ErrorSolicitud } from "@/services/auth"
import { esLimiteRenovacion } from "@/lib/erroresSesion"
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
  guardarSesion: (
    accion?: () => Promise<unknown>,
  ) => Promise<EstadoPerfil>
}

const ContextoSesion = createContext<SesionContexto | undefined>(undefined)

function esSesionRechazada(error: unknown) {
  return (
    (error instanceof ErrorSolicitud &&
      [401, 403].includes(error.estado)) ||
    esLimiteRenovacion(error) ||
    (error instanceof Error && esLimiteRenovacion(error.cause))
  )
}

export function SesionProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  const [autenticado, setAutenticado] = useState(false)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")
  const [estadoPerfil, setEstadoPerfil] = useState<EstadoPerfil | null>(null)

  const revision = useRef(0)
  const operando = useRef(false)
  const restauracion = useRef<number | null>(null)

  const guardarSesion = useCallback(
    async (
      accion?: () => Promise<unknown>,
    ): Promise<EstadoPerfil> => {
      if (operando.current) {
        throw new Error("Ya hay una operación de sesión en curso.")
      }

      operando.current = true
      const turno = ++revision.current
      setError("")

      try {
        if (accion) await accion()

        if (!(await Session.doesSessionExist())) {
          throw new ErrorSolicitud(
            "No se pudo establecer la sesión.",
            401,
          )
        }

        const estado = await consultarEstadoPerfil()

        if (turno !== revision.current) {
          throw new Error(
            "El intento de acceso dejó de estar vigente. Inténtalo nuevamente.",
          )
        }

        setEstadoPerfil(estado)
        setAutenticado(true)

        return estado
      } catch (err) {
        if (turno === revision.current) {
          if (esSesionRechazada(err)) {
            setAutenticado(false)
            setEstadoPerfil(null)
          }

          setError(
            err instanceof Error
              ? err.message
              : "No se pudo consultar tu perfil.",
          )
        }

        throw err
      } finally {
        operando.current = false
        if (turno === revision.current) setCargando(false)
      }
    },
    [],
  )

  const cerrarSesion = useCallback(async () => {
    if (operando.current) return

    operando.current = true
    const turno = ++revision.current
    setError("")

    try {
      await Session.signOut()

      if (turno === revision.current) {
        setAutenticado(false)
        setEstadoPerfil(null)
        navigate("/login", { replace: true })
      }
    } catch {
      setError("No se pudo cerrar la sesión. Vuelve a intentarlo.")
    } finally {
      operando.current = false
      if (turno === revision.current) setCargando(false)
    }
  }, [navigate])

  useEffect(() => {
    sessionStorage.removeItem("access_token")

    // RetornoGoogle finaliza y valida esta sesión.
    if (pathname === "/auth/callback/google") return

    let vigente = true

    async function restaurar() {
      if (
        !vigente ||
        operando.current ||
        restauracion.current !== null
      ) {
        return
      }

      const turno = ++revision.current
      restauracion.current = turno

      const actual = () =>
        vigente && turno === revision.current

      try {
        const existe = await Session.doesSessionExist()
        if (!actual()) return

        if (!existe) {
          setAutenticado(false)
          setEstadoPerfil(null)
          setError("")
          return
        }

        const estado = await consultarEstadoPerfil()
        if (!actual()) return

        setAutenticado(true)
        setEstadoPerfil(estado)
        setError("")
      } catch (err) {
        if (!actual()) return

        if (esSesionRechazada(err)) {
          setAutenticado(false)
          setEstadoPerfil(null)
        }

        setError(
          err instanceof Error
            ? err.message
            : "No se pudo consultar tu perfil.",
        )
      } finally {
        if (restauracion.current === turno) {
          restauracion.current = null
        }

        if (actual()) setCargando(false)
      }
    }

    const visible = () => {
      if (document.visibilityState === "visible") {
        void restaurar()
      }
    }

    // El evento podría proceder de una solicitud anterior.
    // Comprobamos la sesión actual antes de cambiar su estado.
    const expirada = () => {
      void restaurar()
    }

    void restaurar()

    window.addEventListener("sesion-expirada", expirada)
    document.addEventListener("visibilitychange", visible)

    return () => {
      vigente = false
      restauracion.current = null
      window.removeEventListener("sesion-expirada", expirada)
      document.removeEventListener("visibilitychange", visible)
    }
  }, [pathname])

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