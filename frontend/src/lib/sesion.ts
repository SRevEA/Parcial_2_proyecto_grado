import type { Sesion } from './tipos'

const CLAVE = 'sesion'

export function guardar(sesion: Sesion): void {
  try {
    localStorage.setItem(CLAVE, JSON.stringify(sesion))
  } catch {}
}

export function leer(): Sesion | null {
  try {
    const crudo = localStorage.getItem(CLAVE)
    return crudo ? (JSON.parse(crudo) as Sesion) : null
  } catch {
    return null
  }
}

export function borrar(): void {
  try {
    localStorage.removeItem(CLAVE)
  } catch {}
}
