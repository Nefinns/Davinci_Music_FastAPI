import { solicitar } from '@/services/auth'
export function consultar<T>(ruta: string, privada = true) {
  return solicitar<T>(ruta, { metodo: 'GET', requiereSesion: privada })
}
export function operar<T = { mensaje: string }>(ruta: string, datos?: unknown, metodo: 'POST' | 'PUT' | 'DELETE' = 'POST') {
  return solicitar<T>(ruta, { metodo, requiereSesion: true, datos })
}
export interface Horario { dia_semana: string; hora_inicio: string; hora_fin: string; salon: string }
export interface Clase {
  id_usuario_maestro: number; id_clase: number; nombre_clase: string; maestro: string; nombre_instrumento: string;
  nivel: string; costo_mensual: number; cupo_maximo: number; disponibles: number; inscritos: number;
  activa: boolean; id_maestro: number; id_instrumento: number; id_periodo: number;
  nombre_periodo: string; fecha_inicio: string; fecha_fin: string; horarios: Horario[]
}
export interface Inscripcion { es_profesor?: boolean; id_inscripcion: number; id_usuario_maestro: number; id_clase: number; nombre_clase: string; alumno?: string; correo?: string; estado_inscripcion: string; costo_mensual_acordado: number; horarios?: Horario[] }
export const dinero = (n: number) => Number(n).toLocaleString('es-MX', { style: 'currency', currency: 'MXN' })
