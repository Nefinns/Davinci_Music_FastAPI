import { API_URL, Session } from "@/lib/supertokens"
import { solicitar } from "@/services/auth"

export interface Categoria {
  id_categoria: number
  nombre_categoria: string
  descripcion: string | null
}

export interface Instrumento {
  id_instrumento: number
  id_categoria: number
  nombre_categoria: string
  nombre_instrumento: string
  marca: string | null
  modelo: string | null
  tamano: string | null
  color: string | null
  precio_venta: number
  stock_actual: number
  activo: boolean
  imagen_public_id: string | null
  imagen_url: string | null
}

export type DatosInstrumento = Pick<Instrumento,
  "id_categoria" | "nombre_instrumento" | "marca" | "modelo" | "tamano" | "color" |
  "precio_venta" | "stock_actual" | "activo">

export function categorias() {
  return solicitar<Categoria[]>("/catalogo/categorias", { metodo: "GET" })
}

export function instrumentos(parametros: URLSearchParams) {
  return solicitar<{ items: Instrumento[]; total: number; pagina: number; limite: number }>(
    "/catalogo/instrumentos?" + parametros.toString(), { metodo: "GET" },
  )
}

export function detalle(id: number) {
  return solicitar<Instrumento>(`/catalogo/instrumentos/${id}`, { metodo: "GET" })
}

export function todosInstrumentos(parametros = new URLSearchParams()) {
  const consulta = parametros.toString()
  return solicitar<Instrumento[]>("/catalogo/administracion/instrumentos" + (consulta ? `?${consulta}` : ""), {
    metodo: "GET", requiereSesion: true,
  })
}

export function guardarCategoria(datos: Omit<Categoria, "id_categoria">, id?: number) {
  return solicitar<Categoria>(id ? `/catalogo/categorias/${id}` : "/catalogo/categorias", {
    metodo: id ? "PUT" : "POST", requiereSesion: true, datos,
  })
}

export function borrarCategoria(id: number) {
  return solicitar<{ mensaje: string }>(`/catalogo/categorias/${id}`, {
    metodo: "DELETE", requiereSesion: true,
  })
}

export function guardarInstrumento(datos: DatosInstrumento, id?: number) {
  return solicitar<{ id_instrumento: number }>(
    id ? `/catalogo/instrumentos/${id}` : "/catalogo/instrumentos", {
      metodo: id ? "PUT" : "POST", requiereSesion: true, datos,
    },
  )
}

export function retirarInstrumento(id: number) {
  return solicitar<{ mensaje: string }>(`/catalogo/instrumentos/${id}`, {
    metodo: "DELETE", requiereSesion: true,
  })
}

export async function subirImagen(id: number, archivo: File) {
  if (!await Session.doesSessionExist()) throw new Error("Inicia sesión nuevamente.")
  const form = new FormData()
  form.append("archivo", archivo)
  const response = await fetch(`${API_URL}/catalogo/instrumentos/${id}/imagen`, {
    method: "POST",
    headers: { rid: "session" },
    credentials: "include",
    body: form,
  })
  if (!response.ok) {
    const error: { detail?: string } = await response.json().catch(() => ({}))
    throw new Error(error.detail || "No se pudo subir la imagen.")
  }
}
