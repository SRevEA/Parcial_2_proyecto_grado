# Sistema de seguridad por reconocimiento facial

Control de acceso para conjuntos residenciales. El sistema reconoce a los
residentes en la portería a partir de su rostro, deja registro de cada intento
—reconocido o no— y le muestra al vigilante lo que está pasando en tiempo real.
Es nuestro proyecto de grado.

Lo armamos en tres componentes, cada uno en su carpeta:

| Carpeta | Qué es | Dónde corre |
|---|---|---|
| `backend` | la API REST, el reconocimiento y el acceso a la base | el servidor |
| `cliente-captura` | la cámara del punto de acceso | el equipo de la portería |
| `frontend` | el panel del administrador y del vigilante | el navegador |

**El reconocimiento lo hace el servidor, no la portería.** El equipo del punto
de acceso solo captura, comprueba que haya un rostro y transmite. Así el equipo
de la portería puede ser de bajas prestaciones: lleva el detector, que pesa
232 KB, y no el modelo que calcula los vectores, que pesa 39 MB.

## Cómo funciona un acceso, de principio a fin

1. El cliente de captura detecta un rostro y espera a que la persona se quede
   **quieta dos segundos**. Entonces manda **un** intento, con su marca de
   tiempo de captura.
2. El backend extrae el vector de 128 dimensiones del rostro y le pregunta a
   Postgres cuál es el patrón más parecido entre los residentes activos.
3. Si la similitud coseno pasa el umbral, el intento queda como reconocido con
   su residente; si no, queda registrado igual, sin residente.
4. La fotografía del intento se guarda como evidencia, con su hash y su fecha de
   expiración.
5. El panel del vigilante recibe el resultado por un flujo de eventos y muestra
   la foto, el nombre y el apartamento.

Entre el paso 1 y el paso 5 medimos **0,85 s**.

## Stack

| Capa | Tecnología |
|---|---|
| API | Python 3.12, FastAPI, SQLAlchemy |
| Base de datos | PostgreSQL (Supabase) con `pgvector` |
| Detección de rostros | YuNet (ONNX sobre OpenCV) |
| Vectores faciales | SFace, 128 dimensiones, similitud coseno |
| Evidencias | Supabase Storage, con URL firmada |
| Panel web | Next.js 16, React 19, Tailwind |
| Cliente de captura | Python 3.12, OpenCV |

Todo el software que usamos es libre o de código abierto.

## Cómo levantarlo

### En Windows, sin tocar la terminal

1. Poner el `.env` de cada componente en su carpeta. Las claves que lleva cada
   uno están en el `.env.example` de al lado.
2. Doble clic en **`levantar.bat`**.

Instala lo que falte la primera vez, abre el backend y el panel en dos ventanas
y abre el navegador cuando el panel ya responde. Para la cámara de la portería,
**`levantar-captura.bat`** en la máquina que la tenga conectada.

Si falta algo, el `.bat` lo dice y se detiene en vez de arrancar a medias: qué
archivo falta o qué hay que instalar. Necesita Python 3.12 o superior y Node 20
o superior en el `PATH`.

### A mano

Cada componente tiene su propio `README.md` con sus variables y su comando.
Resumen:

```sh
cd backend          && pip install -e ".[dev]" && uvicorn app.main:app --port 8100
cd frontend         && npm install && npm run dev
cd cliente-captura  && pip install -e ".[dev]" && python -m cliente.main
```

El archivo de entorno de cada componente **no se versiona**.

## El panel

| Vista | Para qué | Quién entra |
|---|---|---|
| Monitor | el intento que acaba de pasar, con su foto, y el histórico al lado | vigilante y administrador |
| Historial | todos los intentos, con filtros, evidencias y exportación a CSV | vigilante y administrador |
| Residentes | registrar, autorizar, capturar el rostro y suprimir | administrador |
| Usuarios | administradores y vigilantes | administrador |
| Configuración | el umbral, la conservación de evidencias y el catálogo de torres | administrador |

## Base de datos

Once tablas, en `backend/migraciones/`. Se aplican en orden y **nunca** desde el
entrypoint del contenedor: una migración que corre sola en cada despliegue es
una forma cómoda de perder datos.

Lo que vale la pena saber del diseño:

- Los patrones faciales se guardan como `vector(128)` y la comparación por
  similitud coseno la resuelve Postgres con un índice HNSW. No se comparan
  vectores en memoria.
- Del registro de un residente **no se conserva ninguna fotografía**, solo los
  vectores.
- De cada intento sí se guarda una evidencia fotográfica, con su hash SHA-256 y
  una fecha de expiración tras la cual se elimina sola.
- Ningún patrón facial entra sin la autorización previa del titular: si falta,
  el backend rechaza la captura con `412`.
- Las torres y los apartamentos son un catálogo, no texto libre. Un apartamento
  pertenece a una torre, y al registrar un residente se elige uno que exista.
- Todas las tablas tienen RLS habilitado y sin políticas, así que el único
  camino a los datos es el backend con su llave de servicio.

## Privacidad

Los datos biométricos son datos sensibles bajo la Ley 1581 de 2012. El sistema
guarda la autorización expresa del titular con la versión de la política que
aceptó, permite consultar, actualizar y suprimir sus datos, y deja en bitácora
de auditoría cada vez que alguien abre una evidencia fotográfica.
