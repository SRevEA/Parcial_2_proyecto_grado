# cliente-captura

Cliente que corre en el equipo del punto de acceso. Captura de la camara,
verifica que haya un rostro y transmite el intento al backend.

No tiene interfaz: corre desatendido.

## Que lleva y que no

Lleva **solo YuNet** (232 KB) para detectar que hay una cara. El vector de 128
dimensiones lo extrae el backend, no este cliente. Por eso el equipo del punto
de acceso puede ser de bajas prestaciones.

## Como correr

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m cliente.main
```

En Windows no hace falta activar el entorno: llamando al `python.exe` del
`.venv` directamente funciona igual y no depende de la politica de ejecucion
de PowerShell, que por defecto bloquea `Activate.ps1`.

Desde Git Bash o WSL, cambiar las barras invertidas por barras normales.


Se detiene con Ctrl+C.

## Variables
El archivo tiene que llamarse exactamente `.env`, con el punto al principio y
sin otra extension. Windows oculta las extensiones conocidas, asi que conviene
verificarlo desde la terminal con `dir` o `ls`. Las claves necesarias estan en
`.env.example`.

El `.env` se busca en la carpeta del componente, no en el directorio desde el
que se ejecuta, asi que da igual desde donde se lance.


| Variable | Que es |
|---|---|
| `BACKEND_URL` | URL base del backend, sin `/api/v1` |
| `PUNTO_ACCESO_ID` | id del punto de acceso en la base |
| `PUNTO_ACCESO_API_KEY` | credencial del equipo; en la base solo vive su hash |
| `CAMARA_INDICE` | indice de la camara, 0 por defecto |
| `SEGUNDOS_ESTABLE` | segundos que el rostro debe estar quieto antes de enviar, 2 por defecto |
| `MOVIMIENTO_TOLERADO` | cuanto se puede mover sin reiniciar la cuenta, como fraccion del tamano del rostro (0.08 = 8%) |
| `SEGUNDOS_SIN_ROSTRO` | cuanto tiene que faltar el rostro para considerar que es otra persona, 1 por defecto |
| `SEGUNDOS_ENTRE_INTENTOS` | piso entre envios, 3 por defecto |
| `SEGUNDOS_REINTENTO_COLA` | cada cuanto se intenta vaciar la cola |
| `RUTA_COLA` | archivo SQLite de la cola local |
| `MOSTRAR_VENTANA` | abre la ventana de monitoreo local, `true` por defecto |

## La ventana de monitoreo

Mientras corre abre una ventana con la imagen de la camara, el recuadro de cada
rostro detectado y sus cinco puntos de referencia, mas una barra superior con el
resultado del ultimo intento: verde si reconocio, rojo si no, ambar mientras
espera. Se cierra con `q` o `Esc`.

Es solo local, para ver que esta pasando en el punto de acceso. **No transmite
video**: lo que viaja al servidor siguen siendo unicamente las capturas con un
rostro, como pide el RF13.

En un equipo sin pantalla hay que apagarla con `MOSTRAR_VENTANA=false`, porque
sin servidor grafico la llamada que dibuja la ventana falla. Apagada, la
deteccion solo corre cuando toca enviar, en vez de en cada cuadro.

## La cola local

Si el backend no responde **por falta de conexion**, el intento se guarda en un
SQLite local y se reenvia al reconectar. El cliente nunca se detiene.

Un rechazo del backend (por ejemplo, la imagen no tenia exactamente un rostro)
**no se encola**: se descarta. Solo se encolan los fallos de red.

## Estructura

```
cliente/
├── main.py       el bucle de camara y la ventana
├── config.py     settings
├── camara.py     abrir la camara y entregar cuadros
├── deteccion.py  responder si hay un rostro
├── disparo.py    decidir cuando se envia
├── vista.py      dibujar el recuadro y los puntos
├── envio.py      el hilo que habla con el backend y maneja la cola
├── api.py        las llamadas HTTP
└── cola.py       persistencia de lo que no se pudo enviar
```

## Cuando se envia un intento

**No se envia cada vez que se ve un rostro.** `disparo.py` espera a que el
rostro se quede **quieto** `SEGUNDOS_ESTABLE` seguidos, y entonces manda **un
solo** intento. Mientras esa persona siga ahi no manda nada mas, aunque se
mueva un poco. Para que vuelva a enviar, el rostro tiene que desaparecer
`SEGUNDOS_SIN_ROSTRO` y volver: eso es otra persona, u otro paso de la misma.

La quietud se mide sobre el recuadro del rostro: si el centro o el tamano se
corren mas de `MOVIMIENTO_TOLERADO` del tamano del propio rostro, la cuenta
arranca de nuevo. Es mas barato y mas directo que comparar cuadros enteros, y
es justo lo que interesa: que la persona este plantada mirando a la camara.

**Por que importa:** antes mandaba uno cada `SEGUNDOS_ENTRE_INTENTOS` mientras
hubiera una cara enfrente. Un cliente olvidado corriendo con alguien sentado al
frente generaba mas de 600 intentos por hora, cada uno con su fotografia en
Storage y su fila en la base. Ahora un paso por la porteria es un registro.

Tambien ayuda al reconocimiento: el cuadro que se manda es uno en el que la
persona esta quieta, no uno borroso a mitad de movimiento.

La ventana muestra la cuenta en vivo (`Quieto... 1.4s`) y los fps reales, para
ver si la camara esta rindiendo o no.

## Por que el envio va en un hilo aparte

El bucle de camara no espera a la red. Enviar un intento implica subir la
imagen, que el backend extraiga el vector, consulte la base y guarde la
evidencia en Storage; hacerlo de forma sincrona congelaba la ventana en cada
intento. `envio.py` corre en su propio hilo, con su propia conexion a SQLite
para la cola local, y el bucle solo le deja trabajo y recoge resultados.

La deteccion tambien se abarato: corre sobre una copia reescalada a 640 px de
ancho y las coordenadas se devuelven al tamano original para dibujar. Son 8 ms
por cuadro en vez de 29 sobre 720p. La imagen que viaja al backend sigue siendo
la completa, sin reescalar, para no perder calidad en el reconocimiento ni en la
evidencia.
