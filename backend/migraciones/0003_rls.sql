alter table usuario_sistema        enable row level security;
alter table apartamento            enable row level security;
alter table residente              enable row level security;
alter table autorizacion_datos     enable row level security;
alter table patron_facial          enable row level security;
alter table punto_acceso           enable row level security;
alter table registro_acceso        enable row level security;
alter table evidencia_fotografica  enable row level security;
alter table configuracion          enable row level security;
alter table consulta_evidencia     enable row level security;

revoke all on all tables    in schema public from anon, authenticated;
revoke all on all sequences in schema public from anon, authenticated;
revoke all on all functions in schema public from anon, authenticated;

alter default privileges in schema public revoke all on tables    from anon, authenticated;
alter default privileges in schema public revoke all on sequences from anon, authenticated;
alter default privileges in schema public revoke all on functions from anon, authenticated;
