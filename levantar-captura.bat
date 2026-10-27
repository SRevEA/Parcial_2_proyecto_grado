@echo off
setlocal
cd /d "%~dp0"
title Control de acceso - cliente de captura

echo.
echo   Cliente de captura (la camara del punto de acceso)
echo   ==================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo   [X] No encuentro Python en el PATH.
    echo       Instala Python 3.12 o superior y marca "Add python.exe to PATH".
    goto :fin
)

python -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3, 12) else 1)" 2>nul
if errorlevel 1 (
    echo   [X] Necesita Python 3.12 o superior. En el PATH esta:
    python --version
    goto :fin
)

if not exist "cliente-captura\.env" (
    echo   [X] Falta el archivo cliente-captura\.env
    echo       Las claves que necesita estan en cliente-captura\.env.example
    goto :fin
)

if not exist "cliente-captura\.venv\Scripts\python.exe" (
    echo   Creando el entorno virtual.
    python -m venv "cliente-captura\.venv"
    if errorlevel 1 (
        echo   [X] No se pudo crear el entorno virtual.
        goto :fin
    )
)

"cliente-captura\.venv\Scripts\python.exe" -c "import cv2, httpx, pydantic_settings" 2>nul
if errorlevel 1 (
    echo   Instalando dependencias. La primera vez tarda varios minutos.
    pushd cliente-captura
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -e ".[dev]"
    popd
    "cliente-captura\.venv\Scripts\python.exe" -c "import cv2, httpx, pydantic_settings" 2>nul
    if errorlevel 1 (
        echo.
        echo   [X] Las dependencias no quedaron instaladas.
        echo       Mira el error de pip de arriba. Si no dice nada claro, borra
        echo       la carpeta cliente-captura\.venv y vuelve a correr este archivo.
        goto :fin
    )
) else (
    echo   Dependencias: ya instaladas.
)

where curl >nul 2>nul
if not errorlevel 1 (
    curl -s -o nul -m 5 http://127.0.0.1:8100/health
    if errorlevel 1 (
        echo.
        echo   Aviso: el backend no responde en el 8100. Los intentos se van a
        echo   encolar hasta que lo levantes con levantar.bat.
    )
)

echo.
echo   Se abre una ventana con la camara. El recuadro y los puntos salen
echo   cuando detecta un rostro. Mira el panel Monitor para ver el resultado.
echo   Ctrl+C aqui para detener.
echo.

pushd cliente-captura
".venv\Scripts\python.exe" -m cliente.main
popd

:fin
echo.
pause
