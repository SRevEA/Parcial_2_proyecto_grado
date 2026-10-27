export type Rol = 'ADMINISTRADOR' | 'VIGILANTE'
export type Estado = 'ACTIVO' | 'INACTIVO'
export type Resultado = 'RECONOCIDO' | 'NO_RECONOCIDO'

export type Respuesta<T> = { success: true; statusCode: number; data: T }
export type Pagina<T> = { items: T[]; total: number }

export type ErrorApi = {
  success: false
  statusCode: number
  error: { code: string; message: string; details: unknown[] }
}

export type Sesion = {
  token: string
  id_usuario: number
  nombre: string
  rol: Rol
}

export type Torre = {
  id_torre: number
  nombre: string
  apartamentos: number
}

export type Apartamento = {
  id_apartamento: number
  id_torre: number
  torre: string
  numero: string
  residentes: number
}

export type Residente = {
  id_residente: number
  nombre: string
  apellido: string
  documento: string
  id_apartamento: number
  id_torre: number
  torre: string
  numero: string
  estado: Estado
  muestras: number
  tiene_autorizacion: boolean
}

export type Usuario = {
  id_usuario: number
  nombre: string
  correo: string
  rol: Rol
  estado: Estado
}

export type Registro = {
  id_registro: number
  id_punto: number
  resultado: Resultado
  similitud: number | null
  id_residente: number | null
  nombre_residente: string | null
  torre: string | null
  numero: string | null
  capturado_en: string
  fecha_hora: string
  segundos_respuesta: number
  tiene_evidencia: boolean
}

export type Evidencia = {
  id_evidencia: number
  id_registro: number
  url: string
  hash_sha256: string
  fecha_expiracion: string
}

export type ClaveValor = {
  clave: string
  valor: string
  descripcion: string | null
}

export type Intento = {
  id_registro: number
  id_punto: number
  resultado: Resultado
  similitud: number
  umbral: number
  residente: {
    id_residente: number
    nombre: string
    apellido: string
    torre: string
    numero: string
  } | null
  capturado_en: string
  fecha_hora: string
  segundos_respuesta: number
  imagen?: string
}
