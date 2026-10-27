import os

os.environ.setdefault('SUPABASE_URL', 'https://pruebas.supabase.co')
os.environ.setdefault('SUPABASE_SERVICE_ROLE_KEY', 'llave-de-pruebas')
os.environ.setdefault('BUCKET_EVIDENCIAS', 'evidencias')
os.environ.setdefault('DATABASE_URL', 'postgresql+asyncpg://u:p@localhost:5432/postgres')
os.environ.setdefault('JWT_SECRET', 'secreto-de-pruebas-suficientemente-largo-para-hs256')
