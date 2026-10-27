'use client'

import { useEffect, useRef } from 'react'
import { contar } from '@/lib/animacion'

export function Contador({ valor }: { valor: number }) {
  const ref = useRef<HTMLSpanElement>(null)
  const previo = useRef(0)

  useEffect(() => {
    contar(ref.current, previo.current, valor)
    previo.current = valor
  }, [valor])

  return <span ref={ref}>{valor}</span>
}
