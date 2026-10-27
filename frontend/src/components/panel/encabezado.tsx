'use client'

import { usePathname } from 'next/navigation'
import { ScanFace } from 'lucide-react'
import { ENLACES } from '@/components/panel/navegacion'
import { cn } from '@/lib/utils'

export function Encabezado({ accion }: { accion?: React.ReactNode }) {
  const ruta = usePathname()
  const actual = ENLACES.find((enlace) => enlace.href === ruta)
  const Icono = actual?.icono ?? ScanFace

  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div className="flex min-w-0 items-center gap-3">
        <div
          className={cn(
            'flex size-11 shrink-0 items-center justify-center rounded-xl',
            actual ? cn(actual.fondo, actual.color) : 'bg-muted text-muted-foreground'
          )}
        >
          <Icono className="size-5" />
        </div>
        <div className="min-w-0">
          <h1 className="truncate text-xl font-semibold leading-tight">
            {actual?.texto ?? 'Panel'}
          </h1>
          {actual && <p className="truncate text-sm text-muted-foreground">{actual.descripcion}</p>}
        </div>
      </div>
      {accion}
    </div>
  )
}
