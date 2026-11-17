import type { ReactNode } from 'react'
export default function MarcoOperaciones({ titulo, children }: { titulo: string; children: ReactNode }) {
  return <main className="min-h-screen bg-ivory p-5 text-ebony md:p-10"><div className="mx-auto max-w-6xl"><h1 className="mb-8 font-heading text-4xl">{titulo}</h1>{children}</div></main>
}
