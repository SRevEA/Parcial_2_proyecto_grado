import { borrar, leer } from './sesion'
import type { ErrorApi, Respuesta } from './tipos'

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8100/api/v1'

export class FalloApi extends Error {
  readonly code: string
  readonly statusCode: number
  readonly details: unknown[]

  constructor(cuerpo: ErrorApi) {
    super(cuerpo.error.message)
    this.code = cuerpo.error.code
    this.statusCode = cuerpo.statusCode
    this.details = cuerpo.error.details
  }
}

function cabeceras(extra?: HeadersInit): HeadersInit {
  const sesion = leer()
  return {
    ...(sesion ? { Authorization: `Bearer ${sesion.token}` } : {}),
    ...extra,
  }
}

async function desenvolver<T>(respuesta: Response): Promise<T> {
  if (respuesta.status === 401) {
    borrar()
  }
  const cuerpo = (await respuesta.json()) as Respuesta<T> | ErrorApi
  if (!cuerpo.success) {
    throw new FalloApi(cuerpo)
  }
  return cuerpo.data
}

export async function obtener<T>(ruta: string): Promise<T> {
  return desenvolver<T>(await fetch(`${BASE}${ruta}`, { headers: cabeceras() }))
}

export async function enviar<T>(ruta: string, cuerpo: unknown, metodo = 'POST'): Promise<T> {
  return desenvolver<T>(
    await fetch(`${BASE}${ruta}`, {
      method: metodo,
      headers: cabeceras({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(cuerpo),
    })
  )
}

export async function enviarArchivos<T>(ruta: string, formulario: FormData): Promise<T> {
  return desenvolver<T>(
    await fetch(`${BASE}${ruta}`, { method: 'POST', headers: cabeceras(), body: formulario })
  )
}

export async function eliminar<T>(ruta: string): Promise<T> {
  return desenvolver<T>(
    await fetch(`${BASE}${ruta}`, { method: 'DELETE', headers: cabeceras() })
  )
}

export function urlMonitor(): string {
  return `${BASE}/accesos/monitor`
}

export async function descargar(ruta: string, nombre: string): Promise<void> {
  const respuesta = await fetch(`${BASE}${ruta}`, { headers: cabeceras() })
  if (!respuesta.ok) {
    await desenvolver(respuesta)
    return
  }
  const url = URL.createObjectURL(await respuesta.blob())
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = nombre
  enlace.click()
  URL.revokeObjectURL(url)
}

export function base(): string {
  return BASE
}

export function escucharMonitor(
  alRecibir: (intento: unknown) => void,
  alFallar: (mensaje: string) => void
): () => void {
  const control = new AbortController()

  async function escuchar(): Promise<void> {
    const respuesta = await fetch(urlMonitor(), {
      headers: cabeceras(),
      signal: control.signal,
    })
    if (!respuesta.ok || !respuesta.body) {
      alFallar(`El monitor respondio ${respuesta.status}`)
      return
    }
    const lector = respuesta.body.getReader()
    const decodificador = new TextDecoder()
    let resto = ''
    for (;;) {
      const { done, value } = await lector.read()
      if (done) break
      resto += decodificador.decode(value, { stream: true })
      const bloques = resto.split('\n\n')
      resto = bloques.pop() ?? ''
      for (const bloque of bloques) {
        for (const linea of bloque.split('\n')) {
          if (linea.startsWith('data: ')) {
            alRecibir(JSON.parse(linea.slice(6)))
          }
        }
      }
    }
  }

  escuchar().catch((error: unknown) => {
    if (error instanceof Error && error.name !== 'AbortError') {
      alFallar(error.message)
    }
  })

  return () => control.abort()
}
