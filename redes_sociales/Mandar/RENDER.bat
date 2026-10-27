@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ==================================================
echo   REEL FERRO - CHACO FOR EVER  (1080x1920, 30 fps)
echo ==================================================
echo.

where node >nul 2>nul
if errorlevel 1 goto :nonode

if exist node_modules goto :render
echo [1/2] Instalando dependencias (solo la primera vez)...
call npm install
if errorlevel 1 goto :fail

:render
if not exist out mkdir out
echo.
echo [2/2] Renderizando video. La primera vez descarga Chrome Headless (necesita internet).
echo.
call npx remotion render src/index.ts FerroReel out/reel_ferro_oeste.mp4 --gl=angle
if errorlevel 1 goto :fail

echo.
echo LISTO: %~dp0out\reel_ferro_oeste.mp4
start "" "%~dp0out"
pause
exit /b 0

:nonode
echo [ERROR] No esta instalado Node.js.
echo Instalar la version LTS desde https://nodejs.org y volver a ejecutar este archivo.
pause
exit /b 1

:fail
echo.
echo [ERROR] Algo fallo. Mandar captura de esta ventana.
pause
exit /b 1
