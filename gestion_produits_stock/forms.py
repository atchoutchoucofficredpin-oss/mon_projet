# gestion_produits_stock/forms.py

from django import forms
from django.db.models import Sum
from django.forms import inlineformset_factory
from decimal import Decimal
from .models import (
    Client, Categorie, Fournisseur, Produit, LieuStockage,
    Stock, StockMovement, Facture, LigneFacture, Paiement
)
from django.utils import timezone
from django.forms.widgets import DateInput


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'adresse', 'telephone', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du client'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse du client'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone du client'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email du client'}),
        }
        labels = {
            'nom': 'Nom',
            'adresse': 'Adresse',
            'telephone': 'Téléphone',
            'email': 'Email',
        }


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la catégorie'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description de la catégorie'}),
        }
        labels = {
            'nom': 'Nom',
            'description': 'Description',
        }


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'contact', 'telephone', 'email', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du fournisseur'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du contact'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone du fournisseur'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email du fournisseur'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse du fournisseur'}),
        }
        labels = {
            'nom': 'Nom',
            'contact': 'Contact',
            'telephone': 'Téléphone',
            'email': 'Email',
            'adresse': 'Adresse',
        }


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'code_produit', 'categorie', 'fournisseur', 'prix_unitaire', 'prix_achat', 'seuil_alerte', 'description'] # AJOUT de 'prix_achat' et 'seuil_alerte'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'code_produit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code du produit'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), # NOUVEAU
            'seuil_alerte': forms.NumberInput(attrs={'class': 'form-control'}), # NOUVEAU
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nom': 'Nom',
            'code_produit': 'Code Produit',
            'categorie': 'Catégorie',
            'fournisseur': 'Fournisseur',
            'prix_unitaire': 'Prix de Vente',
            'prix_achat': "Prix d'Achat", # NOUVEAU
            'seuil_alerte': "Seuil d'Alerte", # NOUVEAU
            'description': 'Description',
        }


class LieuStockageForm(forms.ModelForm):
    class Meta:
        model = LieuStockage
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du lieu de stockage'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du lieu'}),
        }
        labels = {
            'nom': 'Nom',
            'description': 'Description',
        }


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['produit', 'lieu_stockage', 'quantite']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'lieu_stockage': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'produit': 'Produit',
            'lieu_stockage': 'Lieu de Stockage',
            'quantite': 'Quantité',
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['produit', 'quantite', 'type_mouvement', 'lieu_stockage_source', 'lieu_stockage_destination', 'description']


class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['client', 'date_echeance'] # AJOUT de 'date_echeance'
        widgets = {
            'date_echeance': DateInput(attrs={'type': 'date', 'class': 'form-control'}), # NOUVEAU
            'client': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['date_echeance'].initial = timezone.now().date() + timezone.timedelta(days=30)
            
            
class LigneFactureForm(forms.ModelForm):
    class Meta:
        model = LigneFacture
        fields = ['produit', 'quantite', 'prix_unitaire_negocie']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control produit-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control quantite-input', 'min': '0', 'step': '0.01'}),
            'prix_unitaire_negocie': forms.NumberInput(attrs={'class': 'form-control prix-input', 'min': '0', 'step': '0.01'}),
        }


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['montant_paye', 'methode_paiement']
        widgets = {
            'montant_paye': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'methode_paiement': forms.Select(attrs={'class': 'form-control'}),
        }