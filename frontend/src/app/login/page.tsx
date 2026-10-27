'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ScanFace } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { FloatingInput } from '@/components/ui/floating-input'
import { enviar } from '@/lib/api'
import { guardar } from '@/lib/sesion'
import type { Sesion } from '@/lib/tipos'

export default function Login() {
  const router = useRouter()
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [enviando, setEnviando] = useState(false)

  async function entrar(evento: React.FormEvent) {
    evento.preventDefault()
    setEnviando(true)
    try {
      const sesion = await enviar<Sesion>('/auth/login', { correo, contrasena })
      guardar(sesion)
      router.replace(sesion.rol === 'VIGILANTE' ? '/monitor' : '/residentes')
    } catch (fallo) {
      toast.error(fallo instanceof Error ? fallo.message : 'No se pudo iniciar sesion')
      setEnviando(false)
    }
  }

  return (
    <main className="grid min-h-screen place-items-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <div className="mb-2 flex size-11 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <ScanFace className="size-6" />
          </div>
          <CardTitle className="text-xl">Control de acceso</CardTitle>
          <CardDescription>
            Reconocimiento facial para conjuntos residenciales
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={entrar} className="space-y-4">
            <FloatingInput
              id="correo"
              label="Correo"
              type="email"
              icon="mail"
              value={correo}
              onChange={setCorreo}
              required
            />
            <FloatingInput
              id="contrasena"
              label="Contrasena"
              type="password"
              icon="lock"
              value={contrasena}
              onChange={setContrasena}
              required
            />
            <Button type="submit" className="w-full" disabled={enviando}>
              {enviando ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  )
}
