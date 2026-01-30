@echo off
echo =================================
echo   Iniciando AgroMonitor Caldart
echo =================================

echo[
echo 1. Ativando ambiente virtual...
if exist venv\Scripts\activate (
    call venv\Scripts\activate
    echo Ambiente virtual ativado.
) else (
    echo ATENCAO: Pasta venv nao encontrada. Usando Python global.
)

echo[
echo 2. Iniciando Servidor API (Dashboard)...
start "AgroMonitor API Server" cmd /k "python services/api/main.py"

echo Aguardando 5 segundos para a API iniciar...
timeout /t 5 >nul

echo[
echo 3. Iniciando Leitura do Arduino (Ingestor)...
start "AgroMonitor Sensor Ingestor" cmd /k "python services/ingestor/main.py"

echo[
echo ===================================================
echo   SISTEMA RODANDO
echo   Acesse o Dashboard: http://localhost:8000
echo ===================================================
echo[
pause
