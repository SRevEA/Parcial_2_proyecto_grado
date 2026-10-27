'use client'

import {
  Building2,
  Camera,
  DoorOpen,
  FileSignature,
  IdCard,
  MoreVertical,
  Pencil,
  ScanFace,
  ShieldCheck,
  Trash2,
  UserCheck,
  UserX,
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { MUESTRAS } from '@/components/panel/capturador-rostro'
import { acento, iniciales } from '@/lib/colores'
import { cn } from '@/lib/utils'
import type { Residente } from '@/lib/tipos'

type Props = {
  residente: Residente
  alAutorizar: () => void
  alCapturar: () => void
  alEditar: () => void
  alCambiarEstado: () => void
  alSuprimir: () => void
}

export function TarjetaResidente({
  residente,
  alAutorizar,
  alCapturar,
  alEditar,
  alCambiarEstado,
  alSuprimir,
}: Props) {
  const color = acento(residente.id_residente)
  const activo = residente.estado === 'ACTIVO'
  const completo = residente.muestras >= MUESTRAS
  const avance = Math.min(residente.muestras / MUESTRAS, 1) * 100

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
          {iniciales(`${residente.nombre} ${residente.apellido}`)}
        </div>

        <div className="min-w-0 flex-1">
          <p className="truncate font-semibold leading-tight">
            {residente.nombre} {residente.apellido}
          </p>
          <p className="metric mt-0.5 flex items-center gap-1 text-xs text-muted-foreground">
            <IdCard className="size-3.5 shrink-0" />
            <span className="truncate">{residente.documento}</span>
          </p>
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon-sm" title="Mas acciones">
              <MoreVertical />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem onSelect={alEditar}>
              <Pencil />
              Editar datos
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={alCambiarEstado}>
              {activo ? <UserX /> : <UserCheck />}
              {activo ? 'Inactivar' : 'Activar'}
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem variant="destructive" onSelect={alSuprimir}>
              <Trash2 />
              Suprimir
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="flex flex-wrap gap-1.5">
        <Badge variant="outline">
          <Building2 />
          Torre {residente.torre}
        </Badge>
        <Badge variant="outline">
          <DoorOpen />
          Apto {residente.numero}
        </Badge>
        <Badge variant={activo ? 'success' : 'destructive'}>
          {activo ? <UserCheck /> : <UserX />}
          {activo ? 'Activo' : 'Inactivo'}
        </Badge>
        <Badge variant={residente.tiene_autorizacion ? 'success' : 'warning'}>
          {residente.tiene_autorizacion ? <ShieldCheck /> : <FileSignature />}
          {residente.tiene_autorizacion ? 'Autorizado' : 'Sin autorizacion'}
        </Badge>
      </div>

      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <ScanFace className="size-3.5" />
            Patron facial
          </span>
          <span className="metric">
            {residente.muestras}/{MUESTRAS}
          </span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-muted">
          <div
            className={cn('h-full rounded-full transition-[width] duration-500', color.barra)}
            style={{ width: `${avance}%` }}
          />
        </div>
      </div>

      <div className="mt-auto">
        {!residente.tiene_autorizacion ? (
          <Button variant="outline" className="w-full" onClick={alAutorizar}>
            <FileSignature />
            Registrar autorizacion
          </Button>
        ) : (
          <Button
            variant={completo ? 'outline' : 'default'}
            className="w-full"
            onClick={alCapturar}
          >
            <Camera />
            {residente.muestras === 0 ? 'Capturar rostro' : 'Capturar mas muestras'}
          </Button>
        )}
      </div>
    </article>
  )
}
