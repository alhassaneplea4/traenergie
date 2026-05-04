@echo off
echo ==========================================
echo   TRAENERGIE - Installation & Demarrage
echo ==========================================
echo.

REM Create virtual environment
echo [1/6] Creation de l'environnement virtuel...
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
echo [2/6] Installation des dependances...
pip install -r requirements.txt

REM Copy env file
echo [3/6] Configuration de l'environnement...
if not exist .env (
    copy .env.example .env
    echo Fichier .env cree. Modifiez-le si necessaire.
)

REM Run migrations
echo [4/6] Creation de la base de donnees...
python manage.py migrate

REM Load fixtures
echo [5/6] Chargement des donnees initiales...
python manage.py loaddata apps/website/fixtures/initial_data.json
python manage.py loaddata apps/stock/fixtures/initial_data.json

REM Create superuser
echo [6/6] Creation du compte administrateur...
echo.
echo Entrez les informations du super-administrateur :
python manage.py createsuperuser

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
