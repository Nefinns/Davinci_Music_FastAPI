import { NavLink, Link, useLocation } from 'react-router-dom'
import { Music2, LogOut } from 'lucide-react'
import AvatarPerfil from '@/components/AvatarPerfil'
import { useSesion } from '@/contexts/SesionContext'
import { useRoles } from '@/hooks/useRoles'
const enlace = ({ isActive }: { isActive: boolean }) => 'rounded-lg px-3 py-2 text-sm hover:bg-patina/10 ' + (isActive ? 'bg-patina/10 font-semibold text-patina' : 'text-ebony')
export default function Cabecera() {
  const { autenticado, cargando, estadoPerfil, cerrarSesion } = useSesion()
  const { roles } = useRoles()
  const { pathname } = useLocation()
  const completo = autenticado && estadoPerfil?.estado === 'completo'
  return <header className="border-b border-ebony/10 bg-ivory text-ebony">
    <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-5 py-4">
      <Link to="/" className="flex items-center gap-2 font-heading text-2xl font-bold"><Music2 className="text-patina" aria-hidden="true"/>DaVinciMusic</Link>
      <div className="flex flex-wrap items-center gap-2">
        <nav aria-label="Navegación principal" className="flex flex-wrap items-center gap-1">
          <NavLink className={enlace} to="/catalogo">Tienda</NavLink><NavLink className={enlace} to="/escuela">Escuela</NavLink>
          <NavLink className={enlace} to="/contacto">Contacto</NavLink><NavLink className={enlace} to="/carrito">Carrito</NavLink>
          {completo && <>
            <NavLink className={enlace} to="/inicio">Mi cuenta</NavLink>
            <details key={pathname} className="relative"><summary className="cursor-pointer rounded-lg border border-patina/30 px-3 py-2 text-sm">Mi espacio</summary>
              <div className="absolute right-0 z-50 mt-2 grid w-56 gap-1 rounded-xl border border-ebony/10 bg-white p-3 shadow-xl">
                {roles.includes('cliente') && <NavLink className={enlace} to="/mis-inscripciones">Mi aprendizaje</NavLink>}
                <NavLink className={enlace} to="/mis-compras">Mis compras</NavLink>
                {roles.includes('maestro') && <NavLink className={enlace} to="/docencia">Área docente</NavLink>}
                {roles.includes('administrador') && <NavLink className={enlace} to="/administracion">Administración</NavLink>}
              </div>
            </details>
          </>}
        </nav>
        {!cargando && (autenticado ? <>
          {completo ? <AvatarPerfil/> : <Link to="/completar-perfil" className="px-3 text-patina">Completar perfil</Link>}
          <button type="button" onClick={() => void cerrarSesion()} aria-label="Cerrar sesión" className="flex items-center gap-2 rounded-full border border-ebony/20 px-3 py-2 text-sm"><LogOut size={16}/><span className="hidden md:inline">Cerrar sesión</span></button>
        </> : <Link to="/login" className="rounded-lg bg-patina px-4 py-2 text-sm font-semibold text-white">Iniciar sesión</Link>)}
      </div>
    </div>
  </header>
}
