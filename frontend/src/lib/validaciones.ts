export const PATRON_CURP = "[A-Z][AEIOUX][A-Z]{2}[0-9]{6}[HM][A-Z]{5}[A-Z0-9][0-9]"
function fechaLocal(fecha: Date) {
  return [fecha.getFullYear(), String(fecha.getMonth() + 1).padStart(2, "0"), String(fecha.getDate()).padStart(2, "0")].join("-")
}
export function limitesNacimiento() {
  const hoy = new Date()
  const minimo = new Date(hoy.getFullYear() - 120, hoy.getMonth(), Math.min(hoy.getDate(), 28))
  return { min: fechaLocal(minimo), max: fechaLocal(hoy) }
}
