# gestion_produits_stock/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal # Ajout de l'import pour la valeur par défaut

from .models import (
    Client, Categorie, Fournisseur, LieuStockage, Produit,
    Stock, StockMovement, Facture, LigneFacture, Paiement
)


# =====================================================================
# Configuration personnalisée pour le modèle Client
# =====================================================================
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'telephone', 'actions_banque_caisse')
    search_fields = ('nom', 'email', 'telephone')

    def actions_banque_caisse(self, obj):
        """ Crée un lien pour accéder à la page Banque & Caisse """
        return format_html(
            '<a class="button" href="{}">Banque & Caisse</a>',
            f'/clients/banque-caisse/{obj.pk}/'
        )
    actions_banque_caisse.short_description = 'Actions'
    actions_banque_caisse.allow_tags = True


# =====================================================================
# Configuration personnalisée pour le modèle Produit
# =====================================================================
@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code_produit', 'prix_unitaire', 'get_stock_total', 'categorie', 'fournisseur')
    search_fields = ('nom', 'code_produit')
    list_filter = ('categorie', 'fournisseur')
    
    # On utilise cette méthode pour afficher le stock total calculé par l'annotation
    def get_stock_total(self, obj):
        # La valeur 'stock_total' est ajoutée à chaque objet 'Produit' par get_queryset
        return obj.stock_total
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # On annote le queryset pour calculer le stock total de chaque produit
        queryset = queryset.annotate(
            # Coalesce s'assure que la valeur est 0.00 si aucun stock n'est trouvé
            stock_total=Coalesce(Sum('stocks__quantite'), Decimal('0.00'), output_field=DecimalField())
        )
        return queryset
    
    get_stock_total.short_description = 'Stock Total'


# =====================================================================
# Enregistrement des autres modèles
# =====================================================================
admin.site.register(Categorie)
admin.site.register(Fournisseur)
admin.site.register(LieuStockage)
admin.site.register(Stock)
admin.site.register(StockMovement)
admin.site.register(Facture)
admin.site.register(LigneFacture)
admin.site.register(Paiement)