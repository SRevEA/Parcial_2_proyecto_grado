'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { Camera, CircleAlert } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { enviarArchivos } from '@/lib/api'

export const MUESTRAS = 5
const MS_ENTRE_MUESTRAS = 600

type Props = {
  idResidente: number
  alTerminar: () => void
}

export function CapturadorRostro({ idResidente, alTerminar }: Props) {
  const video = useRef<HTMLVideoElement>(null)
  const flujo = useRef<MediaStream | null>(null)
  const [listo, setListo] = useState(false)
  const [capturando, setCapturando] = useState(false)
  const [tomadas, setTomadas] = useState<string[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelado = false

    async function encender() {
      try {
        const medios = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480 },
        })
        if (cancelado) {
          medios.getTracks().forEach((pista) => pista.stop())
          return
        }
        flujo.current = medios
        if (video.current) {
          video.current.srcObject = medios
          await video.current.play()
        }
        setListo(true)
      } catch {
        setError('No se pudo acceder a la camara. Revisa el permiso del navegador.')
      }
    }

    void encender()
    return () => {
      cancelado = true
      flujo.current?.getTracks().forEach((pista) => pista.stop())
    }
  }, [])

  const tomarCuadro = useCallback((): Promise<Blob | null> => {
    const elemento = video.current
    if (!elemento) return Promise.resolve(null)
    const lienzo = document.createElement('canvas')
    lienzo.width = elemento.videoWidth || 640
    lienzo.height = elemento.videoHeight || 480
    lienzo.getContext('2d')?.drawImage(elemento, 0, 0)
    return new Promise((resolver) => lienzo.toBlob(resolver, 'image/jpeg', 0.9))
  }, [])

  async function capturar() {
    setCapturando(true)
    setTomadas([])
    const imagenes: Blob[] = []
    const vistas: string[] = []

    for (let i = 0; i < MUESTRAS; i += 1) {
      const cuadro = await tomarCuadro()
      if (cuadro) {
        imagenes.push(cuadro)
        vistas.push(URL.createObjectURL(cuadro))
        setTomadas([...vistas])
      }
      if (i < MUESTRAS - 1) {
        await new Promise((listo) => setTimeout(listo, MS_ENTRE_MUESTRAS))
      }
    }

    try {
      const formulario = new FormData()
      imagenes.forEach((imagen, i) => formulario.append('imagenes', imagen, `muestra-${i}.jpg`))
      const salida = await enviarArchivos<{ agregados: number; total: number }>(
        `/residentes/${idResidente}/patrones`,
        formulario
      )
      toast.success(`Se guardaron ${salida.agregados} patrones. Total: ${salida.total}.`)
      alTerminar()
    } catch (fallo) {
      toast.error(
        fallo instanceof Error ? fallo.message : 'No se pudieron guardar los patrones'
      )
    } finally {
      setCapturando(false)
    }
  }

  if (error) {
    return (
      <div className="flex items-start gap-2 rounded-md border border-destructive/40 bg-destructive/5 p-3 text-sm text-destructive">
        <CircleAlert className="mt-0.5 size-4 shrink-0" />
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <video
        ref={video}
        playsInline
        muted
        className="w-full rounded-md border bg-black"
      />

      <div className="flex items-center gap-1.5">
        {Array.from({ length: MUESTRAS }, (_, i) => (
          <span
            key={i}
            className={cn(
              'h-1.5 flex-1 rounded-full transition-colors',
              i < tomadas.length ? 'bg-status-ok' : 'bg-muted'
            )}
          />
        ))}
      </div>

      <p className="text-xs text-muted-foreground">
        Mira al frente. Se toman {MUESTRAS} muestras con una pausa corta entre cada una.
      </p>

      <Button onClick={capturar} disabled={!listo || capturando} className="w-full">
        <Camera />
        {capturando ? `Capturando ${tomadas.length}/${MUESTRAS}...` : 'Capturar patron facial'}
      </Button>

      {tomadas.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {tomadas.map((url) => (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              key={url}
              src={url}
              alt="muestra"
              className="size-16 rounded-md border object-cover"
            />
          ))}
        </div>
      )}
    </div>
  )
}
