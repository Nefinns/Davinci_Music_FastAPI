import { Braces, FileJson2, Rows3 } from 'lucide-react'
import type { QueryResponse } from '@/lib/api'

type Props = { data: QueryResponse | null; loading: boolean; attempted: boolean }

function asText(value: unknown): string {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'boolean') return value ? 'Sí' : 'No'
  if (typeof value === 'object') return JSON.stringify(value, null, 2)
  return String(value)
}

function CellValue({ value }: { value: unknown }) {
  if (value !== null && typeof value === 'object') {
    return (
      <details className="json-details">
        <summary className="inline-flex cursor-pointer items-center gap-1 text-patina"><Braces size={14} /> Ver documento</summary>
        <pre className="json-cell">{asText(value)}</pre>
      </details>
    )
  }
  return <span className="break-words">{asText(value)}</span>
}

export function Results({ data, loading, attempted }: Props) {
  const rows = data?.resultados ?? []
  const columns = Array.from(new Set(rows.flatMap((row) => Object.keys(row))))
  return (
    <section className="result-card" aria-label="Resultados de consulta">
      <div className="flex flex-wrap items-start justify-between gap-3 pb-5">
        <div className="flex items-start gap-3">
          <div className="icon-soft"><Rows3 size={18} /></div>
          <div>
            <h3 className="text-[17px] font-bold text-ink">Resultados</h3>
            <p className="text-sm text-muted">La tabla se actualiza después de cada consulta.</p>
          </div>
        </div>
        {data && <p className="text-xs font-semibold text-muted">{data.filas} filas · {data.duracion_ms} ms · máx. {data.limite}</p>}
      </div>
      {loading ? (
        <div className="empty-results"><div className="spinner" /><p>Consultando MongoDB Atlas…</p></div>
      ) : rows.length ? (
        <div className="table-wrap">
          <table className="result-table"><thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
            <tbody>{rows.map((row, idx) => <tr key={idx}>{columns.map((key) => <td key={key}><CellValue value={row[key]} /></td>)}</tr>)}</tbody>
          </table>
        </div>
      ) : (
        <div className="empty-results">
          <FileJson2 size={36} strokeWidth={1.5} />
          <strong>{attempted ? 'Sin documentos coincidentes' : 'Todo listo para consultar'}</strong>
          <p>{attempted ? 'La consulta funcionó, pero no encontró registros. Prepara los datos de prueba y vuelve a ejecutarla.' : 'Selecciona un ejercicio y haz clic en Ejecutar consulta.'}</p>
        </div>
      )}
    </section>
  )
}
