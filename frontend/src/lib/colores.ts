export type Acento = {
  fondo: string
  texto: string
  borde: string
  barra: string
}

export const ACENTOS: Acento[] = [
  {
    fondo: 'bg-chart-1/12',
    texto: 'text-chart-1',
    borde: 'border-chart-1/25',
    barra: 'bg-chart-1',
  },
  {
    fondo: 'bg-chart-3/12',
    texto: 'text-chart-3',
    borde: 'border-chart-3/25',
    barra: 'bg-chart-3',
  },
  {
    fondo: 'bg-chart-4/12',
    texto: 'text-chart-4',
    borde: 'border-chart-4/25',
    barra: 'bg-chart-4',
  },
  {
    fondo: 'bg-chart-5/12',
    texto: 'text-chart-5',
    borde: 'border-chart-5/25',
    barra: 'bg-chart-5',
  },
  {
    fondo: 'bg-chart-2/12',
    texto: 'text-chart-2',
    borde: 'border-chart-2/25',
    barra: 'bg-chart-2',
  },
]

export function acento(semilla: number): Acento {
  return ACENTOS[Math.abs(semilla) % ACENTOS.length]
}

export function iniciales(texto: string): string {
  const partes = texto.trim().split(/\s+/).slice(0, 2)
  return partes.map((p) => p[0]?.toUpperCase() ?? '').join('') || '?'
}
