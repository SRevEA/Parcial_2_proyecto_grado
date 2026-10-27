'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { Plus, Users } from 'lucide-react'
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
import { Contador } from '@/components/panel/contador'
import { Encabezado } from '@/components/panel/encabezado'
import { POR_PAGINA, Paginacion } from '@/components/panel/paginacion'
import { TarjetaUsuario } from '@/components/panel/tarjeta-usuario'
import { enviar, obtener } from '@/lib/api'
import { aparecer } from '@/lib/animacion'
import type { Estado, Pagina, Rol, Usuario } from '@/lib/tipos'

const MS_ESPERA_BUSQUEDA = 350

const VACIO = { nombre: '', correo: '', contrasena: '', rol: 'VIGILANTE' as Rol }

const ROLES: ChipOption<Rol>[] = [
  { key: 'VIGILANTE', label: 'Vigilante', icon: 'visibility' },
  { key: 'ADMINISTRADOR', label: 'Administrador', icon: 'admin_panel_settings' },
]

type FiltroRol = 'TODOS' | Rol
type FiltroEstado = 'TODOS' | Estado

const FILTRO_ROLES: ChipOption<FiltroRol>[] = [
  { key: 'TODOS', label: 'Todos', icon: 'done_all' },
  { key: 'ADMINISTRADOR', label: 'Administradores', icon: 'admin_panel_settings' },
  { key: 'VIGILANTE', label: 'Vigilantes', icon: 'visibility' },
]

const FILTRO_ESTADOS: ChipOption<FiltroEstado>[] = [
  { key: 'TODOS', label: 'Todos', icon: 'done_all' },
  { key: 'ACTIVO', label: 'Activos', icon: 'check_circle' },
  { key: 'INACTIVO', label: 'Inactivos', icon: 'cancel' },
]

