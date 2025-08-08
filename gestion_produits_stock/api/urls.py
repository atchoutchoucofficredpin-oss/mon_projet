# C:\MON PROJET\gestion_produits_stock\api\urls.py

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'produits', views.ProduitViewSet)
router.register(r'lieux-stockage', views.LieuStockageViewSet)
router.register(r'stocks', views.StockViewSet)
router.register(r'clients', views.ClientViewSet)
router.register(r'factures', views.FactureViewSet)
router.register(r'lignes-facture', views.LigneFactureViewSet)
router.register(r'paiements', views.PaiementViewSet)
router.register(r'transferts-stock', views.TransfertStockViewSet)

urlpatterns = router.urls
