'use client'

import { useCallback, useEffect, useState } from 'react'
import { Save, SlidersHorizontal } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Catalogo } from '@/components/panel/catalogo'
import { Encabezado } from '@/components/panel/encabezado'
import { Skeleton } from '@/components/ui/skeleton'
import { enviar, obtener } from '@/lib/api'
import type { ClaveValor, Pagina } from '@/lib/tipos'

export default function Configuracion() {
  const [claves, setClaves] = useState<ClaveValor[]>([])
  const [borrador, setBorrador] = useState<Record<string, string>>({})
  const [cargando, setCargando] = useState(true)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      const pagina = await obtener<Pagina<ClaveValor>>('/configuracion')
      setClaves(pagina.items)
      setBorrador(Object.fromEntries(pagina.items.map((c) => [c.clave, c.valor])))
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo cargar la configuracion')
    } finally {
      setCargando(false)
    }
  }, [])

  useEffect(() => {
    void cargar()
  }, [cargar])

  async function guardar(clave: string) {
    try {
      await enviar(`/configuracion/${clave}`, { valor: borrador[clave] }, 'PUT')
      toast.success(`${clave} actualizado.`)
      await cargar()
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo guardar')
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-5">
      <Encabezado />

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <SlidersHorizontal className="size-4 text-chart-2" />
            Parametros del reconocimiento
          </CardTitle>
          <CardDescription>
            El umbral es una similitud coseno entre 0 y 1: mayor es mas parecido. El valor de
            referencia del motor es 0.363. Subirlo hace el sistema mas estricto, con menos falsos
            positivos y mas falsos negativos.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {cargando
            ? [0, 1, 2].map((i) => <Skeleton key={i} className="h-16 w-full" />)
            : claves.map((clave, indice) => (
                <div key={clave.clave} className="space-y-3">
                  {indice > 0 && <Separator />}
                  <div className="flex flex-wrap items-end gap-3">
                    <div className="min-w-0 flex-1 space-y-1.5">
                      <Label htmlFor={clave.clave} className="metric text-xs">
                        {clave.clave}
                      </Label>
                      {clave.descripcion && (
                        <p className="text-xs text-muted-foreground">{clave.descripcion}</p>
                      )}
                    </div>
                    <Input
                      id={clave.clave}
                      className="metric w-36"
                      value={borrador[clave.clave] ?? ''}
                      onChange={(e) => setBorrador({ ...borrador, [clave.clave]: e.target.value })}
                    />
                    <Button
                      variant="outline"
                      disabled={borrador[clave.clave] === clave.valor}
                      onClick={() => void guardar(clave.clave)}
                    >
                      <Save />
                      Guardar
                    </Button>
                  </div>
                </div>
              ))}
        </CardContent>
      </Card>

      <Catalogo />
    </div>
  )
}
