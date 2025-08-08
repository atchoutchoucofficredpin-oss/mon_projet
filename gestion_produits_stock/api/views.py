# C:\MON PROJET\gestion_produits_stock\api\views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum

# Importation des modèles (celle-ci devrait être correcte maintenant)
from ..models import Produit, LieuStockage, Stock, Client, Facture, LigneFacture, Paiement, TransfertStock

# CORRECTION ICI : Importation des serializers.
# Ils se trouvent probablement dans le dossier parent (gestion_produits_stock/)
from ..serializers import ProduitSerializer, LieuStockageSerializer, StockSerializer, ClientSerializer, FactureSerializer, LigneFactureSerializer, PaiementSerializer, TransfertStockSerializer


# ViewSets pour vos modèles
class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

class LieuStockageViewSet(viewsets.ModelViewSet):
    queryset = LieuStockage.objects.all()
    serializer_class = LieuStockageSerializer

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    # Surcharge de la méthode 'create' pour gérer l'ajout/mise à jour du stock
    def create(self, request, *args, **kwargs):
        produit_id = request.data.get('produit')
        lieu_stockage_id = request.data.get('lieu_stockage')
        quantite_ajoutee = request.data.get('quantite')

        # Vérifications de base
        if not all([produit_id, lieu_stockage_id, quantite_ajoutee is not None]):
            return Response({"detail": "Produit, lieu de stockage et quantité sont requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            produit = Produit.objects.get(id=produit_id)
            lieu_stockage = LieuStockage.objects.get(id=lieu_stockage_id)
            quantite_ajoutee = int(quantite_ajoutee)
            if quantite_ajoutee <= 0:
                return Response({"detail": "La quantité à ajouter doit être supérieure à zéro."}, status=status.HTTP_400_BAD_REQUEST)
        except (Produit.DoesNotExist, LieuStockage.DoesNotExist):
            return Response({"detail": "Produit ou lieu de stockage introuvable."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"detail": "La quantité doit être un nombre entier valide."}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier si un stock pour ce produit et ce lieu existe déjà
        existing_stock = Stock.objects.filter(produit=produit, lieu_stockage=lieu_stockage).first()

        if existing_stock:
            # Si le stock existe, mettre à jour la quantité
            existing_stock.quantite += quantite_ajoutee
            existing_stock.save()
            serializer = self.get_serializer(existing_stock)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Si le stock n'existe pas, créer un nouvel enregistrement de stock
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def total_par_produit(self, request):
        produit_id = request.query_params.get('produit_id')
        if not produit_id:
            return Response({"detail": "Le paramètre 'produit_id' est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            produit = Produit.objects.get(id=produit_id)
        except Produit.DoesNotExist:
            return Response({"detail": "Produit introuvable."}, status=status.HTTP_404_NOT_FOUND)

        total_quantite = Stock.objects.filter(produit=produit).aggregate(Sum('quantite'))['quantite__sum'] or 0
        return Response({
            "produit_id": produit_id,
            "produit_nom": produit.nom,
            "total_quantite_globale": total_quantite
        }, status=status.HTTP_200_OK)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class FactureViewSet(viewsets.ModelViewSet):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer

class LigneFactureViewSet(viewsets.ModelViewSet):
    queryset = LigneFacture.objects.all()
    serializer_class = LigneFactureSerializer

class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer

class TransfertStockViewSet(viewsets.ModelViewSet):
    queryset = TransfertStock.objects.all()
    serializer_class = TransfertStockSerializer
