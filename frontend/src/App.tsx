
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import InicioPublico from "@/pages/InicioPublico"
import InicioSesion from "@/pages/InicioSesion"
import Registro from "@/pages/Registro"
import Inicio from "@/pages/Inicio"
import { SesionProvider, useSesion } from "@/contexts/SesionContext"

function RutaProtegida() {
  const { autenticado } = useSesion()

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