export default function Usuarios() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [total, setTotal] = useState(0)
  const [pagina, setPagina] = useState(0)
  const [cargando, setCargando] = useState(true)

  const [busqueda, setBusqueda] = useState('')
  const [buscado, setBuscado] = useState('')
  const [rol, setRol] = useState<FiltroRol>('TODOS')
  const [estado, setEstado] = useState<FiltroEstado>('TODOS')

  const [formulario, setFormulario] = useState(VACIO)
  const [editando, setEditando] = useState<Usuario | null>(null)
  const [abierto, setAbierto] = useState(false)

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
      if (rol !== 'TODOS') p.set('rol', rol)
      if (estado !== 'TODOS') p.set('estado', estado)
      p.set('limite', String(POR_PAGINA))
      p.set('desplazamiento', String(pagina * POR_PAGINA))

      const pedido = await obtener<Pagina<Usuario>>(`/usuarios?${p.toString()}`)
      if (pedido.items.length === 0 && pagina > 0) {
        setPagina(pagina - 1)
        return
      }
      setUsuarios(pedido.items)
      setTotal(pedido.total)
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo cargar la lista')
    } finally {
      setCargando(false)
    }
  }, [buscado, rol, estado, pagina])

  useEffect(() => {
    void cargar()
  }, [cargar])

  useEffect(() => {
    if (!cargando) aparecer(rejilla.current)
  }, [cargando, usuarios])

  function abrirNuevo() {
    setEditando(null)
    setFormulario(VACIO)
    setAbierto(true)
  }

  function abrirEdicion(usuario: Usuario) {
    setEditando(usuario)
    setFormulario({
      nombre: usuario.nombre,
      correo: usuario.correo,
      contrasena: '',
      rol: usuario.rol,
    })
    setAbierto(true)
  }

  function limpiar() {
    setBusqueda('')
    setBuscado('')
    setRol('TODOS')
    setEstado('TODOS')
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
    try {
      if (editando === null) {
        const creado = await enviar<Usuario>('/usuarios', formulario)
        toast.success(`Usuario ${creado.correo} creado.`)
      } else {
        await enviar(
          `/usuarios/${editando.id_usuario}`,
          { nombre: formulario.nombre, rol: formulario.rol, estado: editando.estado },
          'PUT'
        )
        toast.success('Usuario actualizado.')
      }
      setFormulario(VACIO)
      setAbierto(false)
      await cargar()
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo guardar el usuario')
    }
  }

  async function alternarEstado(usuario: Usuario) {
    try {
      await enviar(
        `/usuarios/${usuario.id_usuario}`,
        {
          nombre: usuario.nombre,
          rol: usuario.rol,
          estado: usuario.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO',
        },
        'PUT'
      )
      await cargar()
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo cambiar el estado')
    }
  }

  const filtrosActivos = [buscado !== '', rol !== 'TODOS', estado !== 'TODOS'].filter(
    Boolean
  ).length

  return (
    <div className="space-y-5">
      <Encabezado
        accion={
          <Button onClick={abrirNuevo}>
            <Plus />
            Crear usuario
          </Button>
        }
      />

      <BarraFiltros
        busqueda={busqueda}
        alBuscar={setBusqueda}
        marcador="Nombre o correo"
        activos={filtrosActivos}
        alLimpiar={limpiar}
      >
        <ChipSelector<FiltroRol>
          label="Rol"
          icon="shield_person"
          options={FILTRO_ROLES}
          value={rol}
          onChange={cambiarFiltro(setRol)}
          className="w-full lg:w-52"
          floatingLabel
        />
        <ChipSelector<FiltroEstado>
          label="Estado"
          icon="toggle_on"
          options={FILTRO_ESTADOS}
          value={estado}
          onChange={cambiarFiltro(setEstado)}
          className="w-full lg:w-44"
          floatingLabel
        />
      </BarraFiltros>

      <p className="text-sm text-muted-foreground">
        {cargando ? (
          'Cargando...'
        ) : (
          <>
            <Contador valor={total} />
            {total === 1 ? ' usuario' : ' usuarios'}
            {filtrosActivos > 0 && ' con los filtros aplicados'}
          </>
        )}
      </p>

      {cargando ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-52 w-full rounded-xl" />
          ))}
        </div>
      ) : usuarios.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed py-16 text-center">
          <Users className="size-10 text-muted-foreground opacity-40" />
          <div>
            <p className="font-medium">
              {filtrosActivos > 0 ? 'Ningun usuario coincide' : 'Todavia no hay usuarios'}
            </p>
            <p className="text-sm text-muted-foreground">
              {filtrosActivos > 0
                ? 'Prueba quitando algun filtro.'
                : 'El administrador gestiona; el vigilante monitorea y consulta.'}
            </p>
          </div>
          {filtrosActivos > 0 ? (
            <Button variant="outline" onClick={limpiar}>
              Limpiar los filtros
            </Button>
          ) : (
            <Button onClick={abrirNuevo}>
              <Plus />
              Crear usuario
            </Button>
          )}
        </div>
      ) : (
        <div ref={rejilla} className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {usuarios.map((usuario) => (
            <TarjetaUsuario
              key={usuario.id_usuario}
              usuario={usuario}
              alEditar={() => abrirEdicion(usuario)}
              alCambiarEstado={() => void alternarEstado(usuario)}
            />
          ))}
        </div>
      )}

      <Paginacion pagina={pagina} total={total} alCambiar={setPagina} />

      <Dialog open={abierto} onOpenChange={setAbierto}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editando === null ? 'Crear usuario' : 'Editar usuario'}</DialogTitle>
            <DialogDescription>
              {editando === null
                ? 'La contrasena debe tener al menos 8 caracteres.'
                : `El correo ${editando.correo} no se puede cambiar.`}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={guardar} className="space-y-4">
            <FloatingInput
              id="nombre"
              label="Nombre"
              icon="person"
              value={formulario.nombre}
              onChange={(v) => setFormulario({ ...formulario, nombre: v })}
              required
            />
            {editando === null && (
              <>
                <FloatingInput
                  id="correo"
                  label="Correo"
                  type="email"
                  icon="mail"
                  value={formulario.correo}
                  onChange={(v) => setFormulario({ ...formulario, correo: v })}
                  required
                />
                <FloatingInput
                  id="contrasena"
                  label="Contrasena"
                  type="password"
                  icon="lock"
                  value={formulario.contrasena}
                  onChange={(v) => setFormulario({ ...formulario, contrasena: v })}
                  required
                />
              </>
            )}
            <ChipSelector<Rol>
              label="Rol"
              icon="shield_person"
              options={ROLES}
              value={formulario.rol}
              onChange={(valor) => setFormulario({ ...formulario, rol: valor })}
              floatingLabel
            />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setAbierto(false)}>
                Cancelar
              </Button>
              <Button type="submit">{editando === null ? 'Crear' : 'Guardar cambios'}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
