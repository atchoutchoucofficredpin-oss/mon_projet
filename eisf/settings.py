# settings.py

"""
Django settings for logiciel_gestion project.
"""

from pathlib import Path
import os
import dj_database_url
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Détecter si l'application est en mode "onefile" PyInstaller
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    MEI_PATH = sys._MEIPASS
else:
    # En mode développement, on utilise la racine du projet
    MEI_PATH = BASE_DIR


# Quick-start development settings - unsuitable for production
SECRET_KEY = os.environ.get('SECRET_KEY', 'votre-cle-secrete-generique-pour-le-developpement-local')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Autorise le domaine de Railway et Heroku.
# Railway utilise le domaine .up.railway.app
ALLOWED_HOSTS = ['eisf.herokuapp.com', '127.0.0.1', 'localhost', '192.168.1.4', '0.0.0.0', '.up.railway.app']


# Application definition
INSTALLED_APPS = [
    'jazzmin',  # Le thème Jazzmin doit être en haut de la liste
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestion_produits_stock',
    'widget_tweaks',
]

# Modifié pour inclure WhiteNoise en production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eisf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eisf.wsgi.application'


# Database
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # dj_database_url est déjà configuré pour détecter la base de données
    # de production de services comme Railway ou Heroku
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Bamako'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = []


# Configure WhiteNoise pour servir les fichiers statiques compressés
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Configuration du thème JAZZMIN ---
JAZZMIN_SETTINGS = {
    # Titre qui s'affiche dans la barre de navigation
    "site_title": "ADAMA SOUMARE DISTRIBUTION (ASD)",
    # Titre de la page de connexion
    "site_header": "ADAMA SOUMARE DISTRIBUTION (ASD)",
    # URL vers le logo
    "site_logo": "images/logo.png",
    # Si le menu de navigation est fixé
    "fixed_sidebar_nav": True,
    # Thème du tableau de bord (parmi les thèmes de bootstrap)
    "theme": "united",
    # Masquer l'interface d'administration
    "hide_apps": [],
    "hide_models": [],
    # Liens personnalisés dans la barre de navigation
    "topmenu_links": [
        {"name": "Accueil", "url": "admin:index", "permissions": ["auth.view_user"]},
    ],
    # Menu de navigation latérale
    "icons": {
        "auth.User": "fas fa-user-circle",
        "auth.Group": "fas fa-users",
        # Ajoutez vos icônes ici
    },
}