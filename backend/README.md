# backend

API REST del sistema de control de acceso por reconocimiento facial.
Python 3.12 + FastAPI + SQLAlchemy contra Supabase (PostgreSQL con `pgvector`).

## Quien lo llama

| Quien | Como se autentica |
|---|---|
| `frontend` | token de sesion en `Authorization: Bearer` |
| `cliente-captura` | cabeceras `X-Punto-Id` y `X-Punto-Api-Key` |
| Infraestructura | `GET /health`, sin credencial |

## Como correr

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8100 --reload
```

En Windows no hace falta activar el entorno: llamando al `python.exe` del
`.venv` directamente funciona igual y no depende de la politica de ejecucion
de PowerShell, que por defecto bloquea `Activate.ps1`.

Desde Git Bash o WSL, cambiar las barras invertidas por barras normales.


Documentacion interactiva en `http://localhost:8100/api/v1/docs`.

## Variables
El archivo tiene que llamarse exactamente `.env`, con el punto al principio y
sin otra extension. Windows oculta las extensiones conocidas, asi que conviene
verificarlo desde la terminal con `dir` o `ls`. Las claves necesarias estan en
`.env.example`.

El `.env` se busca en la carpeta del componente, no en el directorio desde el
que se ejecuta, asi que da igual desde donde se lance.


| Variable | Que es |
|---|---|
| `PORT` | puerto del servidor |
| `SUPABASE_URL` | URL del proyecto de Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | llave de servicio; es la que salta RLS |
| `BUCKET_EVIDENCIAS` | bucket privado de evidencias |
| `DATABASE_URL` | cadena de conexion, en modo **session pooler** |
| `JWT_SECRET` | secreto para firmar los tokens |
| `JWT_HORAS_VIGENCIA` | duracion del token |
| `ORIGENES_PERMITIDOS` | origenes del frontend para CORS |

La cadena de conexion usa el **session pooler** de Supabase (puerto 5432 del host
del pooler). El *transaction pooler* (6543) **no sirve** tal cual: no soporta
prepared statements y asyncpg los usa por defecto.

## Endpoints

| Metodo | Ruta | Para que |
|---|---|---|
| POST | `/api/v1/auth/login` | iniciar sesion |
| GET | `/api/v1/auth/yo` | datos de la sesion actual |
| POST | `/api/v1/auth/contrasena` | cambiar la propia contrasena |
| GET POST PUT | `/api/v1/usuarios` | administradores y vigilantes |
| GET POST PUT DELETE | `/api/v1/residentes` | residentes |
| POST | `/api/v1/residentes/{id}/autorizacion` | registrar la autorizacion de datos |
| POST | `/api/v1/residentes/{id}/patrones` | capturar patrones faciales |
| POST | `/api/v1/residentes/{id}/inactivar` | sacar sus patrones del reconocimiento |
| POST | `/api/v1/reconocimiento/intentos` | el cliente envia un intento |
| GET | `/api/v1/accesos` | historial con filtros |
| GET | `/api/v1/accesos/monitor` | flujo SSE para el panel del vigilante |
| GET | `/api/v1/accesos/exportar` | historial en CSV |
| GET | `/api/v1/accesos/{id}/evidencia` | URL firmada, y queda en auditoria |
| GET PUT | `/api/v1/configuracion` | umbral y periodo de conservacion |
| GET POST PUT DELETE | `/api/v1/catalogo/torres` | el catalogo de torres |
| GET POST PUT DELETE | `/api/v1/catalogo/apartamentos` | los apartamentos de cada torre |

## Estructura

```
app/
├── main.py         app, manejadores de error, health
├── config.py       settings
├── routers/        rutas por modulo
├── schemas/        contrato Pydantic por modulo
├── services/       toda la logica
├── repositories/   uno por tabla, unica capa que toca la base
├── models/         uno por tabla, ORM
├── types/          literales y constantes
├── lib/            db, errores, seguridad, almacenamiento, vision, eventos
└── jobs/           purgado de evidencias vencidas
```

`lib/vision.py` convierte imagen en vector y no decide nada.
`services/reconocimiento.py` decide si ese vector es un residente.

## Una transaccion por peticion

Cada funcion de `repositories/` acepta `session` y, si no la recibe, abre la
suya. Eso cuesta: una consulta sobre una conexion abierta son 75 ms, pero abrir
sesion, reservar conexion, consultar, confirmar y devolver la conexion son
370 ms. Cinco repositories sin pasar la sesion son cinco veces ese costo.

Entonces el router declara `sesion: Sesion` y se la pasa al service, el service
la pasa a todos los repositories, y la autenticacion usa la misma: una peticion
de lectura abre **una** transaccion. Las dos excepciones estan explicadas en
`instrucciones/base-de-datos.md`: el flujo SSE del monitor y la consulta de
evidencia, que confirma su propia transaccion antes de entregar la URL firmada
para no dejar hueco en la bitacora del RNF11.

Los listados filtran, ordenan, paginan y cuentan **en SQL**. El frontend solo
manda parametros.

## Migraciones

SQL plano numerado en `migraciones/`, aplicado a mano. **Nunca en el
entrypoint.** El orden importa: la extension, el esquema, el RLS, la semilla y
despues los cambios. Son once tablas.

## Antes de dar algo por terminado

```sh
ruff check .
ruff format .
mypy app
pytest
```

## Primer administrador y primer punto de acceso

**Las migraciones no crean credenciales a proposito.** Un seed con contrasenas
dentro significa publicar esas contrasenas en el repositorio, y cualquier
despliegue que no las cambie queda abierto.

Se crean una sola vez, con valores propios, ejecutando esto en la base:

```sql
insert into usuario_sistema (nombre, correo, contrasena_hash, rol)
values (
    'Nombre del administrador',
    'correo@dominio.com',
    extensions.crypt('<la contrasena>', extensions.gen_salt('bf')),
    'ADMINISTRADOR'
);

insert into punto_acceso (nombre, ubicacion, api_key_hash)
values (
    'Porteria principal',
    'Entrada peatonal',
    extensions.crypt('<la credencial del equipo>', extensions.gen_salt('bf'))
);
```

La credencial del equipo se genera aleatoria y se guarda **solo** en el `.env`
del `cliente-captura`, junto con el `id_punto` que devolvio el insert. En la
base queda unicamente su hash.

El correo no puede usar un dominio reservado como `.local`: el validador de
correos lo rechaza y el login responderia 422.
