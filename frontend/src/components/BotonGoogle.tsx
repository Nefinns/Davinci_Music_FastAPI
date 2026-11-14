import { useRef, useState } from "react"
import { comenzarAccesoGoogle } from "@/services/google"

interface Props {
  vincular?: boolean
  disabled?: boolean
  className?: string
  onProcesando?: (valor: boolean) => void
}

export default function BotonGoogle({
  vincular = false,
  disabled = false,
  className = "",
  onProcesando,
}: Props) {
  const [procesando, setProcesando] = useState(false)
  const [error, setError] = useState("")
  const bloqueo = useRef(false)

  async function continuar() {
    if (bloqueo.current || disabled) return

    bloqueo.current = true
    setProcesando(true)
    setError("")
    onProcesando?.(true)

    try {
      await comenzarAccesoGoogle(vincular)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo abrir Google.",
      )
      bloqueo.current = false
      setProcesando(false)
      onProcesando?.(false)
    }
  }

  return (
    <div className={className}>
      <button
        type="button"
        disabled={disabled || procesando}
        aria-busy={procesando}
        onClick={() => void continuar()}
        className="inline-flex min-h-11 w-full items-center justify-center gap-3 rounded-full border border-[#747775] bg-white px-5 py-3 text-sm font-medium text-[#1f1f1f] shadow-sm transition hover:bg-[#f8fafd] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-patina disabled:cursor-not-allowed disabled:opacity-60"
      >
        <svg
          aria-hidden="true"
          viewBox="0 0 48 48"
          className="h-5 w-5 shrink-0"
        >
          <path
            fill="#EA4335"
            d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5Z"
          />
          <path
            fill="#4285F4"
            d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6C44.4 38.02 46.98 31.86 46.98 24.55Z"
          />
          <path
            fill="#FBBC05"
            d="M10.53 28.59A14.41 14.41 0 0 1 9.75 24c0-1.59.27-3.13.78-4.59l-7.98-6.19A23.86 23.86 0 0 0 0 24c0 3.87.93 7.53 2.56 10.78l7.97-6.19Z"
          />
          <path
            fill="#34A853"
            d="M24 48c6.48 0 11.93-2.13 15.91-5.8l-7.73-6c-2.15 1.45-4.92 2.3-8.18 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48Z"
          />
        </svg>

        {procesando
          ? "Abriendo Google..."
          : vincular
            ? "Vincular Google"
            : "Continuar con Google"}
      </button>

      {error && (
        <p role="alert" className="mt-3 text-sm text-red-700">
          {error}
        </p>
      )}
    </div>
  )
}