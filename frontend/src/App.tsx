import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import type { ReactNode } from "react"

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
    <Routes>
      <Route path="/" element={<InicioPublico />} />
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
        element={<Usuarios />}
      />
      <Route path="/inicio" element={<RutaProtegida />} />
      <Route path="/perfil" element={<RutaProtegida><Perfil /></RutaProtegida>} />
      <Route path="/administracion/catalogo" element={<AdministrarCatalogo />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <SesionProvider>
        <RutasAplicacion />
      </SesionProvider>
    </BrowserRouter>
  )
}
