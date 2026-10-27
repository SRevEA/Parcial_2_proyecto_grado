create table usuario_sistema (
    id_usuario      serial primary key,
    nombre          varchar(80)  not null,
    correo          varchar(120) not null unique,
    contrasena_hash varchar(255) not null,
    rol             varchar(20)  not null check (rol in ('ADMINISTRADOR', 'VIGILANTE')),
    estado          varchar(10)  not null default 'ACTIVO' check (estado in ('ACTIVO', 'INACTIVO')),
    creado          timestamptz  not null default now()
);

create table apartamento (
    id_apartamento serial primary key,
    torre          varchar(20) not null,
    numero         varchar(20) not null,
    unique (torre, numero)
);

create table residente (
    id_residente   serial primary key,
    nombre         varchar(80) not null,
    apellido       varchar(80) not null,
    documento      varchar(20) not null unique,
    id_apartamento integer     not null references apartamento (id_apartamento),
    estado         varchar(10) not null default 'ACTIVO' check (estado in ('ACTIVO', 'INACTIVO')),
    creado         timestamptz not null default now()
);

create table autorizacion_datos (
    id_autorizacion  serial primary key,
    id_residente     integer     not null unique references residente (id_residente) on delete cascade,
    aceptada         boolean     not null,
    finalidades      text        not null,
    version_politica varchar(20) not null,
    fecha            timestamptz not null default now()
);

create table patron_facial (
    id_patron    serial primary key,
    id_residente integer     not null references residente (id_residente) on delete cascade,
    embedding    vector(128) not null,
    creado       timestamptz not null default now()
);

create index patron_facial_embedding_idx
    on patron_facial using hnsw (embedding vector_cosine_ops);

create index patron_facial_residente_idx on patron_facial (id_residente);

create table punto_acceso (
    id_punto     serial primary key,
    nombre       varchar(80)  not null,
    ubicacion    varchar(120),
    api_key_hash varchar(255) not null,
    estado       varchar(10)  not null default 'ACTIVO' check (estado in ('ACTIVO', 'INACTIVO')),
    creado       timestamptz  not null default now()
);

create table registro_acceso (
    id_registro  bigserial primary key,
    id_punto     integer      not null references punto_acceso (id_punto),
    id_residente integer      references residente (id_residente) on delete set null,
    resultado    varchar(15)  not null check (resultado in ('RECONOCIDO', 'NO_RECONOCIDO')),
    similitud    numeric(5, 4),
    capturado_en timestamptz  not null,
    fecha_hora   timestamptz  not null default now()
);

create index registro_acceso_fecha_hora_idx on registro_acceso (fecha_hora desc);
create index registro_acceso_residente_idx on registro_acceso (id_residente);

create table evidencia_fotografica (
    id_evidencia     bigserial primary key,
    id_registro      bigint       not null unique references registro_acceso (id_registro) on delete cascade,
    ruta_archivo     varchar(255) not null,
    hash_sha256      char(64)     not null,
    fecha_expiracion timestamptz  not null,
    creado           timestamptz  not null default now()
);

create index evidencia_fotografica_expiracion_idx on evidencia_fotografica (fecha_expiracion);

create table configuracion (
    clave       varchar(60) primary key,
    valor       text        not null,
    descripcion varchar(200),
    actualizado timestamptz not null default now()
);

create table consulta_evidencia (
    id_consulta  bigserial primary key,
    id_evidencia bigint      references evidencia_fotografica (id_evidencia) on delete set null,
    id_usuario   integer     not null references usuario_sistema (id_usuario),
    fecha_hora   timestamptz not null default now()
);

create index consulta_evidencia_fecha_hora_idx on consulta_evidencia (fecha_hora desc);
