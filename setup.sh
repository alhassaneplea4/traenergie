#!/bin/bash
set -e

echo "=========================================="
echo "  TRAENERGIE - Installation & Démarrage"
echo "=========================================="
echo ""

# Create virtual environment
echo "[1/6] Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "[2/6] Installation des dépendances..."
pip install -r requirements.txt

# Copy env file
echo "[3/6] Configuration de l'environnement..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Fichier .env créé. Modifiez-le si nécessaire."
fi

# Run migrations
echo "[4/6] Création de la base de données..."
python manage.py migrate

# Load fixtures
echo "[5/6] Chargement des données initiales..."
python manage.py loaddata apps/website/fixtures/initial_data.json
python manage.py loaddata apps/stock/fixtures/initial_data.json

# Create superuser
echo "[6/6] Création du compte administrateur..."
echo ""
echo "Entrez les informations du super-administrateur :"
python manage.py createsuperuser

echo ""
echo "=========================================="
echo "  ✅ Installation terminée !"
echo "=========================================="
echo ""
echo "Démarrer le serveur :"
echo "  python manage.py runserver"
echo ""
echo "Accès :"
echo "  Site web     → http://127.0.0.1:8000/"
echo "  Dashboard    → http://127.0.0.1:8000/dashboard/"
echo "  Admin Django → http://127.0.0.1:8000/admin/"
echo ""
