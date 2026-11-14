import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"

import Usuarios from "@/pages/Usuarios"
import InicioPublico from "@/pages/InicioPublico"
import InicioSesion from "@/pages/InicioSesion"
import Registro from "@/pages/Registro"
import RecuperarContrasena from "@/pages/RecuperarContrasena"
import Inicio from "@/pages/Inicio"
import RetornoGoogle from "@/pages/RetornoGoogle"
import CompletarPerfilGoogle from "@/pages/CompletarPerfilGoogle"

import { SesionProvider, useSesion } from "@/contexts/SesionContext"

function RutaProtegida() {
  const { autenticado, cargando, estadoPerfil } = useSesion()

  if (cargando) return <p role="status">Verificando sesión...</p>

  if (!autenticado) {
    return <Navigate to="/login" replace />
  }

  if (estadoPerfil?.estado !== "completo") {
    return <Navigate to="/" replace />
  }

  return <Inicio />
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
