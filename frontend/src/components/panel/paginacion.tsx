'use client'

import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

export const POR_PAGINA = 25

type Props = {
  pagina: number
  total: number
  porPagina?: number
  alCambiar: (pagina: number) => void
}

export function Paginacion({ pagina, total, porPagina = POR_PAGINA, alCambiar }: Props) {
  const paginas = Math.ceil(total / porPagina)
  if (paginas <= 1) return null

  const desde = pagina * porPagina + 1
  const hasta = Math.min(total, (pagina + 1) * porPagina)

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t pt-3">
      <p className="text-xs text-muted-foreground">
        <span className="metric">
          {desde}–{hasta}
        </span>{' '}
        de <span className="metric">{total}</span>
      </p>
      <div className="flex items-center gap-1">
        <Button
          variant="outline"
          size="icon-sm"
          title="Anterior"
          disabled={pagina === 0}
          onClick={() => alCambiar(pagina - 1)}
        >
          <ChevronLeft />
        </Button>
        <span className="metric px-2 text-xs text-muted-foreground">
          {pagina + 1} / {paginas}
        </span>
        <Button
          variant="outline"
          size="icon-sm"
          title="Siguiente"
          disabled={pagina + 1 >= paginas}
          onClick={() => alCambiar(pagina + 1)}
        >
          <ChevronRight />
        </Button>
      </div>
    </div>
  )
}
