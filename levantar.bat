@echo off
setlocal
cd /d "%~dp0"
title Control de acceso - levantar

echo.
echo   Control de acceso por reconocimiento facial
echo   ===========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo   [X] No encuentro Python en el PATH.
    echo       Instala Python 3.12 o superior y marca "Add python.exe to PATH".
    goto :fin
)

python -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3, 12) else 1)" 2>nul
if errorlevel 1 (
    echo   [X] El backend necesita Python 3.12 o superior. En el PATH esta:
    python --version
    goto :fin
)

where npm >nul 2>nul
if errorlevel 1 (
    echo   [X] No encuentro Node.js en el PATH. Instala Node 20 o superior.
    goto :fin
)

if not exist "backend\.env" (
    echo   [X] Falta el archivo backend\.env
    echo       Las claves que necesita estan en backend\.env.example
    goto :fin
)

if not exist "frontend\.env.local" (
    echo   [X] Falta el archivo frontend\.env.local
    echo       La clave que necesita esta en frontend\.env.local.example
    goto :fin
)

if not exist "backend\.venv\Scripts\python.exe" (
    echo   [1/2] Backend: creando el entorno virtual.
    python -m venv "backend\.venv"
    if errorlevel 1 (
        echo   [X] No se pudo crear el entorno virtual del backend.
        goto :fin
    )
)

"backend\.venv\Scripts\python.exe" -c "import uvicorn, fastapi, sqlalchemy" 2>nul
if errorlevel 1 (
    echo   [1/2] Backend: instalando dependencias. La primera vez tarda varios minutos.
    pushd backend
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -e ".[dev]"
    popd
    "backend\.venv\Scripts\python.exe" -c "import uvicorn, fastapi, sqlalchemy" 2>nul
    if errorlevel 1 (
        echo.
        echo   [X] Las dependencias del backend no quedaron instaladas.
        echo       Mira el error de pip de arriba. Si no dice nada claro, borra
        echo       la carpeta backend\.venv y vuelve a correr este archivo.
        goto :fin
    )
) else (
    echo   [1/2] Backend: ya instalado.
)

if exist "frontend\node_modules\next\package.json" (
    echo   [2/2] Panel: ya instalado.
) else (
    echo   [2/2] Panel: instalando dependencias. La primera vez tarda varios minutos.
    pushd frontend
    call npm install --no-fund --no-audit
    popd
    if not exist "frontend\node_modules\next\package.json" (
        echo.
        echo   [X] Las dependencias del panel no quedaron instaladas.
        echo       Mira el error de npm de arriba.
        goto :fin
    )
)

echo.
echo   Abriendo dos ventanas: backend en el 8100 y panel en el 3000.
start "backend" /d "%cd%\backend" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8100"
start "panel" /d "%cd%\frontend" cmd /k "npm run dev"

echo   Esperando a que el panel responda...
where curl >nul 2>nul
if errorlevel 1 (
    ping -n 13 127.0.0.1 >nul
    goto :abrir
)
set INTENTO=0

:esperar
ping -n 3 127.0.0.1 >nul
curl -s -o nul -m 3 http://127.0.0.1:3000
if not errorlevel 1 goto :abrir
set /a INTENTO+=1
if %INTENTO% lss 20 goto :esperar

:abrir
start "" http://localhost:3000

echo.
echo   Listo. El panel quedo en http://localhost:3000
echo   Para probar la camara de la porteria, corre levantar-captura.bat.
echo   Para detener todo, cierra las dos ventanas que se abrieron.

:fin
echo.
pause
