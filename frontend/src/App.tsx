import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import type { ReactNode } from "react"

import Cabecera from '@/components/Cabecera'
import RolesProvider from '@/contexts/RolesProvider'
import { useRoles } from '@/hooks/useRoles'
import Administracion from '@/pages/Administracion'
import Docencia from '@/pages/Docencia'
import GestionVentas from '@/pages/GestionVentas'
import Abastecimiento from '@/pages/Abastecimiento'
import Usuarios from "@/pages/Usuarios"
import InicioPublico from "@/pages/InicioPublico"
import InicioSesion from "@/pages/InicioSesion"
import Registro from "@/pages/Registro"
import RecuperarContrasena from "@/pages/RecuperarContrasena"
import Inicio from "@/pages/Inicio"
import RetornoGoogle from "@/pages/RetornoGoogle"
import CompletarPerfilGoogle from "@/pages/CompletarPerfilGoogle"
import Catalogo from "@/pages/Catalogo"
import DetalleInstrumento from "@/pages/DetalleInstrumento"
import AdministrarCatalogo from "@/pages/AdministrarCatalogo"
import Perfil from "@/pages/Perfil"
import Escuela from '@/pages/Escuela'
import AdministrarEscuela from '@/pages/AdministrarEscuela'
import MisInscripciones from '@/pages/MisInscripciones'
import Carrito from '@/pages/Carrito'
import MisCompras from '@/pages/MisCompras'
import Contacto from "@/pages/Contacto"

import { SesionProvider, useSesion } from "@/contexts/SesionContext"

function RutaProtegida({ children }: { children?: ReactNode }) {
  const { autenticado, cargando, estadoPerfil } = useSesion()

  if (cargando) return <p role="status">Verificando sesión...</p>

  if (!autenticado) {
    return <Navigate to="/login" replace />
  }

  if (estadoPerfil?.estado !== "completo") {
    return <Navigate to="/" replace />
  }

  return children ?? <Inicio />
}

function AccesoRol({ rol, children }: { rol: string; children: ReactNode }) {
  const { roles, cargando, error } = useRoles()
  if (cargando) return <p role="status">Consultando permisos...</p>
  if (error) return <p role="alert">{error}</p>
  if (!roles.includes(rol)) return <p role="alert" className="p-8">No tienes acceso a esta sección.</p>
  return children
}

function RutaCompletarPerfil() {
  const { autenticado, cargando } = useSesion()

  if (cargando) return <p role="status">Verificando sesión...</p>

  if (!autenticado) {
    return <Navigate to="/login" replace />
  }

  return <CompletarPerfilGoogle />
}

function RutasAplicacion() {
  return (
    <>
    <Cabecera />
    <Routes>
      <Route path="/administracion" element={<RutaProtegida><AccesoRol rol="administrador"><Administracion /></AccesoRol></RutaProtegida>} />
      <Route path="/administracion/ventas" element={<RutaProtegida><AccesoRol rol="administrador"><GestionVentas /></AccesoRol></RutaProtegida>} />
      <Route path="/administracion/abastecimiento" element={<RutaProtegida><AccesoRol rol="administrador"><Abastecimiento /></AccesoRol></RutaProtegida>} />
      <Route path="/docencia" element={<RutaProtegida><AccesoRol rol="maestro"><Docencia /></AccesoRol></RutaProtegida>} />
      <Route path="/" element={<InicioPublico />} />
      <Route path="/escuela" element={<Escuela />} />
      <Route path="/carrito" element={<Carrito />} />
      <Route path="/mis-compras" element={<RutaProtegida><MisCompras /></RutaProtegida>} />
      <Route path="/mis-inscripciones" element={<RutaProtegida><MisInscripciones /></RutaProtegida>} />
      <Route path="/administracion/escuela" element={<RutaProtegida><AccesoRol rol="administrador"><AdministrarEscuela /></AccesoRol></RutaProtegida>} />
      <Route path="/contacto" element={<Contacto />} />
      <Route path="/catalogo" element={<Catalogo />} />
      <Route path="/catalogo/:id" element={<DetalleInstrumento />} />
      <Route path="/login" element={<InicioSesion />} />
      <Route path="/registro" element={<Registro />} />
      <Route
        path="/recuperar-contrasena"
        element={<RecuperarContrasena />}
      />
      <Route
        path="/restablecer-contrasena"
        element={<RecuperarContrasena restablecer />}
      />

      <Route
        path="/auth/callback/google"
        element={<RetornoGoogle />}
      />
      <Route
        path="/completar-perfil"
        element={<RutaCompletarPerfil />}
      />

      <Route
        path="/administracion/usuarios"
        element={<RutaProtegida><AccesoRol rol="administrador"><Usuarios /></AccesoRol></RutaProtegida>}
      />
      <Route path="/inicio" element={<RutaProtegida />} />
      <Route path="/perfil" element={<RutaProtegida><Perfil /></RutaProtegida>} />
      <Route path="/administracion/catalogo" element={<RutaProtegida><AccesoRol rol="administrador"><AdministrarCatalogo /></AccesoRol></RutaProtegida>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <SesionProvider>
        <RolesProvider><RutasAplicacion /></RolesProvider>
      </SesionProvider>
    </BrowserRouter>
  )
}
