import { solicitar } from "@/services/auth"
import EmailPassword from "supertokens-web-js/recipe/emailpassword"
export type Rol = "cliente" | "maestro" | "administrador"

export interface MetodosAcceso {
  google_vinculado: boolean
  contrasena_configurada: boolean
  correo: string
}

export function obtenerMetodosAcceso() {
  return solicitar<MetodosAcceso>(
    "/usuarios/me/metodos-acceso",
    { metodo: "GET", requiereSesion: true },
  )
}

export async function agregarContrasena(
  correo: string,
  contrasena: string,
) {
  const resultado = await EmailPassword.signUp({
    formFields: [
      { id: "email", value: correo },
      { id: "password", value: contrasena },
    ],
    shouldTryLinkingWithSessionUser: true,
  })

  if (resultado.status === "OK") return

  if (resultado.status === "FIELD_ERROR") {
    throw new Error(
      resultado.formFields.map(campo => campo.error).join(". "),
    )
  }

  throw new Error(
    resultado.reason || "No se pudo agregar la contraseña.",
  )
}
export interface UsuarioAdministracion {
  id_usuario: number; nombre_usuario: string; nombre: string; correo: string
  activo: boolean; vinculado: boolean; roles: string[]
}
export interface PaginaUsuarios {
  items: UsuarioAdministracion[]; total: number; offset: number; limit: number; id_actual: number
}
export async function puedeAdministrar() {
  const [roles, permisos] = await Promise.all([
    solicitar<string[]>("/usuarios/me/roles", { metodo: "GET", requiereSesion: true }),
    solicitar<string[]>("/usuarios/me/permisos", { metodo: "GET", requiereSesion: true }),
  ])
  return roles.includes("administrador") && permisos.includes("usuarios:roles:administrar")
}
export function consultarMetodosAcceso() {
  return solicitar<{ google_vinculado: boolean }>(
    "/usuarios/me/metodos-acceso",
    { metodo: "GET", requiereSesion: true },
  )
}
export function listarUsuarios(q: string, offset: number) {
  const params = new URLSearchParams({ q, offset: String(offset), limit: "10" })
  return solicitar<PaginaUsuarios>("/usuarios?" + params.toString(), { metodo: "GET", requiereSesion: true })
}
export function cambiarRol(id: number, rol: Rol, agregar: boolean) {
  return solicitar<{ mensaje: string }>(
    "/usuarios/" + id + "/roles/" + rol,
    { metodo: agregar ? "PUT" : "DELETE", requiereSesion: true },
  )
}
export function darBajaUsuario(id: number) {
  return solicitar<{ mensaje: string }>(`/usuarios/${id}/baja`, {
    metodo: "POST", requiereSesion: true, datos: { confirmar: true },
  })
}

export function reactivarUsuario(id: number) {
  return solicitar<{ mensaje: string }>(`/usuarios/${id}/reactivar`, {
    metodo: "POST",
    requiereSesion: true,
  })
}