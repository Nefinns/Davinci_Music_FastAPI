import { createContext, useContext } from 'react'
export const RolesContext = createContext<{ roles: string[]; cargando: boolean; error: string }>({ roles: [], cargando: true, error: '' })
export const useRoles = () => useContext(RolesContext)
