# run.py
import os
import sys
from wsgiref.simple_server import make_server
from pathlib import Path
from django.core.wsgi import get_wsgi_application

BASE_DIR = Path(__file__).resolve().parent

if __name__ == '__main__':
    # Ajoute le chemin du projet au PYTHONPATH
    sys.path.append(str(BASE_DIR))
    
    # Définit le module de configuration de Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eisf.settings")
    
    # Configure l'application WSGI de Django
    try:
        application = get_wsgi_application()
    except Exception as exc:
        print("Erreur de configuration de l'application Django:", exc)
        sys.exit(1)
    
    # Définit l'hôte et le port du serveur
    host = '0.0.0.0'
    port = 8000
    
    # Lance le serveur simple de Python
    print(f"Lancement du serveur sur http://{host}:{port}/")
    try:
        httpd = make_server(host, port, application)
        httpd.serve_forever()
    except Exception as e:
        print(f"Erreur lors du lancement du serveur: {e}")
        sys.exit(1)