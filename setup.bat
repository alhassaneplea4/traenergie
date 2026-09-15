@echo off
setlocal
set "PYTHON=venv\Scripts\python.exe"

echo ==========================================
echo   TRAENERGIE - Installation ^& Demarrage
echo ==========================================
echo.

REM Create virtual environment
echo [1/6] Creation de l'environnement virtuel...
python -m venv venv
if errorlevel 1 goto :error
if not exist "%PYTHON%" goto :error

echo Utilisation de :
"%PYTHON%" --version

REM Install dependencies
echo [2/6] Installation des dependances...
"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto :error
"%PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 goto :error

REM Copy env file
echo [3/6] Configuration de l'environnement...
if not exist .env (
    copy .env.example .env
    echo Fichier .env cree. Modifiez-le si necessaire.
)

REM Run migrations
echo [4/6] Creation de la base de donnees...
"%PYTHON%" manage.py migrate
if errorlevel 1 goto :error

REM Load fixtures
echo [5/6] Chargement des donnees initiales...
"%PYTHON%" manage.py loaddata apps/website/fixtures/initial_data.json
if errorlevel 1 goto :error
"%PYTHON%" manage.py loaddata apps/stock/fixtures/initial_data.json
if errorlevel 1 goto :error

echo.
echo ==========================================
echo   Installation terminee avec succes !
echo ==========================================
echo.
echo Demarrer le serveur avec :
echo   python manage.py runserver
echo.
echo Acces :
echo   Site web     : http://127.0.0.1:8000/
echo   Dashboard    : http://127.0.0.1:8000/dashboard/
echo   Admin Django : http://127.0.0.1:8000/admin/
echo.
pause
exit /b 0

:error
echo.
echo ==========================================
echo   Installation interrompue : une erreur est survenue.
echo ==========================================
echo Verifiez le message ci-dessus, puis relancez setup.bat.
pause
exit /b 1
