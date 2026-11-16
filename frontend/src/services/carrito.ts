export interface ArticuloCarrito { id_instrumento: number; nombre: string; precio: number; cantidad: number }
const clave = 'davinci-carrito-v1'
export function leerCarrito(): ArticuloCarrito[] {
  try {
    const r: unknown = JSON.parse(localStorage.getItem(clave) || '[]')
    if (!Array.isArray(r)) return []
    return r.filter((x): x is ArticuloCarrito => x && Number.isInteger(x.id_instrumento) && x.id_instrumento > 0 && typeof x.nombre === 'string' && typeof x.precio === 'number' && Number.isInteger(x.cantidad) && x.cantidad > 0 && x.cantidad <= 20).slice(0,30)
  } catch { return [] }
}
export function guardarCarrito(items: ArticuloCarrito[]) { localStorage.setItem(clave, JSON.stringify(items)) }
export function agregarCarrito(i: { id_instrumento: number; nombre_instrumento: string; precio_venta: number; stock_actual: number }) {
  const items = leerCarrito(), actual = items.find(x => x.id_instrumento === i.id_instrumento)
  if ((actual?.cantidad || 0) >= Math.min(20, i.stock_actual)) throw new Error('Alcanzaste las existencias disponibles para este artículo.')
  if (actual) actual.cantidad++
  else { if (items.length >= 30) throw new Error('Máximo 30 artículos diferentes.'); items.push({ id_instrumento: i.id_instrumento, nombre: i.nombre_instrumento, precio: Number(i.precio_venta), cantidad: 1 }) }
  guardarCarrito(items)
}
