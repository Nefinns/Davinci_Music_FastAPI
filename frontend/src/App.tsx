import Usuarios from "@/pages/Usuarios"

import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import InicioPublico from "@/pages/InicioPublico"
import InicioSesion from "@/pages/InicioSesion"
import Registro from "@/pages/Registro"
import RecuperarContrasena from "@/pages/RecuperarContrasena"
import Inicio from "@/pages/Inicio"
import { SesionProvider, useSesion } from "@/contexts/SesionContext"

function RutaProtegida() {
  const { autenticado, cargando } = useSesion()

  if (cargando) return <p role="status">Verificando sesión...</p>

  if (!autenticado) {
    return <Navigate to="/login" replace />
  }

  return <Inicio />
}

function RutasAplicacion() {
  return (
    <Routes>
      <Route path="/" element={<InicioPublico />} />
      <Route path="/login" element={<InicioSesion />} />
      <Route path="/registro" element={<Registro />} />
      <Route path="/recuperar-contrasena" element={<RecuperarContrasena />} />
      <Route path="/restablecer-contrasena" element={<RecuperarContrasena restablecer />} />
      <Route path="/administracion/usuarios" element={<Usuarios />} />
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

