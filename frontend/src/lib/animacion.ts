'use client'

import { animate, stagger } from 'animejs'

export function sinMovimiento(): boolean {
  return (
    typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  )
}

export function aparecer(contenedor: HTMLElement | null, selector = '[data-animar]'): void {
  if (!contenedor || sinMovimiento()) return
  const objetivos = contenedor.querySelectorAll(selector)
  if (objetivos.length === 0) return
  animate(objetivos, {
    opacity: [0, 1],
    translateY: [14, 0],
    scale: [0.97, 1],
    duration: 420,
    delay: stagger(35, { start: 20 }),
    ease: 'outCubic',
  })
}

export function latir(elemento: HTMLElement | null): void {
  if (!elemento || sinMovimiento()) return
  animate(elemento, {
    scale: [1, 1.18, 1],
    duration: 420,
    ease: 'outBack',
  })
}

export function resaltar(elemento: HTMLElement | null): void {
  if (!elemento || sinMovimiento()) return
  animate(elemento, {
    opacity: [0.35, 1],
    translateX: [-6, 0],
    duration: 320,
    ease: 'outQuad',
  })
}

export function contar(elemento: HTMLElement | null, desde: number, hasta: number): void {
  if (!elemento) return
  if (sinMovimiento() || desde === hasta) {
    elemento.textContent = String(hasta)
    return
  }
  const estado = { valor: desde }
  animate(estado, {
    valor: hasta,
    duration: 520,
    ease: 'outQuad',
    onUpdate: () => {
      elemento.textContent = String(Math.round(estado.valor))
    },
  })
}
