import ThirdParty from "supertokens-web-js/recipe/thirdparty"
import { solicitar } from "@/services/auth"
import { Session } from "@/lib/supertokens"

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
  if (vincularCuenta && !(await Session.doesSessionExist())) {
    throw new Error(
      "Inicia sesión con tu método habitual antes de vincular Google.",
    )
  }

  const url =
    await ThirdParty.getAuthorisationURLWithQueryParamsAndSetState({
      thirdPartyId: "google",
      frontendRedirectURI:
        `${window.location.origin}/auth/callback/google`,
      shouldTryLinkingWithSessionUser: vincularCuenta,
    })

  window.location.assign(url)
}

export async function finalizarAccesoGoogle() {
  const intento = ThirdParty.getStateAndOtherInfoFromStorage()
  const vinculando =
    intento?.shouldTryLinkingWithSessionUser === true

  const resultado = await ThirdParty.signInAndUp()

  if (resultado.status === "OK") return

  if (resultado.status === "SIGN_IN_UP_NOT_ALLOWED") {
    // Solo el diagnóstico del rechazo; no imprimir usuarios ni tokens.
    console.warn("Google: acceso rechazado por SuperTokens", {
      status: resultado.status,
      reason: resultado.reason,
    })

    throw new Error(
      vinculando
        ? "No se pudo vincular Google a esta cuenta. Vuelve a entrar con tu método habitual e inténtalo desde Mi cuenta. Si continúa, consulta el detalle del rechazo en la consola."
        : "No se pudo continuar con Google. Si ya tienes una cuenta, inicia sesión con tu método habitual y vincula Google desde Mi cuenta. Si continúa, consulta el detalle del rechazo en la consola.",
    )
  }

  throw new Error(
    "Google no proporcionó un correo para completar el acceso.",
  )
}