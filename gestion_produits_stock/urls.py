# gestion_produits_stock/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Page d'accueil/Tableau de bord
    path('', views.home, name='home'),
    
    # URL pour le rapport de bénéfice journalier (NOUVEAU)
    path('inventaire/benefice-journee/', views.inventaire_benefice_journee, name='inventaire_benefice_journee'),
    
    # URLS pour les clients
    path('clients/', views.liste_clients, name='liste_clients'),
    path('clients/ajouter/', views.ajouter_client, name='ajouter_client'),
    path('clients/modifier/<int:pk>/', views.modifier_client, name='modifier_client'),
    path('clients/supprimer/<int:pk>/', views.supprimer_client, name='supprimer_client'),
    path('clients/<int:pk>/historique/', views.historique_client, name='historique_client'),
    path('clients/banque-caisse/<int:pk>/', views.banque_caisse_client, name='banque_caisse_client'),

    # URLS pour les catégories
    path('categories/', views.liste_categories, name='liste_categories'),
    path('categories/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),
    path('categories/modifier/<int:pk>/', views.modifier_categorie, name='modifier_categorie'),
    path('categories/supprimer/<int:pk>/', views.supprimer_categorie, name='supprimer_categorie'),

    # URLS pour les fournisseurs
    path('fournisseurs/', views.liste_fournisseurs, name='liste_fournisseurs'),
    path('fournisseurs/ajouter/', views.ajouter_fournisseur, name='ajouter_fournisseur'),
    path('fournisseurs/modifier/<int:pk>/', views.modifier_fournisseur, name='modifier_fournisseur'),
    path('fournisseurs/supprimer/<int:pk>/', views.supprimer_fournisseur, name='supprimer_fournisseur'),

    # URLS pour les produits
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produits/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produits/modifier/<int:pk>/', views.modifier_produit, name='modifier_produit'),
    path('produits/supprimer/<int:pk>/', views.supprimer_produit, name='supprimer_produit'),

    # URLS pour les lieux de stockage
    path('lieux-stockage/', views.liste_lieux_stockage, name='liste_lieux_stockage'),
    path('lieux-stockage/ajouter/', views.ajouter_lieu_stockage, name='ajouter_lieu_stockage'),
    path('lieux-stockage/modifier/<int:pk>/', views.modifier_lieu_stockage, name='modifier_lieu_stockage'),
    path('lieux-stockage/supprimer/<int:pk>/', views.supprimer_lieu_stockage, name='supprimer_lieu_stockage'),

    # URLS pour la gestion des stocks
    path('stocks/', views.liste_stocks, name='liste_stocks'),
    path('stocks/entree/', views.entree_stock, name='entree_stock'),
    path('stocks/mouvements/', views.liste_mouvements_stock, name='liste_mouvements_stock'),
    path('stocks/<int:pk>/', views.detail_stock, name='detail_stock'),

    # URLS pour les factures et les paiements
    path('factures/', views.liste_factures, name='liste_factures'),
    path('factures/detail/<int:pk>/', views.detail_facture, name='detail_facture'),
    path('factures/generer-pdf/<int:pk>/', views.generer_facture_pdf, name='generer_facture_pdf'),
    path('factures/<int:facture_pk>/ajouter_paiement/', views.ajouter_paiement, name='ajouter_paiement'),

    # URLs pour l'interface de vente
    path('deconnexion-vente/', views.deconnexion_vente, name='deconnexion_vente'),
    path('vente/', views.interface_vente, name='interface_vente'),
    path('vente/modifier/<int:pk>/', views.modifier_vente, name='modifier_vente'),

    # URLs pour l'API (recherche AJAX)
    path('recherche-produit-ajax/', views.recherche_produit_ajax, name='recherche_produit_ajax'),
    path('get-product-stock-ajax/', views.get_product_stock_ajax, name='get_product_stock_ajax'),
]