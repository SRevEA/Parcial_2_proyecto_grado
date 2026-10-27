'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import {
  CircleCheck,
  CircleX,
  DoorOpen,
  Download,
  Eye,
  FileSearch,
  Loader2,
  ShieldAlert,
  UserX,
} from 'lucide-react'
import { toast } from 'sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ChipSelector, type ChipOption } from '@/components/ui/chip-selector'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { FloatingDatePicker } from '@/components/ui/floating-date-picker'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { BarraFiltros } from '@/components/panel/barra-filtros'
import { Contador } from '@/components/panel/contador'
import { Encabezado } from '@/components/panel/encabezado'
import { POR_PAGINA, Paginacion } from '@/components/panel/paginacion'
import { descargar, obtener } from '@/lib/api'
import { acento, iniciales } from '@/lib/colores'
import { cn } from '@/lib/utils'
import type { Evidencia, Pagina, Registro } from '@/lib/tipos'

const SEGUNDOS_RNF01 = 3

type Filtro = 'TODOS' | 'RECONOCIDO' | 'NO_RECONOCIDO'

const OPCIONES: ChipOption<Filtro>[] = [
  { key: 'TODOS', label: 'Todos', icon: 'done_all' },
  { key: 'RECONOCIDO', label: 'Reconocido', icon: 'check_circle' },
  { key: 'NO_RECONOCIDO', label: 'No reconocido', icon: 'cancel' },
]

function soloFecha(fecha: Date): string {
  const mes = String(fecha.getMonth() + 1).padStart(2, '0')
  const dia = String(fecha.getDate()).padStart(2, '0')
  return `${fecha.getFullYear()}-${mes}-${dia}`
}

