from typing import Literal

Rol = Literal['ADMINISTRADOR', 'VIGILANTE']
Estado = Literal['ACTIVO', 'INACTIVO']
Resultado = Literal['RECONOCIDO', 'NO_RECONOCIDO']

CLAVE_UMBRAL = 'umbral_similitud'
CLAVE_DIAS_EVIDENCIA = 'dias_conservacion_evidencia'
CLAVE_VERSION_POLITICA = 'version_politica_datos'

MUESTRAS_REGISTRO = 5

ZONA_HORARIA = 'America/Bogota'
