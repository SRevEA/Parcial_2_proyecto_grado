'use client'

import { useEffect, useState } from 'react'

export const MOVIL = '(max-width: 1023px)'

export function usarMedia(consulta: string): boolean {
  const [coincide, setCoincide] = useState(false)

  useEffect(() => {
    const lista = window.matchMedia(consulta)
    setCoincide(lista.matches)
    function alCambiar(evento: MediaQueryListEvent) {
      setCoincide(evento.matches)
    }
    lista.addEventListener('change', alCambiar)
    return () => lista.removeEventListener('change', alCambiar)
  }, [consulta])

  return coincide
}

export function usarEsMovil(): boolean {
  return usarMedia(MOVIL)
}
