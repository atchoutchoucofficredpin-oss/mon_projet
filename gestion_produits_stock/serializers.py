# C:\MON PROJET\gestion_produits_stock\serializers.py

from rest_framework import serializers
from .models import (
    Produit, Stock, LieuStockage, StockMovement,
    Client, Facture, LigneFacture, Paiement,
)

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'

class LieuStockageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LieuStockage
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)
    lieu_stockage = LieuStockageSerializer(read_only=True)

    class Meta:
        model = Stock
        fields = '__all__'

class StockMovementSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)
    lieu_stockage = LieuStockageSerializer(read_only=True)
    produit_id = serializers.PrimaryKeyRelatedField(queryset=Produit.objects.all(), source='produit', write_only=True)
    lieu_stockage_id = serializers.PrimaryKeyRelatedField(queryset=LieuStockage.objects.all(), source='lieu_stockage', write_only=True)

    class Meta:
        model = StockMovement
        fields = '__all__'
        extra_kwargs = {
            'produit': {'required': False, 'read_only': True},
            'lieu_stockage': {'required': False, 'read_only': True}
        }

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class LigneFactureSerializer(serializers.ModelSerializer):
    produit_detail = ProduitSerializer(source='produit', read_only=True)
    produit = serializers.PrimaryKeyRelatedField(queryset=Produit.objects.all(), write_only=True)

    class Meta:
        model = LigneFacture
        fields = '__all__'
        read_only_fields = ['montant_total_ligne']

class FactureSerializer(serializers.ModelSerializer):
    lignes = LigneFactureSerializer(many=True, read_only=True)
    client_detail = ClientSerializer(source='client', read_only=True)
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), write_only=True)

    class Meta:
        model = Facture
        fields = '__all__'
        read_only_fields = ['montant_total']

class PaiementSerializer(serializers.ModelSerializer):
    facture_detail = FactureSerializer(source='facture', read_only=True)
    facture = serializers.PrimaryKeyRelatedField(queryset=Facture.objects.all(), write_only=True)

    class Meta:
        model = Paiement
        fields = '__all__'
