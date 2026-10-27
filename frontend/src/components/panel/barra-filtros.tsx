'use client'

import { useEffect, useRef, useState } from 'react'
import { Eraser, SlidersHorizontal } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { FloatingInput } from '@/components/ui/floating-input'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { latir } from '@/lib/animacion'
import { usarEsMovil } from '@/lib/pantalla'
import { cn } from '@/lib/utils'

type Props = {
  busqueda?: string
  alBuscar?: (texto: string) => void
  marcador?: string
  activos: number
  alLimpiar: () => void
  children: React.ReactNode
}

export function BarraFiltros({
  busqueda,
  alBuscar,
  marcador,
  activos,
  alLimpiar,
  children,
}: Props) {
  const esMovil = usarEsMovil()
  const [abierto, setAbierto] = useState(false)
  const insignia = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    if (activos > 0) latir(insignia.current)
  }, [activos])

  const buscador =
    alBuscar === undefined ? null : (
      <div className="min-w-0 flex-1 lg:max-w-sm">
        <FloatingInput
          id="buscar"
          label="Buscar"
          icon="search"
          placeholder={marcador}
          value={busqueda ?? ''}
          onChange={alBuscar}
        />
      </div>
    )

  if (!esMovil) {
    return (
      <div className="flex flex-wrap items-end gap-3">
        {buscador}
        {children}
        {activos > 0 && (
          <Button variant="ghost" onClick={alLimpiar}>
            <Eraser />
            Limpiar
          </Button>
        )}
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2">
      {buscador}

      <Button
        variant="outline"
        size="lg"
        className={cn('relative shrink-0', buscador === null && 'w-full')}
        onClick={() => setAbierto(true)}
      >
        <SlidersHorizontal />
        Filtros
        {activos > 0 && (
          <span
            ref={insignia}
            className="absolute -right-1.5 -top-1.5 flex size-5 items-center justify-center rounded-full bg-primary text-[0.625rem] font-semibold text-primary-foreground"
          >
            {activos}
          </span>
        )}
      </Button>

      <Sheet open={abierto} onOpenChange={setAbierto}>
        <SheetContent side="bottom" className="rounded-t-2xl pb-2" showCloseButton={false}>
          <div className="mx-auto mt-3 h-1.5 w-10 rounded-full bg-border" />
          <SheetHeader className="pb-0">
            <SheetTitle>Filtros</SheetTitle>
            <SheetDescription>
              {activos === 0
                ? 'Sin filtros aplicados.'
                : `${activos} ${activos === 1 ? 'filtro aplicado' : 'filtros aplicados'}.`}
            </SheetDescription>
          </SheetHeader>

          <div className="flex flex-col gap-4 px-4">{children}</div>

          <SheetFooter className="flex-row gap-2 pb-[max(0.5rem,env(safe-area-inset-bottom))]">
            <Button
              variant="outline"
              className="flex-1"
              disabled={activos === 0}
              onClick={alLimpiar}
            >
              <Eraser />
              Limpiar
            </Button>
            <Button className="flex-1" onClick={() => setAbierto(false)}>
              Ver resultados
            </Button>
          </SheetFooter>
        </SheetContent>
      </Sheet>
    </div>
  )
}
