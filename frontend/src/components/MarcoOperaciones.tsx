import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useSesion } from '@/contexts/SesionContext'
import AvatarPerfil from '@/components/AvatarPerfil'
export default function MarcoOperaciones({ titulo, children }: { titulo: string; children: ReactNode }) {
  const { autenticado, estadoPerfil } = useSesion()
  return <main className="min-h-screen bg-ivory p-5 text-ebony md:p-10"><div className="mx-auto max-w-6xl">
    <header className="flex flex-wrap items-center justify-between gap-4 border-b border-ebony/10 pb-5">
      <Link to="/" className="font-heading text-2xl font-bold text-patina">DaVinciMusic</Link>
      <nav aria-label="Tienda y escuela" className="flex flex-wrap items-center gap-4 text-sm">
        <Link to="/catalogo">Tienda</Link><Link to="/escuela">Escuela</Link><Link to="/carrito">Carrito</Link>
        {autenticado ? <><Link to="/inicio">Mi cuenta</Link><Link to="/mis-inscripciones">Mis clases</Link><Link to="/mis-compras">Mis compras</Link>{estadoPerfil?.estado === 'completo' && <AvatarPerfil />}</> : <Link to="/login">Iniciar sesión</Link>}
      </nav>
    </header><h1 className="mb-8 mt-10 font-heading text-4xl">{titulo}</h1>{children}
  </div></main>
}
