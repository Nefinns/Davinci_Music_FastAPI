import { useCallback, useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { UserRound } from "lucide-react"
import { solicitar } from "@/services/auth"

export default function AvatarPerfil({ texto = "Mi perfil" }: { texto?: string }) {
  const [imagen, setImagen] = useState<string | null>(null)
  const [falloImagen, setFalloImagen] = useState(false)

  const cargar = useCallback(async () => {
    try {
      const perfil = await solicitar<{ imagen_url: string | null }>(
        "/usuarios/me",
        { metodo: "GET", requiereSesion: true },
      )
      setImagen(perfil.imagen_url)
      setFalloImagen(false)
    } catch {
      setImagen(null)
    }
  }, [])

  useEffect(() => {
    void Promise.resolve().then(cargar)
    const actualizar = () => { void cargar() }
    window.addEventListener("davincimusic:perfil-actualizado", actualizar)
    return () => {
      window.removeEventListener("davincimusic:perfil-actualizado", actualizar)
    }
  }, [cargar])

  return (
    <Link
      to="/perfil"
      aria-label="Ir a mi perfil"
      className="inline-flex items-center gap-2 rounded-full px-2 py-1 font-semibold hover:bg-black/5"
    >
      <span className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-full bg-sidebar text-white">
        {imagen && !falloImagen ? (
          <img
            src={imagen}
            alt=""
            className="h-full w-full object-cover"
            onError={() => setFalloImagen(true)}
          />
        ) : (
          <UserRound size={23} aria-hidden="true" />
        )}
      </span>
      <span className="hidden sm:inline">{texto}</span>
    </Link>
  )
}