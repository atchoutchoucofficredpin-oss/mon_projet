# C:\MON PROJET\interface_vente\urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('vendre/', views.creer_vente, name='creer_vente'),
    path('facture/<int:facture_id>/', views.detail_facture, name='detail_facture'),
]
