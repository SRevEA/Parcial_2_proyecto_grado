import time
from datetime import UTC, datetime
from typing import Any

from . import camara, deteccion, disparo, envio, vista
from .config import settings


def _describir(cuerpo: dict[str, Any]) -> tuple[str, tuple[int, int, int]]:
    datos = cuerpo.get('data')
    if not isinstance(datos, dict):
        return 'respuesta sin datos', vista.AMBAR
    similitud = datos.get('similitud')
    if datos.get('resultado') != 'RECONOCIDO':
        return f'No se reconoce ({similitud})', vista.ROJO
    residente = datos.get('residente')
    if not isinstance(residente, dict):
        return f'Reconocido ({similitud})', vista.VERDE
    nombre = f'{residente.get("nombre")} {residente.get("apellido")}'
    ubicacion = f'torre {residente.get("torre")} apto {residente.get("numero")}'
    return f'{nombre} - {ubicacion} ({similitud})', vista.VERDE


def _traducir(tipo: str, dato: Any) -> tuple[str, tuple[int, int, int]] | None:
    if tipo == 'ok':
        return _describir(dato)
    if tipo == 'sin_conexion':
        return 'Sin conexion, intento encolado', vista.AMBAR
    if tipo == 'rechazado':
        return f'Rechazado por el backend ({dato})', vista.AMBAR
    if tipo == 'reenviado':
        print(f'reenviado intento en cola {dato}')
    elif tipo == 'descartado':
        print(f'intento en cola descartado: {dato}')
    elif tipo == 'encolados':
        print(f'{dato} intentos pendientes de envio')
    return None


def main() -> None:
    captura = camara.abrir(settings.CAMARA_INDICE)
    envio.iniciar()
    print(f'punto {settings.PUNTO_ACCESO_ID} contra {settings.BACKEND_URL}')
    print(f'envia cuando el rostro lleve {settings.SEGUNDOS_ESTABLE} s quieto')

    ventana = settings.MOSTRAR_VENTANA and vista.disponible()
    if ventana:
        print('ventana abierta: q o Esc para salir')
    elif settings.MOSTRAR_VENTANA:
        print(
            'sin soporte grafico en OpenCV, se sigue sin ventana. '
            'Para tenerla: pip uninstall opencv-python-headless y reinstalar opencv-python'
        )

    estado, color = 'Esperando', vista.AMBAR
    fps = 0.0
    anterior = time.monotonic()
    try:
        while True:
            cuadro = camara.leer(captura)
            if cuadro is None:
                time.sleep(0.1)
                continue

            for tipo, dato in envio.resultados():
                traducido = _traducir(tipo, dato)
                if traducido is not None:
                    estado, color = traducido
                    print(estado)

            ahora = time.monotonic()
            transcurrido = ahora - anterior
            anterior = ahora
            if transcurrido > 0:
                instante = 1 / transcurrido
                fps = instante if fps == 0.0 else fps * 0.9 + instante * 0.1

            caras = deteccion.detectar(cuadro)
            decision = disparo.evaluar(caras, ahora, envio.ocupado())

            if ventana:
                pie = decision.etiqueta or estado
                tinta = vista.AMBAR if decision.etiqueta else color
                if not vista.mostrar(vista.dibujar(cuadro.copy(), caras, pie, tinta, fps)):
                    break

            if decision.enviar:
                envio.enviar(camara.a_jpg(cuadro), datetime.now(UTC))
    except KeyboardInterrupt:
        pass
    finally:
        print('detenido')
        envio.detener()
        captura.release()
        if ventana:
            vista.cerrar()


if __name__ == '__main__':
    main()
