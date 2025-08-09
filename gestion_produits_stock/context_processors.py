# gestion_produits_stock/context_processors.py

from .models import Facture, Produit
from django.utils import timezone
from django.db.models import F

def alerts_processor(request):
    """
    Processeur de contexte pour ajouter les alertes de stock et de dettes.
    """
    if request.user.is_authenticated:
        dettes_impayees = Facture.objects.filter(
            est_payee=False,
            date_echeance__lt=timezone.now().date()
        ).select_related('client').order_by('date_echeance')

        produits_stock_faible = Produit.objects.filter(
            stock__quantite__lte=F('seuil_alerte')
        ).distinct()
        
        return {
            'dettes_impayees': dettes_impayees,
            'produits_stock_faible': produits_stock_faible,
        }
    return {}