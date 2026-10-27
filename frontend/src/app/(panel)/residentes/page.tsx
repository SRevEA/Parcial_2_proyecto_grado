'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { Building2, Plus, Trash2, UsersRound } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { ChipSelector, type ChipOption } from '@/components/ui/chip-selector'
import { FloatingInput } from '@/components/ui/floating-input'
import { Skeleton } from '@/components/ui/skeleton'
import { BarraFiltros } from '@/components/panel/barra-filtros'
import { CapturadorRostro } from '@/components/panel/capturador-rostro'
import { Contador } from '@/components/panel/contador'
import { Encabezado } from '@/components/panel/encabezado'
import { Paginacion } from '@/components/panel/paginacion'
import { TarjetaResidente } from '@/components/panel/tarjeta-residente'
import { eliminar, enviar, obtener } from '@/lib/api'
import { aparecer } from '@/lib/animacion'
import type { Apartamento, Estado, Pagina, Residente, Torre } from '@/lib/tipos'

const POR_PAGINA = 24
const MS_ESPERA_BUSQUEDA = 350

const VACIO = { nombre: '', apellido: '', documento: '', idTorre: '', idApartamento: '' }

const TEXTO_AUTORIZACION =
  'Autorizo el tratamiento de mis datos biometricos para la verificacion de identidad en el ' +
  'control de acceso del conjunto y la conservacion temporal de evidencias fotograficas.'

type FiltroEstado = 'TODOS' | Estado
type FiltroSiNo = 'TODOS' | 'SI' | 'NO'

const ESTADOS: ChipOption<FiltroEstado>[] = [
  { key: 'TODOS', label: 'Todos', icon: 'done_all' },
  { key: 'ACTIVO', label: 'Activos', icon: 'check_circle' },
  { key: 'INACTIVO', label: 'Inactivos', icon: 'cancel' },
]

const AUTORIZACIONES: ChipOption<FiltroSiNo>[] = [
  { key: 'TODOS', label: 'Todas', icon: 'done_all' },
  { key: 'SI', label: 'Con autorizacion', icon: 'how_to_reg' },
  { key: 'NO', label: 'Sin autorizacion', icon: 'gpp_bad' },
]

const PATRONES: ChipOption<FiltroSiNo>[] = [
  { key: 'TODOS', label: 'Todos', icon: 'done_all' },
  { key: 'SI', label: 'Con patron', icon: 'fingerprint' },
  { key: 'NO', label: 'Sin patron', icon: 'block' },
]

function bandera(valor: FiltroSiNo): string | null {
  if (valor === 'TODOS') return null
  return valor === 'SI' ? 'true' : 'false'
}

