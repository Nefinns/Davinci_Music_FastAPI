import ThirdParty from "supertokens-web-js/recipe/thirdparty"
import { solicitar } from "@/services/auth"

export type EstadoPerfil =
  | { estado: "completo"; id_usuario: number }
  | { estado: "pendiente"; correo: string }
  | { estado: "vincular_cuenta"; correo: string }

export interface RegistroGoogle {
  nombre_usuario: string
  nombre: string
  apellido_paterno: string
  apellido_materno: string | null
  fecha_nacimiento: string
  curp: string
  ine: string | null
  telefono: string | null
  direccion: string | null
}

export function consultarEstadoPerfil() {
  return solicitar<EstadoPerfil>("/auth/estado-perfil", {
    metodo: "GET",
    requiereSesion: true,
  })
}

export function completarRegistroGoogle(datos: RegistroGoogle) {
  return solicitar<unknown>("/auth/completar-registro-google", {
    datos,
    requiereSesion: true,
  })
}

export async function comenzarAccesoGoogle(vincularCuenta = false) {
  const url = await ThirdParty.getAuthorisationURLWithQueryParamsAndSetState({
    thirdPartyId: "google",
    frontendRedirectURI: `${window.location.origin}/auth/callback/google`,
    shouldTryLinkingWithSessionUser: vincularCuenta,
  })

  window.location.assign(url)
}

export async function finalizarAccesoGoogle() {
  const resultado = await ThirdParty.signInAndUp()

  if (resultado.status !== "OK") {
    throw new Error(
      resultado.status === "SIGN_IN_UP_NOT_ALLOWED"
        ? "No se pudo vincular esta cuenta de Google. Comprueba que no pertenezca a otro usuario."
        : "Google no proporcionó una cuenta válida para iniciar sesión.",
    )
  }
}