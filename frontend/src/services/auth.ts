
const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "")

const CLAVE_TOKEN = "access_token"

export interface UsuarioRegistro {
  nombre_usuario: string
  nombre: string
  apellido_paterno: string
  apellido_materno?: string | null
  fecha_nacimiento: string
  curp: string
  ine?: string | null
  correo: string
  telefono?: string | null
  direccion?: string | null
  contrasena: string
}

export interface UsuarioLogin {
  correo: string
  contrasena: string
}

export interface TokenRespuesta {
  access_token: string
  token_type: string
}

export interface UsuarioRespuesta {
  id_usuario: number
  nombre_usuario: string
  nombre: string
  apellido_paterno: string
  apellido_materno: string | null
  fecha_nacimiento: string
  curp: string
  ine: string | null
  correo: string
  telefono: string | null
  direccion: string | null
  activo: boolean
  fecha_registro: string | null
}

interface OpcionesSolicitud {
  requiereSesion?: boolean
  metodo?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE"
  datos?: unknown
}

function obtenerMensajeError(
  resultado: unknown,
  estado: number,
): string {
  const detalle =
    typeof resultado === "object" &&
    resultado !== null &&
    "detail" in resultado
      ? (resultado as { detail: unknown }).detail
      : null

  if (typeof detalle === "string") {
    return detalle
  }

  if (Array.isArray(detalle)) {
    return detalle
      .map((error) =>
        typeof error === "object" &&
        error !== null &&
        "msg" in error
          ? String(error.msg)
          : "Hay un dato inválido.",
      )
      .join(". ")
  }

  switch (estado) {
    case 400:
      return "La solicitud contiene datos incorrectos."
    case 401:
      return "No estás autenticado o tus credenciales son incorrectas."
    case 403:
      return "No tienes permiso para realizar esta acción."
    case 404:
      return "No se encontró el recurso solicitado."
    case 409:
      return "La operación entra en conflicto con los datos existentes."
    case 422:
      return "Los datos enviados no son válidos."
    case 429:
      return "Has realizado demasiadas solicitudes. Inténtalo más tarde."
    default:
      return estado >= 500
        ? "Ocurrió un problema en el servidor. Inténtalo más tarde."
        : `No se pudo completar la solicitud (${estado}).`
  }
}

export async function solicitar<T>(
  endpoint: string,
  opciones: OpcionesSolicitud = {},
): Promise<T> {
  const {
    requiereSesion = false,
    metodo = "POST",
    datos,
  } = opciones

  const token = sessionStorage.getItem(CLAVE_TOKEN)

  if (requiereSesion && !token) {
    window.dispatchEvent(new Event("sesion-expirada"))
    throw new Error("Tu sesión ha terminado. Inicia sesión nuevamente.")
  }

  const headers: Record<string, string> = {
    Accept: "application/json",
  }

  if (datos !== undefined) {
    headers["Content-Type"] = "application/json"
  }

  if (requiereSesion && token) {
    headers.Authorization = `Bearer ${token}`
  }

  let respuesta: Response

  try {
    respuesta = await fetch(`${API_URL}${endpoint}`, {
      method: metodo,
      headers,
      ...(datos !== undefined
        ? { body: JSON.stringify(datos) }
        : {}),
    })
  } catch {
    throw new Error(
      "No se pudo conectar con el servidor. Comprueba que la API esté ejecutándose.",
    )
  }

  if (respuesta.status === 401 && requiereSesion) {
    window.dispatchEvent(new Event("sesion-expirada"))
    throw new Error(
      "Tu sesión ha expirado. Inicia sesión nuevamente.",
    )
  }

  const contenido = await respuesta.text()
  let resultado: unknown = null

  if (contenido) {
    try {
      resultado = JSON.parse(contenido)
    } catch {
      resultado = null
    }
  }

  if (!respuesta.ok) {
    throw new Error(obtenerMensajeError(resultado, respuesta.status))
  }

  if (!contenido) {
    return undefined as T
  }

  if (resultado === null) {
    throw new Error("El servidor devolvió una respuesta no válida.")
  }

  return resultado as T
}

export function iniciarSesion(datos: UsuarioLogin) {
  return solicitar<TokenRespuesta>("/auth/login", { datos })
}

export function registrarUsuario(datos: UsuarioRegistro) {
  return solicitar<UsuarioRespuesta>("/auth/registro", { datos })
}

export function solicitarRecuperacion(correo: string) {
  return solicitar<unknown>("/auth/recuperar-contrasena", {
    datos: { correo },
  })
}

export function restablecerContrasena(
  token: string,
  nueva_contrasena: string,
) {
  return solicitar<unknown>("/auth/restablecer-contrasena", {
    datos: { token, nueva_contrasena },
  })
}
