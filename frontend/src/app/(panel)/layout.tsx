'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useTheme } from 'next-themes'
import { LogOut, Moon, PanelLeftClose, PanelLeftOpen, ScanFace, Sun } from 'lucide-react'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { VisuallyHidden } from '@/components/ui/visually-hidden'
import { BarraMovil, Marca, Navegacion } from '@/components/panel/navegacion'
import { iniciales } from '@/lib/colores'
import { borrar, leer } from '@/lib/sesion'
import { cn } from '@/lib/utils'
import type { Sesion } from '@/lib/tipos'

const CLAVE_SIDEBAR = 'sidebar-expandido'

export default function PanelLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { resolvedTheme, setTheme } = useTheme()
  const [sesion, setSesion] = useState<Sesion | null>(null)
  const [expandido, setExpandido] = useState(true)

  useEffect(() => {
    const actual = leer()
    if (!actual) {
      router.replace('/login')
      return
    }
    setSesion(actual)
  }, [router])

  useEffect(() => {
    setExpandido(window.localStorage.getItem(CLAVE_SIDEBAR) !== 'no')
  }, [])

  function alternarSidebar() {
    setExpandido((previo) => {
      window.localStorage.setItem(CLAVE_SIDEBAR, previo ? 'no' : 'si')
      return !previo
    })
  }

  if (!sesion) {
    return null
  }

  const oscuro = resolvedTheme === 'dark'

  function salir() {
    borrar()
    router.replace('/login')
  }

  return (
    <div className="flex min-h-screen">
      <aside
        className={cn(
          'hidden shrink-0 flex-col border-r bg-sidebar transition-[width] duration-300 ease-out lg:flex',
          expandido ? 'w-60' : 'w-[4.5rem]'
        )}
      >
        <Marca compacta={!expandido} />
        <div className="py-3">
          <Navegacion rol={sesion.rol} compacta={!expandido} />
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b bg-background/85 px-3 backdrop-blur sm:px-4">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon-sm"
                className="hidden lg:inline-flex"
                onClick={alternarSidebar}
              >
                {expandido ? <PanelLeftClose /> : <PanelLeftOpen />}
                <VisuallyHidden>{expandido ? 'Ocultar el menu' : 'Mostrar el menu'}</VisuallyHidden>
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              {expandido ? 'Ocultar el menu' : 'Mostrar el menu'}
            </TooltipContent>
          </Tooltip>

          <div className="flex items-center gap-2.5 lg:hidden">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <ScanFace className="size-4" />
            </div>
            <p className="truncate text-sm font-semibold">Control de acceso</p>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon-sm" className="ml-auto rounded-full">
                <Avatar className="size-7">
                  <AvatarFallback className="bg-primary text-[11px] text-primary-foreground">
                    {iniciales(sesion.nombre)}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel className="font-normal">
                <p className="truncate text-sm font-medium">{sesion.nombre}</p>
                <p className="truncate text-xs text-muted-foreground">
                  {sesion.rol === 'ADMINISTRADOR' ? 'Administrador' : 'Vigilante'}
                </p>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onSelect={() => setTheme(oscuro ? 'light' : 'dark')}>
                {oscuro ? <Sun /> : <Moon />}
                {oscuro ? 'Modo claro' : 'Modo oscuro'}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onSelect={salir}>
                <LogOut />
                Cerrar sesion
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>

        <main className="min-w-0 flex-1 space-y-5 p-4 pb-24 lg:p-6 lg:pb-6">{children}</main>
      </div>

      <BarraMovil rol={sesion.rol} />
    </div>
  )
}
