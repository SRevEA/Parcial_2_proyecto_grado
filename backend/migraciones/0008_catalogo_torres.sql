create table torre (
    id_torre serial primary key,
    nombre   varchar(20) not null unique,
    creado   timestamptz not null default now()
);

alter table torre enable row level security;

revoke all on torre from anon, authenticated;
revoke all on sequence torre_id_torre_seq from anon, authenticated;

insert into torre (nombre)
select distinct btrim(torre) from apartamento where btrim(torre) <> ''
on conflict (nombre) do nothing;

alter table apartamento
    add column id_torre integer references torre (id_torre) on delete restrict;

update apartamento a set id_torre = t.id_torre
from torre t where btrim(a.torre) = t.nombre;

alter table apartamento alter column id_torre set not null;

alter table apartamento drop constraint apartamento_torre_numero_key;

alter table apartamento drop column torre;

alter table apartamento add constraint apartamento_torre_numero_key unique (id_torre, numero);

create index apartamento_torre_idx on apartamento (id_torre);
