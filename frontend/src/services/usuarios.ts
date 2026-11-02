import { solicitar } from "@/services/auth"
export type Rol = "cliente" | "maestro" | "administrador"
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
