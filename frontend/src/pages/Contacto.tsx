import { Link } from "react-router-dom"

const direccion = "Doroteo Arango 119, colonia Francisco Villa, Tonalá, Jalisco, México"
const mapa = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(direccion)}`

export default function Contacto() {
  return <main className="min-h-screen bg-ivory px-6 py-10 text-ebony">
    <div className="mx-auto max-w-6xl">
      <Link to="/" className="text-patina hover:underline">← DaVinciMusic</Link>
      <h1 className="mt-10 font-heading text-5xl">Contacto y ubicación</h1>
      <p className="mt-4 max-w-3xl text-lg text-secondary">Visítanos para conocer la escuela de música y la tienda. Las clases son presenciales; confirma disponibilidad y horarios antes de acudir.</p>
      <div className="mt-10 grid gap-8 md:grid-cols-2">
        <section className="rounded-2xl bg-white p-7 shadow-sm">
          <h2 className="font-heading text-3xl">Estamos en Tonalá</h2>
          <address className="mt-4 not-italic leading-7">{direccion}</address>
          <a href={mapa} target="_blank" rel="noopener noreferrer" className="mt-4 inline-block font-semibold text-patina underline">Ver ubicación en Maps</a>
          <div className="mt-7 space-y-3">
            <p><strong>Atención en línea:</strong> siempre abierto. Consulta los horarios de visita y clases antes de acudir.</p>
            <p><strong>Oficina y contrataciones:</strong> <a className="text-patina underline" href="tel:+523311875269">33 1187 5269</a></p>
            <p><strong>Celular:</strong> <a className="text-patina underline" href="tel:+523313144767">33 1314 4767</a></p>
            <p><strong>Correo:</strong> <a className="break-all text-patina underline" href="mailto:orquestadavinci@hotmail.com">orquestadavinci@hotmail.com</a></p>
            <p>Se ofrece facturación; solicita los detalles directamente por los medios anteriores.</p>
            <p><a className="text-patina underline" href="https://www.youtube.com/channel/UCwcqY5K3-7vof1tWvKn0Qsg" target="_blank" rel="noopener noreferrer">Conoce nuestro canal de YouTube</a></p>
          </div>
        </section>
        <figure className="overflow-hidden rounded-2xl bg-white shadow-sm">
          <img src="/images/fachada-escuela.jpeg" alt="Fachada de la Escuela de Música Da Vinci en Doroteo Arango" className="h-96 w-full object-cover object-center" />
          <figcaption className="p-5 text-sm text-secondary">Reconoce la fachada de la Escuela de Música Da Vinci al llegar.</figcaption>
        </figure>
      </div>
    </div>
  </main>
}