export default function Residentes() {
  const [residentes, setResidentes] = useState<Residente[]>([])
  const [total, setTotal] = useState(0)
  const [pagina, setPagina] = useState(0)
  const [cargando, setCargando] = useState(true)

  const [busqueda, setBusqueda] = useState('')
  const [buscado, setBuscado] = useState('')
  const [estado, setEstado] = useState<FiltroEstado>('TODOS')
  const [autorizacion, setAutorizacion] = useState<FiltroSiNo>('TODOS')
  const [patrones, setPatrones] = useState<FiltroSiNo>('TODOS')

  const [torres, setTorres] = useState<Torre[]>([])
  const [aptos, setAptos] = useState<Apartamento[]>([])

  const [formulario, setFormulario] = useState(VACIO)
  const [editando, setEditando] = useState<number | null>(null)
  const [formAbierto, setFormAbierto] = useState(false)
  const [capturando, setCapturando] = useState<Residente | null>(null)
  const [autorizando, setAutorizando] = useState<Residente | null>(null)
  const [suprimiendo, setSuprimiendo] = useState<Residente | null>(null)

  const rejilla = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const espera = setTimeout(() => {
      setBuscado(busqueda)
      setPagina(0)
    }, MS_ESPERA_BUSQUEDA)
    return () => clearTimeout(espera)
  }, [busqueda])

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      const p = new URLSearchParams()
      if (buscado) p.set('buscar', buscado)
      if (estado !== 'TODOS') p.set('estado', estado)
      const conAutorizacion = bandera(autorizacion)
      if (conAutorizacion) p.set('autorizacion', conAutorizacion)
      const conPatrones = bandera(patrones)
      if (conPatrones) p.set('patrones', conPatrones)
      p.set('limite', String(POR_PAGINA))
      p.set('desplazamiento', String(pagina * POR_PAGINA))

      const pedido = await obtener<Pagina<Residente>>(`/residentes?${p.toString()}`)
      if (pedido.items.length === 0 && pagina > 0) {
        setPagina(pagina - 1)
        return
      }
      setResidentes(pedido.items)
      setTotal(pedido.total)
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo cargar la lista')
    } finally {
      setCargando(false)
    }
  }, [buscado, estado, autorizacion, patrones, pagina])

  useEffect(() => {
    void cargar()
  }, [cargar])

  const cargarTorres = useCallback(async () => {
    try {
      const pedido = await obtener<Pagina<Torre>>('/catalogo/torres')
      setTorres(pedido.items)
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo cargar el catalogo')
    }
  }, [])

  useEffect(() => {
    void cargarTorres()
  }, [cargarTorres])

  useEffect(() => {
    if (!formulario.idTorre) {
      setAptos([])
      return
    }
    async function cargarAptos(idTorre: string) {
      try {
        const pedido = await obtener<Pagina<Apartamento>>(
          `/catalogo/apartamentos?id_torre=${idTorre}`
        )
        setAptos(pedido.items)
      } catch (fallo) {
        toast.error(
          fallo instanceof Error ? fallo.message : 'No se pudieron cargar los apartamentos'
        )
      }
    }
    void cargarAptos(formulario.idTorre)
  }, [formulario.idTorre])

  useEffect(() => {
    if (!cargando) aparecer(rejilla.current)
  }, [cargando, residentes])

  const abrirNuevo = useCallback(() => {
    setEditando(null)
    setFormulario(VACIO)
    setFormAbierto(true)
  }, [])

  function abrirEdicion(residente: Residente) {
    setEditando(residente.id_residente)
    setFormulario({
      nombre: residente.nombre,
      apellido: residente.apellido,
      documento: residente.documento,
      idTorre: String(residente.id_torre),
      idApartamento: String(residente.id_apartamento),
    })
    setFormAbierto(true)
  }

  function limpiar() {
    setBusqueda('')
    setBuscado('')
    setEstado('TODOS')
    setAutorizacion('TODOS')
    setPatrones('TODOS')
    setPagina(0)
  }

  function cambiarFiltro<T>(aplicar: (valor: T) => void): (valor: T) => void {
    return (valor) => {
      aplicar(valor)
      setPagina(0)
    }
  }

  async function guardar(evento: React.FormEvent) {
    evento.preventDefault()
    if (!formulario.idApartamento) {
      toast.error('Hay que elegir la torre y el apartamento')
      return
    }
    const cuerpo = {
      nombre: formulario.nombre,
      apellido: formulario.apellido,
      documento: formulario.documento,
      id_apartamento: Number(formulario.idApartamento),
    }
    try {
      if (editando === null) {
        const creado = await enviar<Residente>('/residentes', cuerpo)
        toast.success(
          `${creado.nombre} ${creado.apellido} quedo registrado. Falta la autorizacion.`
        )
      } else {
        await enviar<Residente>(`/residentes/${editando}`, cuerpo, 'PUT')
        toast.success('Datos actualizados.')
      }
      setFormAbierto(false)
      await cargar()
      await cargarTorres()
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo guardar')
    }
  }

  async function autorizar() {
    if (!autorizando) return
    try {
      await enviar(`/residentes/${autorizando.id_residente}/autorizacion`, {
        aceptada: true,
        finalidades: TEXTO_AUTORIZACION,
      })
      toast.success('Autorizacion registrada. Ya se puede capturar el patron facial.')
      setAutorizando(null)
      await cargar()
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo registrar la autorizacion')
    }
  }

  async function cambiarEstado(residente: Residente) {
    const accion = residente.estado === 'ACTIVO' ? 'inactivar' : 'activar'
    try {
      await enviar(`/residentes/${residente.id_residente}/${accion}`, {})
      await cargar()
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo cambiar el estado')
    }
  }

  async function suprimir() {
    if (!suprimiendo) return
    try {
      await eliminar(`/residentes/${suprimiendo.id_residente}`)
      toast.success('Residente y datos biometricos suprimidos.')
      setSuprimiendo(null)
      await cargar()
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo suprimir')
    }
  }

  const opcionesTorre: ChipOption<string>[] = torres.map((fila) => ({
    key: String(fila.id_torre),
    label: fila.nombre,
    icon: 'apartment',
  }))

  const opcionesApto: ChipOption<string>[] = aptos.map((fila) => ({
    key: String(fila.id_apartamento),
    label: fila.numero,
    icon: 'door_front',
  }))

  const filtrosActivos = [
    buscado !== '',
    estado !== 'TODOS',
    autorizacion !== 'TODOS',
    patrones !== 'TODOS',
  ].filter(Boolean).length

  return (
    <div className="space-y-5">
      <Encabezado
        accion={
          <Button onClick={abrirNuevo}>
            <Plus />
            Registrar residente
          </Button>
        }
      />

      <BarraFiltros
        busqueda={busqueda}
        alBuscar={setBusqueda}
        marcador="Nombre, documento, torre o apartamento"
        activos={filtrosActivos}
        alLimpiar={limpiar}
      >
        <ChipSelector<FiltroEstado>
          label="Estado"
          icon="toggle_on"
          options={ESTADOS}
          value={estado}
          onChange={cambiarFiltro(setEstado)}
          className="w-full lg:w-44"
          floatingLabel
        />
        <ChipSelector<FiltroSiNo>
          label="Autorizacion"
          icon="verified_user"
          options={AUTORIZACIONES}
          value={autorizacion}
          onChange={cambiarFiltro(setAutorizacion)}
          className="w-full lg:w-52"
          floatingLabel
        />
        <ChipSelector<FiltroSiNo>
          label="Patron facial"
          icon="face"
          options={PATRONES}
          value={patrones}
          onChange={cambiarFiltro(setPatrones)}
          className="w-full lg:w-48"
          floatingLabel
        />
      </BarraFiltros>

      <p className="text-sm text-muted-foreground">
        {cargando ? (
          'Cargando...'
        ) : (
          <>
            <Contador valor={total} />
            {total === 1 ? ' residente' : ' residentes'}
            {filtrosActivos > 0 && ' con los filtros aplicados'}
          </>
        )}
      </p>

      {cargando ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-60 w-full rounded-xl" />
          ))}
        </div>
      ) : residentes.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed py-16 text-center">
          <UsersRound className="size-10 text-muted-foreground opacity-40" />
          <div>
            <p className="font-medium">
              {filtrosActivos > 0 ? 'Ningun residente coincide' : 'Todavia no hay residentes'}
            </p>
            <p className="text-sm text-muted-foreground">
              {filtrosActivos > 0
                ? 'Prueba quitando algun filtro.'
                : 'El orden es registrar, autorizar y recien entonces capturar.'}
            </p>
          </div>
          {filtrosActivos > 0 ? (
            <Button variant="outline" onClick={limpiar}>
              Limpiar los filtros
            </Button>
          ) : (
            <Button onClick={abrirNuevo}>
              <Plus />
              Registrar residente
            </Button>
          )}
        </div>
      ) : (
        <div ref={rejilla} className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {residentes.map((residente) => (
            <TarjetaResidente
              key={residente.id_residente}
              residente={residente}
              alAutorizar={() => setAutorizando(residente)}
              alCapturar={() => setCapturando(residente)}
              alEditar={() => abrirEdicion(residente)}
              alCambiarEstado={() => void cambiarEstado(residente)}
              alSuprimir={() => setSuprimiendo(residente)}
            />
          ))}
        </div>
      )}

      <Paginacion pagina={pagina} total={total} porPagina={POR_PAGINA} alCambiar={setPagina} />

      <Dialog open={formAbierto} onOpenChange={setFormAbierto}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editando === null ? 'Registrar residente' : 'Editar residente'}
            </DialogTitle>
            <DialogDescription>
              Al registrarlo queda sin autorizacion y sin patrones faciales.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={guardar} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <FloatingInput
                id="nombre"
                label="Nombre"
                icon="person"
                value={formulario.nombre}
                onChange={(v) => setFormulario({ ...formulario, nombre: v })}
                required
              />
              <FloatingInput
                id="apellido"
                label="Apellido"
                icon="person"
                value={formulario.apellido}
                onChange={(v) => setFormulario({ ...formulario, apellido: v })}
                required
              />
              <FloatingInput
                id="documento"
                label="Documento"
                icon="badge"
                value={formulario.documento}
                onChange={(v) => setFormulario({ ...formulario, documento: v })}
                required
              />
              <ChipSelector<string>
                label="Torre"
                icon="apartment"
                options={opcionesTorre}
                value={formulario.idTorre}
                onChange={(valor) =>
                  setFormulario({ ...formulario, idTorre: valor, idApartamento: '' })
                }
                floatingLabel
              />
              <ChipSelector<string>
                label="Apartamento"
                icon="door_front"
                options={opcionesApto}
                value={formulario.idApartamento}
                onChange={(valor) => setFormulario({ ...formulario, idApartamento: valor })}
                floatingLabel
              />
            </div>
            {torres.length === 0 && (
              <p className="flex items-start gap-2 rounded-md border border-chart-2/30 bg-chart-2/5 p-3 text-xs text-chart-2">
                <Building2 className="mt-0.5 size-4 shrink-0" />
                No hay torres en el catalogo. Creala primero en Configuracion y vuelve a este
                formulario.
              </p>
            )}
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setFormAbierto(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={torres.length === 0}>
                {editando === null ? 'Registrar' : 'Guardar cambios'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog
        open={autorizando !== null}
        onOpenChange={(abierto) => !abierto && setAutorizando(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Autorizacion de tratamiento de datos</DialogTitle>
            <DialogDescription>
              {autorizando && `${autorizando.nombre} ${autorizando.apellido}`}
            </DialogDescription>
          </DialogHeader>
          <p className="rounded-md border bg-muted/50 p-3 text-sm leading-relaxed">
            {TEXTO_AUTORIZACION}
          </p>
          <p className="text-xs text-muted-foreground">
            Sin esta autorizacion el sistema rechaza la captura del patron facial.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAutorizando(null)}>
              Cancelar
            </Button>
            <Button onClick={() => void autorizar()}>Registrar autorizacion</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={capturando !== null}
        onOpenChange={(abierto) => !abierto && setCapturando(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Capturar patron facial</DialogTitle>
            <DialogDescription>
              {capturando && `${capturando.nombre} ${capturando.apellido}`}
            </DialogDescription>
          </DialogHeader>
          {capturando && (
            <CapturadorRostro
              idResidente={capturando.id_residente}
              alTerminar={() => {
                setCapturando(null)
                void cargar()
              }}
            />
          )}
        </DialogContent>
      </Dialog>

      <Dialog
        open={suprimiendo !== null}
        onOpenChange={(abierto) => !abierto && setSuprimiendo(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Suprimir definitivamente</DialogTitle>
            <DialogDescription>
              {suprimiendo && `${suprimiendo.nombre} ${suprimiendo.apellido}`}
            </DialogDescription>
          </DialogHeader>
          <p className="text-sm">
            Se borran sus patrones faciales y las evidencias asociadas. No se puede deshacer.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSuprimiendo(null)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={() => void suprimir()}>
              <Trash2 />
              Suprimir
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
