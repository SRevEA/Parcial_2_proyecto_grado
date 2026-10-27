'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { leer } from '@/lib/sesion'

export default function Inicio() {
  const router = useRouter()

  useEffect(() => {
    const sesion = leer()
    if (!sesion) {
      router.replace('/login')
      return
    }
    router.replace(sesion.rol === 'VIGILANTE' ? '/monitor' : '/residentes')
  }, [router])

  return null
}
