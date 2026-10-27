'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  ClipboardList,
  MonitorPlay,
  ScanFace,
  Settings,
  Users,
  UsersRound,
  type LucideIcon,
} from 'lucide-react'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { latir } from '@/lib/animacion'
import { cn } from '@/lib/utils'
import type { Rol } from '@/lib/tipos'

type Enlace = {
  href: string
  texto: string
  corto: string
  descripcion: string
  icono: LucideIcon
  soloAdmin: boolean
  color: string
  fondo: string
  barra: string
}

export const ENLACES: Enlace[] = [
  {
    href: '/monitor',
    texto: 'Monitor',
    corto: 'Monitor',
    descripcion: 'Reconocimiento en tiempo real',
    icono: MonitorPlay,
    soloAdmin: false,
    color: 'text-chart-3',
    fondo: 'bg-chart-3/12',
    barra: 'bg-chart-3',
  },
  {
    href: '/historial',
    texto: 'Historial',
    corto: 'Historial',
    descripcion: 'Intentos de acceso y evidencias',
    icono: ClipboardList,
    soloAdmin: false,
    color: 'text-chart-5',
    fondo: 'bg-chart-5/12',
    barra: 'bg-chart-5',
  },
  {
    href: '/residentes',
    texto: 'Residentes',
    corto: 'Residentes',
    descripcion: 'Registro y patrones faciales',
    icono: UsersRound,
    soloAdmin: true,
    color: 'text-chart-1',
    fondo: 'bg-chart-1/12',
    barra: 'bg-chart-1',
  },
  {
    href: '/usuarios',
    texto: 'Usuarios',
    corto: 'Usuarios',
    descripcion: 'Administradores y vigilantes',
    icono: Users,
    soloAdmin: true,
    color: 'text-chart-4',
    fondo: 'bg-chart-4/12',
    barra: 'bg-chart-4',
  },
  {
    href: '/configuracion',
    texto: 'Configuracion',
    corto: 'Ajustes',
    descripcion: 'Umbral y conservacion',
    icono: Settings,
    soloAdmin: true,
    color: 'text-chart-2',
    fondo: 'bg-chart-2/12',
    barra: 'bg-chart-2',
  },
]

export function enlacesVisibles(rol: Rol): Enlace[] {
  return ENLACES.filter((enlace) => !enlace.soloAdmin || rol === 'ADMINISTRADOR')
}

export function Marca({ compacta = false }: { compacta?: boolean }) {
  return (
    <div
      className={cn(
        'flex h-16 items-center gap-2.5 border-b',
        compacta ? 'justify-center px-2' : 'px-4'
      )}
    >
      <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
        <ScanFace className="size-5" />
      </div>
      {!compacta && (
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold leading-tight">Control de acceso</p>
          <p className="truncate text-xs text-muted-foreground">Reconocimiento facial</p>
        </div>
      )}
    </div>
  )
}

type PropsNavegacion = {
  rol: Rol
  compacta?: boolean
  alNavegar?: () => void
}

export function Navegacion({ rol, compacta = false, alNavegar }: PropsNavegacion) {
  const ruta = usePathname()

  return (
    <nav className={cn('flex flex-col gap-1', compacta ? 'px-2' : 'px-2')}>
      {enlacesVisibles(rol).map((enlace) => {
        const Icono = enlace.icono
        const activo = ruta === enlace.href
        const contenido = (
          <Link
            key={enlace.href}
            href={enlace.href}
            onClick={alNavegar}
            aria-current={activo ? 'page' : undefined}
            className={cn(
              'group relative flex items-center rounded-lg text-sm transition-colors',
              compacta ? 'justify-center p-2.5' : 'gap-3 px-3 py-2',
              activo
                ? cn(enlace.fondo, enlace.color, 'font-medium')
                : 'text-muted-foreground hover:bg-sidebar-accent/60 hover:text-foreground'
            )}
          >
            {activo && (
              <span
                className={cn(
                  'absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-r-full',
                  enlace.barra
                )}
              />
            )}
            <Icono className="size-[1.1rem] shrink-0" />
            {!compacta && <span className="truncate">{enlace.texto}</span>}
          </Link>
        )

        if (!compacta) return contenido

        return (
          <Tooltip key={enlace.href}>
            <TooltipTrigger asChild>{contenido}</TooltipTrigger>
            <TooltipContent side="right" sideOffset={8}>
              {enlace.texto}
            </TooltipContent>
          </Tooltip>
        )
      })}
    </nav>
  )
}

export function BarraMovil({ rol }: { rol: Rol }) {
  const ruta = usePathname()
  const activo = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    latir(activo.current)
  }, [ruta])

  return (
    <nav className="fixed inset-x-0 bottom-0 z-30 border-t bg-background/95 pb-[env(safe-area-inset-bottom)] backdrop-blur lg:hidden">
      <ul className="flex items-stretch">
        {enlacesVisibles(rol).map((enlace) => {
          const Icono = enlace.icono
          const esActivo = ruta === enlace.href
          return (
            <li key={enlace.href} className="min-w-0 flex-1">
              <Link
                href={enlace.href}
                aria-current={esActivo ? 'page' : undefined}
                className={cn(
                  'flex flex-col items-center gap-1 px-1 py-2 text-[0.6875rem] transition-colors',
                  esActivo ? enlace.color : 'text-muted-foreground'
                )}
              >
                <span
                  ref={esActivo ? activo : undefined}
                  className={cn(
                    'flex h-7 w-12 items-center justify-center rounded-full transition-colors',
                    esActivo && enlace.fondo
                  )}
                >
                  <Icono className="size-5" />
                </span>
                <span className={cn('max-w-full truncate', esActivo && 'font-medium')}>
                  {enlace.corto}
                </span>
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
