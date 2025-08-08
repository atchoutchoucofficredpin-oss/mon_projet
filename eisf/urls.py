# MONPROJET/urls.py (Votre fichier urls.py principal)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # C'est la page d'administration de Django, elle doit toujours être là
    path('admin/', admin.site.urls),

    # C'est la ligne la plus importante pour votre application !
    # Elle dit à Django : "Pour tout ce qui commence à la racine (chemin vide ''),
    # va voir les définitions d'URL dans le fichier 'gestion_produits_stock/urls.py'."
    path('', include('gestion_produits_stock.urls')),

    # Si vous aviez d'autres applications Django, leurs chemins seraient ajoutés ici, par exemple :
    # path('blog/', include('blog.urls')),
]

# Ces lignes sont pour servir les fichiers statiques et médias en mode développement.
# Elles ne sont actives que si DEBUG = True dans votre settings.py.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

