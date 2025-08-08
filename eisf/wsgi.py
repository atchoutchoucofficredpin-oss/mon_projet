# C:\MON PROJET\eisf\wsgi.py

import os

from django.core.wsgi import get_wsgi_application

# IMPORTANT : Le nom de votre module principal est 'eisf'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eisf.settings')

application = get_wsgi_application()
