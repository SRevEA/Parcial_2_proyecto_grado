'use client'

import { useCallback, useEffect, useState } from 'react'
import { CircleCheck, CircleX, Radio, RadioTower, UserRound } from 'lucide-react'
import { toast } from 'sonner'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { Encabezado } from '@/components/panel/encabezado'
import { escucharMonitor, obtener } from '@/lib/api'
import { cn } from '@/lib/utils'
import type { Intento, Pagina, Registro } from '@/lib/tipos'

const MAXIMO_RECIENTES = 30
const RECIENTES_INICIALES = 20

type Fila = {
  id_registro: number
  fecha_hora: string
  reconocido: boolean
  quien: string | null
  ubicacion: string | null
  similitud: number | null
}

function hora(iso: string): string {
  return new Date(iso).toLocaleTimeString('es-CO')
}

function deRegistro(registro: Registro): Fila {
  return {
    id_registro: registro.id_registro,
    fecha_hora: registro.fecha_hora,
    reconocido: registro.resultado === 'RECONOCIDO',
    quien: registro.nombre_residente,
    ubicacion: registro.torre ? `T${registro.torre} · ${registro.numero}` : null,
    similitud: registro.similitud,
  }
}

function deIntento(intento: Intento): Fila {
  return {
    id_registro: intento.id_registro,
    fecha_hora: intento.fecha_hora,
    reconocido: intento.resultado === 'RECONOCIDO',
    quien: intento.residente ? `${intento.residente.nombre} ${intento.residente.apellido}` : null,
    ubicacion: intento.residente
      ? `T${intento.residente.torre} · ${intento.residente.numero}`
      : null,
    similitud: intento.similitud,
  }
}

function Dato({ etiqueta, valor }: { etiqueta: string; valor: string }) {
  return (
    <div className="min-w-0">
      <p className="text-[0.6875rem] uppercase tracking-wide text-muted-foreground">{etiqueta}</p>
      <p className="metric truncate text-sm">{valor}</p>
    </div>
  )
}

