
import { Link } from "react-router-dom"
import {
  ArrowRight,
  Music2,
  Guitar,
  GraduationCap,
  Headphones,
  Music,
  BookOpen,
} from "lucide-react"

const opciones = [
  {
    nombre: "Instrumentos musicales",
    descripcion:
      "Encuentra instrumentos para comenzar o continuar tu camino musical.",
    Icono: Guitar,
  },
  {
    nombre: "Accesorios y equipo",
    descripcion:
      "Descubre accesorios y equipo para practicar y disfrutar de la música.",
    Icono: Headphones,
  },
  {
    nombre: "Material musical",
    descripcion:
      "Explora recursos que te acompañarán durante tu aprendizaje musical.",
    Icono: Music,
  },
]

export default function InicioPublico() {
  return (
    <main className="min-h-screen bg-ivory text-ebony">
      <header className="border-b border-ebony/10">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-5 lg:px-10">
          <Link to="/" className="flex shrink-0 items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-full bg-sidebar text-brass">
              <Music2 size={25} />
            </div>

            <div>
              <p className="font-heading text-2xl font-bold leading-none">
                DaVinciMusic
              </p>
              <p className="mt-1 text-[10px] uppercase tracking-[0.2em] text-secondary">
                Tienda y escuela musical
              </p>
            </div>
          </Link>

          <nav className="hidden items-center gap-6 lg:flex">
            <a href="#tienda" className="text-sm text-secondary hover:text-patina">
              Tienda
            </a>
            <a href="#escuela" className="text-sm text-secondary hover:text-patina">
              Escuela de música
            </a>
            <a href="#nosotros" className="text-sm text-secondary hover:text-patina">
              Nosotros
            </a>
          </nav>

          <div className="flex shrink-0 items-center gap-2">
            <Link
              to="/login"
              className="hidden rounded-full px-4 py-2 text-sm font-semibold transition hover:bg-black/5 sm:inline-flex"
            >
              Iniciar sesión
            </Link>
            <Link
              to="/registro"
              className="inline-flex items-center gap-2 rounded-full bg-patina px-4 py-3 text-sm font-semibold text-white transition hover:bg-sidebar"
            >
              Crear cuenta
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden bg-sidebar text-white">
        <div className="pointer-events-none absolute -right-20 -top-24 h-80 w-80 rounded-full border border-brass/20" />
        <div className="pointer-events-none absolute -right-4 -top-10 h-56 w-56 rounded-full border border-brass/20" />

        <div className="mx-auto grid max-w-7xl items-center gap-12 px-6 py-16 md:grid-cols-2 md:py-24 lg:px-10">
          <div className="relative z-10">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-brass/40 px-4 py-2 text-xs uppercase tracking-[0.15em] text-brass">
              <Music2 size={15} />
              Tu mundo musical comienza aquí
            </div>

            <h1 className="max-w-xl font-heading text-5xl font-semibold leading-tight md:text-6xl lg:text-7xl">
              La música se aprende, se vive y se comparte.
            </h1>

            <p className="mt-6 max-w-lg text-base leading-7 text-white/75 md:text-lg">
              Descubre instrumentos, desarrolla tu talento y encuentra un
              espacio para hacer de la música parte de tu vida.
            </p>

            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                to="/registro"
                className="inline-flex items-center gap-2 rounded-full bg-brass px-6 py-3.5 font-semibold text-ebony transition hover:bg-[#d8b45f]"
              >
                Comenzar ahora
                <ArrowRight size={18} />
              </Link>

              <a
                href="#nosotros"
                className="inline-flex items-center rounded-full border border-white/30 px-6 py-3.5 font-semibold transition hover:bg-white/10"
              >
                Conócenos
              </a>
            </div>

            <div className="mt-12 grid grid-cols-3 gap-4 border-t border-white/15 pt-6">
              <div>
                <p className="font-heading text-xl font-semibold text-brass md:text-2xl">
                  Tienda
                </p>
                <p className="mt-1 text-xs text-white/60">
                  Instrumentos y accesorios
                </p>
              </div>
              <div>
                <p className="font-heading text-xl font-semibold text-brass md:text-2xl">
                  Escuela
                </p>
                <p className="mt-1 text-xs text-white/60">
                  Formación musical
                </p>
              </div>
              <div>
                <p className="font-heading text-xl font-semibold text-brass md:text-2xl">
                  Comunidad
                </p>
                <p className="mt-1 text-xs text-white/60">
                  Aprende y comparte
                </p>
              </div>
            </div>
          </div>

          <div className="relative mx-auto flex aspect-square w-full max-w-md items-center justify-center">
            <div className="absolute inset-5 rounded-full border border-brass/25" />
            <div className="absolute inset-12 rounded-full border border-white/10" />

            <div className="relative flex h-64 w-64 items-center justify-center rounded-full bg-white/[0.06] md:h-80 md:w-80">
              <div className="absolute inset-4 rounded-full border border-brass/30" />
              <Guitar
                className="h-36 w-36 -rotate-12 text-brass md:h-48 md:w-48"
                strokeWidth={0.8}
              />
            </div>

            <div className="absolute right-0 top-12 rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur-sm">
              <Music2 className="mb-2 text-brass" size={23} />
              <p className="text-sm font-semibold">Inspira tu talento</p>
              <p className="mt-1 text-xs text-white/60">Una nota a la vez</p>
            </div>

            <div className="absolute bottom-10 left-0 rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur-sm">
              <GraduationCap className="mb-2 text-brass" size={23} />
              <p className="text-sm font-semibold">Aprende música</p>
              <p className="mt-1 text-xs text-white/60">A tu propio ritmo</p>
            </div>
          </div>
        </div>
      </section>

      <section id="tienda" className="mx-auto max-w-7xl px-6 py-20 lg:px-10">
        <div className="mb-10 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.25em] text-patina">
              Explora nuestras opciones
            </p>
            <h2 className="mt-3 font-heading text-4xl font-semibold md:text-5xl">
              Encuentra tu sonido
            </h2>
          </div>

          <p className="max-w-md leading-7 text-secondary">
            Un espacio para descubrir herramientas, recursos e inspiración
            para tu recorrido musical.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-3">
          {opciones.map(({ nombre, descripcion, Icono }) => (
            <article
              key={nombre}
              className="rounded-2xl border border-ebony/10 bg-white/70 p-7 transition hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-patina/10 text-patina">
                <Icono size={25} />
              </div>

              <h3 className="mt-6 font-heading text-2xl font-semibold">
                {nombre}
              </h3>

              <p className="mt-3 leading-7 text-secondary">{descripcion}</p>

              <Link
                to="/registro"
                className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-patina hover:text-sidebar"
              >
                Explorar
                <ArrowRight size={16} />
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section id="escuela" className="bg-[#e6ebe5]">
        <div className="mx-auto grid max-w-7xl gap-10 px-6 py-20 md:grid-cols-2 md:items-center lg:px-10">
          <div className="flex min-h-64 items-center justify-center rounded-3xl bg-sidebar p-10 text-brass">
            <div className="text-center">
              <GraduationCap className="mx-auto h-20 w-20" strokeWidth={1} />
              <p className="mt-5 font-heading text-3xl font-semibold text-white">
                Aprende. Practica. Evoluciona.
              </p>
            </div>
          </div>

          <div>
            <p className="text-xs font-bold uppercase tracking-[0.25em] text-patina">
              Escuela de música
            </p>

            <h2 className="mt-3 font-heading text-4xl font-semibold md:text-5xl">
              Tu pasión también puede convertirse en conocimiento.
            </h2>

            <p className="mt-5 leading-7 text-secondary">
              DaVinciMusic reúne la tienda de instrumentos y la formación
              musical en un mismo espacio. Explora las posibilidades y comienza
              a construir tu camino musical.
            </p>

            <Link
              to="/registro"
              className="mt-7 inline-flex items-center gap-2 rounded-full bg-patina px-6 py-3 font-semibold text-white transition hover:bg-sidebar"
            >
              Únete a la comunidad
              <ArrowRight size={17} />
            </Link>
          </div>
        </div>
      </section>

      <section id="nosotros" className="mx-auto max-w-7xl px-6 py-20 lg:px-10">
        <div className="mx-auto max-w-3xl text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-brass/20 text-patina">
            <BookOpen size={27} />
          </div>

          <h2 className="mt-5 font-heading text-4xl font-semibold md:text-5xl">
            Mucho más que una tienda musical
          </h2>

          <p className="mt-5 leading-8 text-secondary">
            Nuestro propósito es acercar la música a más personas, facilitando
            el acceso a instrumentos y creando oportunidades para aprender.
            Queremos que encuentres en DaVinciMusic un lugar para explorar tu
            creatividad y desarrollar tu talento.
          </p>

          <Link
            to="/registro"
            className="mt-8 inline-flex items-center gap-2 font-semibold text-patina hover:text-sidebar"
          >
            Forma parte de DaVinciMusic
            <ArrowRight size={17} />
          </Link>
        </div>
      </section>

      <footer className="bg-[#101d1c] text-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-8 md:flex-row md:items-center md:justify-between lg:px-10">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10 text-brass">
              <Music2 size={22} />
            </div>
            <div>
              <p className="font-heading text-xl font-semibold">DaVinciMusic</p>
              <p className="text-xs text-white/50">Tienda y escuela musical</p>
            </div>
          </div>

          <p className="text-sm text-white/50">
            © {new Date().getFullYear()} DaVinciMusic. Todos los derechos
            reservados.
          </p>

          <div className="flex gap-5 text-sm">
            <Link to="/login" className="text-white/70 transition hover:text-brass">
              Iniciar sesión
            </Link>
            <Link to="/registro" className="text-white/70 transition hover:text-brass">
              Crear cuenta
            </Link>
          </div>
        </div>
      </footer>
    </main>
  )
}
