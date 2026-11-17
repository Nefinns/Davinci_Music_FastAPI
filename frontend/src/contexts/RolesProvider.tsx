import { useEffect, useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { useSesion } from '@/contexts/SesionContext'
import { RolesContext } from '@/hooks/useRoles'
import { consultar } from '@/services/operaciones'
export default function RolesProvider({ children }: { children: ReactNode }) {
  const { autenticado, estadoPerfil } = useSesion()
  const { pathname } = useLocation()
  const id = estadoPerfil?.estado === 'completo' ? estadoPerfil.id_usuario : null
  const [estado, setEstado] = useState({ roles: [] as string[], cargando: true, error: '', id: null as number | null })
  useEffect(() => {
    let vivo = true
    if (autenticado && id) void consultar<string[]>('/usuarios/me/roles')
      .then(roles => { if (vivo) setEstado({ roles, cargando: false, error: '', id }) })
      .catch(e => { if (vivo) setEstado({ roles: [], cargando: false, error: String(e), id }) })
    return () => { vivo = false }
  }, [autenticado, id, pathname])
  const valor = !autenticado || !id ? { roles: [], cargando: false, error: '' }
    : estado.id !== id ? { roles: [], cargando: true, error: '' } : estado
  return <RolesContext.Provider value={valor}>{children}</RolesContext.Provider>
}
