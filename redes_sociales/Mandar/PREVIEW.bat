@echo off
chcp 65001 >nul
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Falta Node.js LTS: https://nodejs.org
  pause
  exit /b 1
)
if not exist node_modules call npm install
call npx remotion studio
