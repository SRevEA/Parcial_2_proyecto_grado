'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import {
  Building2,
  ChevronRight,
  DoorOpen,
  MoreVertical,
  Pencil,
  Plus,
  Trash2,
  Users,
} from 'lucide-react'
import { toast } from 'sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { FloatingInput } from '@/components/ui/floating-input'
import { Skeleton } from '@/components/ui/skeleton'
import { eliminar, enviar, obtener } from '@/lib/api'
import { aparecer } from '@/lib/animacion'
import { acento } from '@/lib/colores'
import { cn } from '@/lib/utils'
import type { Apartamento, Pagina, Torre } from '@/lib/tipos'

type Borrado = { tipo: 'torre'; torre: Torre } | { tipo: 'apartamento'; apartamento: Apartamento }

export function Catalogo() {
  const [torres, setTorres] = useState<Torre[]>([])
  const [apartamentos, setApartamentos] = useState<Apartamento[]>([])
  const [seleccionada, setSeleccionada] = useState<number | null>(null)
  const [cargando, setCargando] = useState(true)
  const [cargandoAptos, setCargandoAptos] = useState(false)

  const [formTorre, setFormTorre] = useState<{ editando: Torre | null; nombre: string } | null>(
    null
  )
  const [formApto, setFormApto] = useState<{
    editando: Apartamento | null
    numero: string
  } | null>(null)
  const [borrando, setBorrando] = useState<Borrado | null>(null)

  const listaTorres = useRef<HTMLUListElement>(null)
  const rejillaAptos = useRef<HTMLDivElement>(null)

  const cargarTorres = useCallback(async (): Promise<Torre[]> => {
    const pedido = await obtener<Pagina<Torre>>('/catalogo/torres')
    setTorres(pedido.items)
    return pedido.items
  }, [])

  const cargarApartamentos = useCallback(async (idTorre: number) => {
    setCargandoAptos(true)
    try {
      const pedido = await obtener<Pagina<Apartamento>>(
        `/catalogo/apartamentos?id_torre=${idTorre}`
      )
      setApartamentos(pedido.items)
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudieron cargar los apartamentos')
    } finally {
      setCargandoAptos(false)
    }
  }, [])

  useEffect(() => {
    async function inicial() {
      setCargando(true)
      try {
        const items = await cargarTorres()
        if (items.length > 0) setSeleccionada(items[0].id_torre)
      } catch (fallo) {
        toast.error(fallo instanceof Error ? fallo.message : 'No se pudieron cargar las torres')
      } finally {
        setCargando(false)
      }
    }
    void inicial()
  }, [cargarTorres])

  useEffect(() => {
    if (seleccionada === null) {
      setApartamentos([])
      return
    }
    void cargarApartamentos(seleccionada)
  }, [seleccionada, cargarApartamentos])

  useEffect(() => {
    if (!cargando) aparecer(listaTorres.current)
  }, [cargando, torres])

  useEffect(() => {
    if (!cargandoAptos) aparecer(rejillaAptos.current)
  }, [cargandoAptos, apartamentos])

  async function refrescar(idTorre: number | null) {
    await cargarTorres()
    if (idTorre !== null) await cargarApartamentos(idTorre)
  }

  async function guardarTorre(evento: React.FormEvent) {
    evento.preventDefault()
    if (!formTorre) return
    try {
      if (formTorre.editando === null) {
        const creada = await enviar<Torre>('/catalogo/torres', { nombre: formTorre.nombre })
        toast.success(`Torre ${creada.nombre} creada.`)
        setFormTorre(null)
        await cargarTorres()
        setSeleccionada(creada.id_torre)
        return
      }
      await enviar(
        `/catalogo/torres/${formTorre.editando.id_torre}`,
        { nombre: formTorre.nombre },
        'PUT'
      )
      toast.success('Torre renombrada.')
      setFormTorre(null)
      await refrescar(seleccionada)
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo guardar la torre')
    }
  }

  async function guardarApartamento(evento: React.FormEvent) {
    evento.preventDefault()
    if (!formApto || seleccionada === null) return
    try {
      if (formApto.editando === null) {
        await enviar(`/catalogo/torres/${seleccionada}/apartamentos`, { numero: formApto.numero })
        toast.success(`Apartamento ${formApto.numero} agregado.`)
      } else {
        await enviar(
          `/catalogo/apartamentos/${formApto.editando.id_apartamento}`,
          { numero: formApto.numero },
          'PUT'
        )
        toast.success('Apartamento actualizado.')
      }
      setFormApto(null)
      await refrescar(seleccionada)
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo guardar el apartamento')
    }
  }

  async function borrar() {
    if (!borrando) return
    try {
      if (borrando.tipo === 'torre') {
        await eliminar(`/catalogo/torres/${borrando.torre.id_torre}`)
        toast.success(`Torre ${borrando.torre.nombre} eliminada.`)
        setBorrando(null)
        const items = await cargarTorres()
        if (borrando.torre.id_torre === seleccionada) {
          setSeleccionada(items.length > 0 ? items[0].id_torre : null)
        }
        return
      }
      await eliminar(`/catalogo/apartamentos/${borrando.apartamento.id_apartamento}`)
      toast.success('Apartamento eliminado.')
      setBorrando(null)
      await refrescar(seleccionada)
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo eliminar')
    }
  }

  const torre = torres.find((t) => t.id_torre === seleccionada) ?? null

  return (
    <>
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Building2 className="size-4 text-chart-3" />
              Torres
            </CardTitle>
            <CardDescription>Cada apartamento pertenece a una torre.</CardDescription>
            <div className="col-start-2 row-span-2 row-start-1 self-start justify-self-end">
              <Button size="sm" onClick={() => setFormTorre({ editando: null, nombre: '' })}>
                <Plus />
                Torre
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {cargando ? (
              <div className="space-y-2">
                {[0, 1, 2].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : torres.length === 0 ? (
              <div className="flex flex-col items-center gap-3 py-10 text-center">
                <Building2 className="size-9 text-muted-foreground opacity-40" />
                <div>
                  <p className="font-medium">Todavia no hay torres</p>
                  <p className="text-sm text-muted-foreground">
                    Crea la primera para poder agregarle apartamentos.
                  </p>
                </div>
                <Button onClick={() => setFormTorre({ editando: null, nombre: '' })}>
                  <Plus />
                  Crear torre
                </Button>
              </div>
            ) : (
              <ul ref={listaTorres} className="space-y-1.5">
                {torres.map((fila) => {
                  const color = acento(fila.id_torre)
                  const activa = fila.id_torre === seleccionada
                  return (
                    <li key={fila.id_torre} data-animar>
                      <div
                        className={cn(
                          'flex items-center gap-2 rounded-lg border p-2 transition-colors',
                          activa ? cn(color.fondo, color.borde) : 'border-transparent'
                        )}
                      >
                        <button
                          type="button"
                          onClick={() => setSeleccionada(fila.id_torre)}
                          className="flex min-w-0 flex-1 items-center gap-3 text-left"
                        >
                          <span
                            className={cn(
                              'flex size-9 shrink-0 items-center justify-center rounded-lg border text-sm font-semibold',
                              color.fondo,
                              color.texto,
                              color.borde
                            )}
                          >
                            <Building2 className="size-4" />
                          </span>
                          <span className="min-w-0 flex-1">
                            <span className="block truncate font-medium leading-tight">
                              {fila.nombre}
                            </span>
                            <span className="block text-xs text-muted-foreground">
                              {fila.apartamentos}{' '}
                              {fila.apartamentos === 1 ? 'apartamento' : 'apartamentos'}
                            </span>
                          </span>
                          <ChevronRight
                            className={cn(
                              'size-4 shrink-0 transition-transform',
                              activa ? cn(color.texto, 'translate-x-0.5') : 'text-muted-foreground'
                            )}
                          />
                        </button>

                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon-sm" title="Acciones de la torre">
                              <MoreVertical />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="w-44">
                            <DropdownMenuItem
                              onSelect={() => setFormTorre({ editando: fila, nombre: fila.nombre })}
                            >
                              <Pencil />
                              Renombrar
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              variant="destructive"
                              onSelect={() => setBorrando({ tipo: 'torre', torre: fila })}
                            >
                              <Trash2 />
                              Eliminar
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </li>
                  )
                })}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <DoorOpen className="size-4 text-chart-1" />
              {torre ? `Apartamentos de la torre ${torre.nombre}` : 'Apartamentos'}
            </CardTitle>
            <CardDescription>
              {torre
                ? 'Al registrar un residente se elige uno de estos.'
                : 'Elige una torre para ver sus apartamentos.'}
            </CardDescription>
            {torre && (
              <div className="col-start-2 row-span-2 row-start-1 self-start justify-self-end">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setFormApto({ editando: null, numero: '' })}
                >
                  <Plus />
                  Apartamento
                </Button>
              </div>
            )}
          </CardHeader>
          <CardContent>
            {torre === null ? (
              <p className="py-10 text-center text-sm text-muted-foreground">
                Ninguna torre seleccionada.
              </p>
            ) : cargandoAptos ? (
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                {[0, 1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-16 w-full rounded-lg" />
                ))}
              </div>
            ) : apartamentos.length === 0 ? (
              <div className="flex flex-col items-center gap-3 py-10 text-center">
                <DoorOpen className="size-9 text-muted-foreground opacity-40" />
                <div>
                  <p className="font-medium">La torre {torre.nombre} no tiene apartamentos</p>
                  <p className="text-sm text-muted-foreground">
                    Agrega el primero para poder asignarle residentes.
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => setFormApto({ editando: null, numero: '' })}
                >
                  <Plus />
                  Agregar apartamento
                </Button>
              </div>
            ) : (
              <div ref={rejillaAptos} className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                {apartamentos.map((apto) => (
                  <div
                    key={apto.id_apartamento}
                    data-animar
                    className="flex items-center gap-2 rounded-lg border bg-card p-2.5 transition-shadow hover:shadow-sm"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="metric truncate font-medium leading-tight">{apto.numero}</p>
                      <p className="mt-0.5 flex items-center gap-1 text-xs text-muted-foreground">
                        <Users className="size-3 shrink-0" />
                        {apto.residentes}
                      </p>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon-xs" title="Acciones del apartamento">
                          <MoreVertical />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-44">
                        <DropdownMenuItem
                          onSelect={() => setFormApto({ editando: apto, numero: apto.numero })}
                        >
                          <Pencil />
                          Cambiar numero
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          variant="destructive"
                          onSelect={() => setBorrando({ tipo: 'apartamento', apartamento: apto })}
                        >
                          <Trash2 />
                          Eliminar
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Dialog open={formTorre !== null} onOpenChange={(abierto) => !abierto && setFormTorre(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {formTorre?.editando === null ? 'Crear torre' : 'Renombrar torre'}
            </DialogTitle>
            <DialogDescription>
              El nombre no se repite. Puede ser un numero, una letra o un nombre corto.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={guardarTorre} className="space-y-4">
            <FloatingInput
              id="nombre-torre"
              label="Nombre de la torre"
              icon="apartment"
              value={formTorre?.nombre ?? ''}
              onChange={(v) =>
                setFormTorre((previo) => (previo ? { ...previo, nombre: v } : previo))
              }
              required
            />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setFormTorre(null)}>
                Cancelar
              </Button>
              <Button type="submit">{formTorre?.editando === null ? 'Crear' : 'Guardar'}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={formApto !== null} onOpenChange={(abierto) => !abierto && setFormApto(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {formApto?.editando === null ? 'Agregar apartamento' : 'Cambiar numero'}
            </DialogTitle>
            <DialogDescription>
              {torre && `Torre ${torre.nombre}. El numero no se repite dentro de la torre.`}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={guardarApartamento} className="space-y-4">
            <FloatingInput
              id="numero-apto"
              label="Numero del apartamento"
              icon="door_front"
              value={formApto?.numero ?? ''}
              onChange={(v) =>
                setFormApto((previo) => (previo ? { ...previo, numero: v } : previo))
              }
              required
            />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setFormApto(null)}>
                Cancelar
              </Button>
              <Button type="submit">{formApto?.editando === null ? 'Agregar' : 'Guardar'}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={borrando !== null} onOpenChange={(abierto) => !abierto && setBorrando(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {borrando?.tipo === 'torre' ? 'Eliminar torre' : 'Eliminar apartamento'}
            </DialogTitle>
            <DialogDescription>
              {borrando?.tipo === 'torre'
                ? `Torre ${borrando.torre.nombre}`
                : borrando?.tipo === 'apartamento'
                  ? `Apartamento ${borrando.apartamento.numero} de la torre ${borrando.apartamento.torre}`
                  : ''}
            </DialogDescription>
          </DialogHeader>
          <p className="text-sm">
            {borrando?.tipo === 'torre'
              ? 'Solo se puede eliminar si ya no tiene apartamentos.'
              : 'Solo se puede eliminar si ya no tiene residentes registrados.'}
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setBorrando(null)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={() => void borrar()}>
              <Trash2 />
              Eliminar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
