@echo off
setlocal enabledelayedexpansion

:: -----------------------------------------------------------------
:: Script para automatizar la creacion del instalador de CyberTrainer
:: 1. Limpia compilaciones anteriores.
:: 2. Verifica dependencias (Inno Setup).
:: 3. Crea el ejecutable .exe con PyInstaller.
:: 4. Compila el script de Inno Setup para crear el instalador final.
:: -----------------------------------------------------------------

:: --- CONFIGURACION ---
set "APP_NAME=CyberTrainer"
:: Asegurate de que este es el nombre de tu script principal de Python.
set "MAIN_SCRIPT=app.py"
set "ICON_PATH=assets\images\app_icon.ico"
set "ASSETS_FOLDER=assets"
set "INNO_SCRIPT=installer.iss"

TITLE Compilador de %APP_NAME%

echo [PASO 1] Limpiando artefactos de compilaciones anteriores...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist "%APP_NAME%.spec" del "%APP_NAME%.spec"
echo Limpieza completada.

echo.
echo [PASO 2] Verificando dependencias...

:: Buscar el compilador de Inno Setup (ISCC)
set "ISCC_PATH="
for %%i in ("%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe", "%ProgramFiles%\Inno Setup 6\ISCC.exe") do (
    if exist "%%~i" set "ISCC_PATH=%%~i"
)
if defined ISCC_PATH (
    echo Inno Setup encontrado en: !ISCC_PATH!
) else (
    echo ADVERTENCIA: No se encontro Inno Setup en la ruta por defecto.
    echo Se intentara usar la version del PATH del sistema...
    set "ISCC_PATH=ISCC.exe"
)

echo.
echo [PASO 3] Creando el ejecutable de la aplicacion...
if not exist "%MAIN_SCRIPT%" (
    echo.
    echo [ERROR] El script principal '%MAIN_SCRIPT%' no se encuentra.
    echo          Asegurate de que el nombre es correcto en la seccion de CONFIGURACION.
    pause
    exit /b
)

echo Ejecutando PyInstaller para '%MAIN_SCRIPT%'...
:: --add-data "origen;destino": Incluye archivos o carpetas adicionales.
:: El formato para Windows es "ruta\origen;ruta\de\destino_dentro_del_exe".
:: Aquí, incluimos toda la carpeta 'assets' en la raíz del ejecutable,
:: manteniendo su estructura interna (como la subcarpeta 'images').
pyinstaller --name "%APP_NAME%" ^
 --onefile ^
 --windowed ^
 --icon="%ICON_PATH%" ^
 --add-data "%ASSETS_FOLDER%;%ASSETS_FOLDER%" ^
 "%MAIN_SCRIPT%"

if not exist "dist\%APP_NAME%.exe" (
    echo.
    echo [ERROR] PyInstaller no pudo crear el archivo 'dist\%APP_NAME%.exe'. Abortando.
    pause
    exit /b
)
echo Ejecutable creado con exito.

echo.
echo [PASO 4] Compilando el instalador con Inno Setup...
:: Se añade /DSourcePath="%CD%" para pasar la ruta actual del proyecto al script de Inno Setup.
:: Esto asegura que siempre encuentre los archivos (como el icono) sin importar desde donde se ejecute.
"!ISCC_PATH!" /DSourcePath="%CD%" "%INNO_SCRIPT%"

echo.
echo --- PROCESO COMPLETADO ---
echo El instalador para %APP_NAME% deberia estar en la carpeta 'Output'.
pause