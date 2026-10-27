# frontend

Panel del administrador y del vigilante. Next.js 16 con React 19 y Tailwind.

## Como correr

```sh
npm install
npm run dev
```

Queda en `http://localhost:3000`. Necesita el backend arriba.

## Variables

| Variable | Que es |
|---|---|
| `NEXT_PUBLIC_API_URL` | base de la API, incluyendo `/api/v1` |

Va en `.env.local`. Conviene apuntarla a `127.0.0.1` y no a `localhost`:
resolver `localhost` en Windows cuesta unos 200 ms por peticion, porque intenta
primero por IPv6 y el backend escucha en IPv4.

## Pantallas

| Ruta | Caso de uso | Quien entra |
|---|---|---|
| `/login` | UC01 | todos |
| `/monitor` | UC09, UC13 | vigilante y administrador |
| `/historial` | UC08, UC14 | vigilante y administrador |
| `/residentes` | UC02 a UC06 | solo administrador |
| `/usuarios` | UC07 | solo administrador |
| `/configuracion` | RF20, catalogo de torres | solo administrador |

## Estructura

```
src/
├── app/
│   ├── login/          la entrada
│   └── (panel)/        el armazon y las cinco vistas de adentro
├── components/
│   ├── panel/          lo que es de este sistema
│   └── ui/             la biblioteca de componentes
└── lib/
    ├── api.ts          el cliente de la API y el flujo del monitor
    ├── sesion.ts       el token en el navegador
    ├── tipos.ts         los contratos que devuelve el backend
    ├── animacion.ts    las animaciones, con anime.js
    ├── colores.ts      los acentos por registro
    └── pantalla.ts     si estamos en movil
```

## Reglas que seguimos

**Nada de logica de datos aqui.** Filtrar, buscar, ordenar, paginar, contar y
calcular derivados es trabajo del backend. Las vistas mandan parametros y
dibujan lo que reciben. Si falta un filtro, se agrega al endpoint, no al
componente: con paginacion, filtrar en memoria solo filtraria la pagina visible
y el total saldria mal.

**Un solo encabezado por vista.** Cada vista dibuja su titulo y su boton de
accion; la barra de arriba solo lleva el armazon (ocultar el menu, la marca en
movil y el menu del perfil, con el modo oscuro adentro).

**En movil, el menu es una barra inferior** y los filtros salen en un panel
desde abajo.

**Las animaciones respetan `prefers-reduced-motion`.** Si el sistema pide menos
movimiento, no se animan, y nada depende de que la animacion corra: las
tarjetas no se dibujan invisibles esperando que algo las revele.

## Dos detalles

**El capturador de rostro** (`components/panel/capturador-rostro.tsx`) es la
unica parte que toca hardware: pide permiso de camara al navegador y toma las
cinco muestras del registro. Necesita `localhost` o HTTPS, porque los
navegadores no dan camara en origenes no seguros.

**El monitor no usa `EventSource`.** `EventSource` no puede enviar cabeceras,
asi que el token no viajaria y el backend responderia 401. El flujo SSE se
consume con `fetch` en streaming desde `lib/api.ts`.

## Antes de dar algo por terminado

```sh
npm run typecheck
npm run build
```