export default function Monitor() {
  const [ultimo, setUltimo] = useState<Intento | null>(null)
  const [recientes, setRecientes] = useState<Fila[]>([])
  const [cargandoHistorico, setCargandoHistorico] = useState(true)
  const [error, setError] = useState('')
  const [conectado, setConectado] = useState(false)

  const cargarHistorico = useCallback(async () => {
    try {
      const pagina = await obtener<Pagina<Registro>>(`/accesos?limite=${RECIENTES_INICIALES}`)
      setRecientes(pagina.items.map(deRegistro))
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo cargar el historico')
    } finally {
      setCargandoHistorico(false)
    }
  }, [])

  useEffect(() => {
    void cargarHistorico()
  }, [cargarHistorico])

  useEffect(() => {
    setConectado(true)
    const detener = escucharMonitor(
      (dato) => {
        const intento = dato as Intento
        setUltimo(intento)
        setRecientes((previos) =>
          [
            deIntento(intento),
            ...previos.filter((f) => f.id_registro !== intento.id_registro),
          ].slice(0, MAXIMO_RECIENTES)
        )
      },
      (mensaje) => {
        setError(mensaje)
        setConectado(false)
      }
    )
    return () => {
      detener()
      setConectado(false)
    }
  }, [])

  const reconocido = ultimo?.resultado === 'RECONOCIDO'

  return (
    <div className="space-y-5">
      <Encabezado />

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.9fr)_minmax(0,1fr)]">
        <div className="space-y-4">
          <div className="overflow-hidden rounded-xl border bg-card shadow-sm">
            <div
              className={cn(
                'relative aspect-[4/3] w-full',
                !ultimo && 'bg-muted',
                ultimo && (reconocido ? 'bg-status-ok/10' : 'bg-status-trip/10')
              )}
            >
              {ultimo?.imagen ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={ultimo.imagen}
                  alt={`Captura del intento ${ultimo.id_registro}`}
                  className="size-full object-cover"
                />
              ) : (
                <div className="flex size-full flex-col items-center justify-center gap-3 text-muted-foreground">
                  {ultimo ? (
                    <UserRound className="size-16 opacity-30" />
                  ) : (
                    <RadioTower className="size-16 opacity-30" />
                  )}
                  <p className="max-w-xs text-center text-sm">
                    {ultimo
                      ? 'El intento llego sin imagen.'
                      : conectado
                        ? 'Esperando intentos del punto de acceso...'
                        : 'Monitor desconectado.'}
                  </p>
                </div>
              )}

              {ultimo && (
                <div
                  className={cn(
                    'absolute inset-x-0 bottom-0 flex items-center gap-3 px-4 py-3 text-white',
                    reconocido ? 'bg-status-ok/90' : 'bg-status-trip/90'
                  )}
                >
                  {reconocido ? (
                    <CircleCheck className="size-7 shrink-0" />
                  ) : (
                    <CircleX className="size-7 shrink-0" />
                  )}
                  <div className="min-w-0">
                    <p className="truncate text-2xl font-bold leading-tight tracking-tight">
                      {reconocido && ultimo.residente
                        ? `${ultimo.residente.nombre} ${ultimo.residente.apellido}`
                        : 'No se reconoce'}
                    </p>
                    <p className="metric text-xs opacity-90">
                      {hora(ultimo.fecha_hora)} · punto {ultimo.id_punto}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          <Card>
            <CardContent className="flex flex-wrap items-center gap-x-6 gap-y-4">
              <div
                className={cn(
                  'flex size-14 shrink-0 items-center justify-center rounded-full',
                  !ultimo && 'bg-muted text-muted-foreground',
                  ultimo && reconocido && 'bg-status-ok/15 text-status-ok',
                  ultimo && !reconocido && 'bg-status-trip/15 text-status-trip'
                )}
              >
                <UserRound className="size-7" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-lg font-semibold leading-tight">
                  {!ultimo
                    ? 'Sin intentos en esta sesion'
                    : reconocido && ultimo.residente
                      ? `${ultimo.residente.nombre} ${ultimo.residente.apellido}`
                      : 'Persona no reconocida'}
                </p>
                <p className="text-sm text-muted-foreground">
                  {ultimo?.residente
                    ? `Torre ${ultimo.residente.torre} · Apto ${ultimo.residente.numero}`
                    : 'Sin apartamento asociado'}
                </p>
              </div>
              {ultimo && (
                <Badge variant={reconocido ? 'success' : 'destructive'}>
                  {reconocido ? 'Reconocido' : 'No reconocido'}
                </Badge>
              )}

              {ultimo && (
                <>
                  <Separator className="basis-full" />
                  <div className="grid w-full grid-cols-2 gap-4 sm:grid-cols-4">
                    <Dato etiqueta="Similitud" valor={ultimo.similitud.toFixed(4)} />
                    <Dato etiqueta="Umbral" valor={ultimo.umbral.toFixed(4)} />
                    <Dato
                      etiqueta="Respuesta"
                      valor={`${ultimo.segundos_respuesta.toFixed(2)} s`}
                    />
                    <Dato etiqueta="Registro" valor={`#${ultimo.id_registro}`} />
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {error && (
            <Card className="border-destructive/40 bg-destructive/5">
              <CardContent className="text-sm text-destructive">{error}</CardContent>
            </Card>
          )}
        </div>

        <Card className="lg:sticky lg:top-20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Radio
                className={cn('size-4', conectado ? 'text-status-ok' : 'text-muted-foreground')}
              />
              Historico
            </CardTitle>
            <CardDescription>
              Los ultimos intentos del punto de acceso. Los nuevos entran arriba.
            </CardDescription>
          </CardHeader>
          {cargandoHistorico ? (
            <CardContent className="space-y-2">
              {[0, 1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </CardContent>
          ) : recientes.length === 0 ? (
            <CardContent className="text-center text-sm text-muted-foreground">
              Todavia no hay intentos.
            </CardContent>
          ) : (
            <ScrollArea className="h-[26rem] lg:h-[calc(100vh-17rem)]">
              <ul className="divide-y">
                {recientes.map((fila) => (
                  <li key={fila.id_registro} className="flex items-center gap-3 px-6 py-2.5">
                    <span
                      className={cn(
                        'size-2 shrink-0 rounded-full',
                        fila.reconocido ? 'bg-status-ok' : 'bg-status-trip'
                      )}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">
                        {fila.quien ?? 'No reconocido'}
                      </p>
                      <p className="metric text-xs text-muted-foreground">
                        {hora(fila.fecha_hora)}
                        {fila.ubicacion ? ` · ${fila.ubicacion}` : ''}
                      </p>
                    </div>
                    <span className="metric shrink-0 text-xs text-muted-foreground">
                      {fila.similitud === null ? '—' : fila.similitud.toFixed(3)}
                    </span>
                  </li>
                ))}
              </ul>
            </ScrollArea>
          )}
        </Card>
      </div>
    </div>
  )
}
