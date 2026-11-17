import {Guitar,Music2} from 'lucide-react'
import type { ReactNode } from 'react'
export default function MarcoOperaciones({ titulo, children }: { titulo: string; children: ReactNode }) {
  return <main className="relative isolate min-h-screen overflow-hidden bg-ivory p-5 text-ebony md:p-10"><div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10 overflow-hidden text-patina/10"><Guitar className="absolute -right-12 top-16 h-72 w-72 rotate-12" strokeWidth={0.6}/><Music2 className="absolute -left-8 bottom-16 h-48 w-48 -rotate-12" strokeWidth={0.7}/></div><div className="mx-auto max-w-6xl"><h1 className="mb-8 font-heading text-4xl">{titulo}</h1>{children}</div></main>
}
