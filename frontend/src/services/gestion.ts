export interface DetalleVenta { id_instrumento: number; nombre_instrumento: string; cantidad: number; precio_unitario: number }
export interface Venta {
  id_venta: number; estado_venta: string; estado_entrega: string; fecha_venta: string; total_centavos: number;
  cliente?: string; correo?: string; estado_reembolso?: string; motivo?: string; resolucion?: string; stripe_refund_id?: string;
  reembolso?: { estado: string; motivo: string; resolucion?: string; stripe_refund_id?: string };
  detalles: DetalleVenta[]; historial?: { accion: string; fecha: string; administrador: string }[]
}
export interface Proveedor { id_proveedor: number; nombre_proveedor: string; rfc: string; correo: string | null; telefono: string | null; direccion: string | null; activo: boolean }
export interface Producto { id_instrumento: number; nombre_instrumento: string; stock_actual: number; activo: boolean }
export interface LineaOrden { id_instrumento: number; cantidad_solicitada: number; costo_unitario: number }
export interface Orden { id_orden: number; nombre_proveedor: string; administrador: string; fecha_orden: string; estado_orden: string; total: number; detalles: (LineaOrden & { nombre_instrumento: string; cantidad_recibida: number })[] }
