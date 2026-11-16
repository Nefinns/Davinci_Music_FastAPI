import { Link } from "react-router-dom"

export default function Contacto() {
  return <main className="min-h-screen bg-ivory p-8 text-ebony">
    <div className="mx-auto max-w-3xl">
      <Link to="/" className="text-patina">← DaVinciMusic</Link>
      <h1 className="mt-12 font-heading text-5xl">Contacto</h1>
      <p className="mt-5 text-lg">¿Tienes preguntas sobre instrumentos o clases? Ponte en contacto con el equipo de DaVinciMusic.</p>
      <p className="mt-4">Los datos de contacto se publicarán cuando la tienda comience operaciones.</p>
    </div>
  </main>
}