export default function Historial() {
  const [registros, setRegistros] = useState<Registro[]>([])
  const [total, setTotal] = useState(0)
  const [desde, setDesde] = useState<Date | undefined>(undefined)
  const [hasta, setHasta] = useState<Date | undefined>(undefined)
  const [resultado, setResultado] = useState<Filtro>('TODOS')
  const [pagina, setPagina] = useState(0)
  const [cargando, setCargando] = useState(true)
  const [evidencia, setEvidencia] = useState<Evidencia | null>(null)
  const [abriendo, setAbriendo] = useState<number | null>(null)
  const descargando = useRef(false)

  const parametros = useCallback(() => {
    const p = new URLSearchParams()
    if (desde) p.set('desde', soloFecha(desde))
    if (hasta) p.set('hasta', soloFecha(hasta))
    if (resultado !== 'TODOS') p.set('resultado', resultado)
    const texto = p.toString()
    return texto ? `?${texto}` : ''
  }, [desde, hasta, resultado])

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      const filtros = parametros()
      const pedido = await obtener<Pagina<Registro>>(
        `/accesos${filtros}${filtros ? '&' : '?'}limite=${POR_PAGINA}` +
          `&desplazamiento=${pagina * POR_PAGINA}`
      )
      setRegistros(pedido.items)
      setTotal(pedido.total)
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo cargar el historial')
    } finally {
      setCargando(false)
    }
  }, [parametros, pagina])

  useEffect(() => {
    void cargar()
  }, [cargar])

  const exportar = useCallback(async () => {
    if (descargando.current) return
    descargando.current = true
    try {
      await descargar(`/accesos/exportar${parametros()}`, 'historial-accesos.csv')
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo exportar')
    } finally {
      descargando.current = false
    }
  }, [parametros])

  function cambiarFiltro<T>(aplicar: (valor: T) => void): (valor: T) => void {
    return (valor) => {
      aplicar(valor)
      setPagina(0)
    }
  }

  function limpiar() {
    setDesde(undefined)
    setHasta(undefined)
    setResultado('TODOS')
    setPagina(0)
  }

  async function verEvidencia(idRegistro: number) {
    setAbriendo(idRegistro)
    try {
      setEvidencia(await obtener<Evidencia>(`/accesos/${idRegistro}/evidencia`))
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo abrir la evidencia')
    } finally {
      setAbriendo(null)
    }
  }

  const filtrosActivos = [desde !== undefined, hasta !== undefined, resultado !== 'TODOS'].filter(
    Boolean
  ).length

  return (
    <div className="space-y-5">
      <Encabezado
        accion={
          <Button variant="outline" onClick={() => void exportar()}>
            <Download />
            Exportar CSV
          </Button>
        }
      />

      <BarraFiltros activos={filtrosActivos} alLimpiar={limpiar}>
        <FloatingDatePicker
          id="desde"
          label="Desde"
          value={desde}
          onChange={cambiarFiltro(setDesde)}
          className="w-full lg:w-44"
        />
        <FloatingDatePicker
          id="hasta"
          label="Hasta"
          value={hasta}
          onChange={cambiarFiltro(setHasta)}
          className="w-full lg:w-44"
        />
        <ChipSelector<Filtro>
          label="Resultado"
          icon="filter_list"
          options={OPCIONES}
          value={resultado}
          onChange={cambiarFiltro(setResultado)}
          className="w-full lg:w-48"
          floatingLabel
        />
      </BarraFiltros>

      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-muted-foreground">
          {cargando ? (
            'Cargando...'
          ) : (
            <>
              <Contador valor={total} />
              {total === 1 ? ' intento' : ' intentos'}
              {filtrosActivos > 0 && ' con los filtros aplicados'}
            </>
          )}
        </p>
        <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <ShieldAlert className="size-3.5 shrink-0" />
          Cada evidencia que abras queda en la bitacora de auditoria
        </p>
      </div>

      <Card>
        <CardContent className="space-y-3">
          {cargando ? (
            <div className="space-y-2">
              {[0, 1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : registros.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-12 text-center">
              <FileSearch className="size-9 text-muted-foreground opacity-40" />
              <p className="font-medium">No hay intentos con esos filtros</p>
              {filtrosActivos > 0 && (
                <Button variant="outline" size="sm" onClick={limpiar}>
                  Limpiar los filtros
                </Button>
              )}
            </div>
          ) : (
            <div className="-mx-2 overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead>Fecha</TableHead>
                    <TableHead>Resultado</TableHead>
                    <TableHead>Residente</TableHead>
                    <TableHead className="text-right">Similitud</TableHead>
                    <TableHead className="hidden text-right md:table-cell">
                      <Tooltip>
                        <TooltipTrigger className="cursor-help underline decoration-dotted underline-offset-4">
                          Respuesta
                        </TooltipTrigger>
                        <TooltipContent side="top" className="max-w-56">
                          Tiempo entre la captura en la porteria y el registro en el sistema. Se
                          marca en ambar si pasa de {SEGUNDOS_RNF01} s.
                        </TooltipContent>
                      </Tooltip>
                    </TableHead>
                    <TableHead className="hidden text-center lg:table-cell">Punto</TableHead>
                    <TableHead className="text-right">Evidencia</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {registros.map((registro) => {
                    const reconocido = registro.resultado === 'RECONOCIDO'
                    const fecha = new Date(registro.fecha_hora)
                    const tardo = registro.segundos_respuesta
                    const color = acento(registro.id_residente ?? 0)
                    return (
                      <TableRow key={registro.id_registro}>
                        <TableCell className="py-2.5">
                          <p className="metric text-sm leading-tight">
                            {fecha.toLocaleDateString('es-CO')}
                          </p>
                          <p className="metric text-xs leading-tight text-muted-foreground">
                            {fecha.toLocaleTimeString('es-CO')}
                          </p>
                        </TableCell>

                        <TableCell className="py-2.5">
                          <Badge variant={reconocido ? 'success' : 'destructive'}>
                            {reconocido ? <CircleCheck /> : <CircleX />}
                            {reconocido ? 'Reconocido' : 'No reconocido'}
                          </Badge>
                        </TableCell>

                        <TableCell className="py-2.5">
                          <div className="flex items-center gap-2.5">
                            {registro.nombre_residente ? (
                              <>
                                <span
                                  className={cn(
                                    'flex size-8 shrink-0 items-center justify-center rounded-lg border text-[0.6875rem] font-semibold',
                                    color.fondo,
                                    color.texto,
                                    color.borde
                                  )}
                                >
                                  {iniciales(registro.nombre_residente)}
                                </span>
                                <div className="min-w-0">
                                  <p className="truncate text-sm font-medium leading-tight">
                                    {registro.nombre_residente}
                                  </p>
                                  <p className="metric text-xs leading-tight text-muted-foreground">
                                    T{registro.torre} · {registro.numero}
                                  </p>
                                </div>
                              </>
                            ) : (
                              <>
                                <span className="flex size-8 shrink-0 items-center justify-center rounded-lg border bg-muted text-muted-foreground">
                                  <UserX className="size-4" />
                                </span>
                                <p className="text-sm text-muted-foreground">Sin identificar</p>
                              </>
                            )}
                          </div>
                        </TableCell>

                        <TableCell className="py-2.5 text-right">
                          <span
                            className={cn(
                              'metric text-sm',
                              reconocido ? 'text-status-ok' : 'text-muted-foreground'
                            )}
                          >
                            {registro.similitud === null ? '—' : registro.similitud.toFixed(4)}
                          </span>
                        </TableCell>

                        <TableCell className="hidden py-2.5 text-right md:table-cell">
                          <span
                            className={cn(
                              'metric text-sm',
                              tardo > SEGUNDOS_RNF01 ? 'text-status-warn' : 'text-muted-foreground'
                            )}
                          >
                            {tardo.toFixed(2)} s
                          </span>
                        </TableCell>

                        <TableCell className="hidden py-2.5 text-center lg:table-cell">
                          <Badge variant="outline">
                            <DoorOpen />
                            {registro.id_punto}
                          </Badge>
                        </TableCell>

                        <TableCell className="py-2.5 text-right">
                          {registro.tiene_evidencia ? (
                            <Button
                              variant="outline"
                              size="sm"
                              disabled={abriendo !== null}
                              onClick={() => void verEvidencia(registro.id_registro)}
                            >
                              {abriendo === registro.id_registro ? (
                                <Loader2 className="animate-spin" />
                              ) : (
                                <Eye />
                              )}
                              Ver
                            </Button>
                          ) : (
                            <span className="text-xs text-muted-foreground">sin foto</span>
                          )}
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </div>
          )}
          <Paginacion pagina={pagina} total={total} alCambiar={setPagina} />
        </CardContent>
      </Card>

      <Dialog open={evidencia !== null} onOpenChange={(abierto) => !abierto && setEvidencia(null)}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Evidencia del intento {evidencia?.id_registro}</DialogTitle>
            <DialogDescription>
              Expira el{' '}
              {evidencia && new Date(evidencia.fecha_expiracion).toLocaleDateString('es-CO')}. Esta
              consulta quedo registrada en la bitacora de auditoria.
            </DialogDescription>
          </DialogHeader>
          {evidencia && (
            <div className="space-y-3">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={evidencia.url}
                alt={`Evidencia del intento ${evidencia.id_registro}`}
                className="w-full rounded-md border"
              />
              <p className="metric break-all text-xs text-muted-foreground">
                SHA-256 {evidencia.hash_sha256}
              </p>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
