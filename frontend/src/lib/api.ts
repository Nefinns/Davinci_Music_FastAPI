const BASE = (import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '')

export type Category = 'simples' | 'joins' | 'agregadas' | 'vistas'
export type Exercise = {
  id: string
  categoria: Category
  titulo: string
  descripcion: string
  coleccion: string
  tipo: 'find' | 'aggregate' | 'view'
  codigo: string
}
export type Catalog = { ejercicios: Exercise[]; categorias: { id: Category; titulo: string }[] }
export type DatabaseStatus = {
  base_datos: string
  colecciones: Record<string, number>
  vistas: string[]
  total_demo: number
  escritura_demo_habilitada: boolean
}
export type QueryResponse = {
  ejercicio: string
  filas: number
  duracion_ms: number
  resultados: Record<string, unknown>[]
  limite: number
}

async function request<T>(path: string, method: 'GET' | 'POST' = 'GET'): Promise<T> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 16000)
  try {
    const res = await fetch(`${BASE}${path}`, { method, signal: controller.signal, headers: { Accept: 'application/json' } })
    const data: unknown = await res.json()
    if (!res.ok) {
      const err = data as { detail?: string }
      throw new Error(err.detail ?? `Error HTTP ${res.status}`)
    }
    return data as T
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('La consulta tardó demasiado. Revisa la conexión con MongoDB Atlas.')
    }
    if (error instanceof TypeError) {
      throw new Error('No se puede conectar con FastAPI. Comprueba que esté iniciado en 127.0.0.1:8000.')
    }
    throw error
  } finally {
    window.clearTimeout(timeout)
  }
}

export const api = {
  health: () => request<{ ok: boolean; base_datos: string; escritura_demo_habilitada: boolean }>('/api/health'),
  catalog: () => request<Catalog>('/api/catalogo'),
  status: () => request<DatabaseStatus>('/api/estado'),
  execute: (id: string) => request<QueryResponse>(`/api/consultas/${encodeURIComponent(id)}`),
  seed: () => request<{ insertados: Record<string, number>; total_nuevos: number; mensaje: string }>('/api/datos-prueba', 'POST'),
  views: () => request<{ vistas: string[]; mensaje: string }>('/api/vistas/preparar', 'POST'),
}
