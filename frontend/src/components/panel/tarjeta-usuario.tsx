'use client'

import { Eye, Mail, Pencil, ShieldCheck, UserCheck, UserX } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ACENTOS, iniciales } from '@/lib/colores'
import { cn } from '@/lib/utils'
import type { Usuario } from '@/lib/tipos'

type Props = {
  usuario: Usuario
  alEditar: () => void
  alCambiarEstado: () => void
}

export function TarjetaUsuario({ usuario, alEditar, alCambiarEstado }: Props) {
  const esAdmin = usuario.rol === 'ADMINISTRADOR'
  const activo = usuario.estado === 'ACTIVO'
  const color = esAdmin ? ACENTOS[2] : ACENTOS[1]

  return (
    <article
      data-animar
      className={cn(
        'flex flex-col gap-4 rounded-xl border bg-card p-4 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md',
        !activo && 'opacity-75'
      )}
    >
      <div className="flex items-start gap-3">
        <div
          className={cn(
            'flex size-11 shrink-0 items-center justify-center rounded-xl border text-sm font-semibold',
            color.fondo,
            color.texto,
            color.borde
          )}
        >
          {iniciales(usuario.nombre)}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate font-semibold leading-tight">{usuario.nombre}</p>
          <p className="metric mt-0.5 flex items-center gap-1 text-xs text-muted-foreground">
            <Mail className="size-3.5 shrink-0" />
            <span className="truncate">{usuario.correo}</span>
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5">
        <Badge variant="outline" className={cn(color.texto, color.borde, color.fondo)}>
          {esAdmin ? <ShieldCheck /> : <Eye />}
          {esAdmin ? 'Administrador' : 'Vigilante'}
        </Badge>
        <Badge variant={activo ? 'success' : 'destructive'}>
          {activo ? <UserCheck /> : <UserX />}
          {activo ? 'Activo' : 'Inactivo'}
        </Badge>
      </div>

      <p className="text-xs leading-relaxed text-muted-foreground">
        {esAdmin
          ? 'Gestiona residentes, usuarios y configuracion, y consulta evidencias.'
          : 'Monitorea en tiempo real y consulta el historial.'}
      </p>

      <div className="mt-auto flex gap-2">
        <Button variant="outline" size="sm" className="flex-1" onClick={alEditar}>
          <Pencil />
          Editar
        </Button>
        <Button variant="ghost" size="sm" className="flex-1" onClick={alCambiarEstado}>
          {activo ? <UserX /> : <UserCheck />}
          {activo ? 'Inactivar' : 'Activar'}
        </Button>
      </div>
    </article>
  )
}
