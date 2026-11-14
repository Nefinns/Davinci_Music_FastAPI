export const MENSAJE_SESION =
  "No se pudo validar tu sesión después de renovarla. " +
  "Comprueba que la fecha y hora del equipo estén sincronizadas " +
  "y vuelve a iniciar sesión. Si continúa, revisa la configuración " +
  "de sesiones del servidor."

export function esLimiteRenovacion(error: unknown): boolean {
  // Mensaje del SDK supertokens-website utilizado por el proyecto.
  return (
    error instanceof Error &&
    error.message.includes(
      "The maximum session refresh limit has been reached",
    )
  )
}

export function mensajeFalloSolicitud(error: unknown): string {
  if (esLimiteRenovacion(error)) {
    return MENSAJE_SESION
  }

  if (error instanceof TypeError) {
    return (
      "No se pudo completar la conexión con la API. " +
      "Comprueba la conexión y la configuración del servidor."
    )
  }

  return "No se pudo completar la solicitud. Inténtalo nuevamente."
}