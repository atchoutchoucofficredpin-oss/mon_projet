# gestion_produits_stock/forms.py

from django import forms
from django.db.models import Sum
from django.forms import inlineformset_factory
from decimal import Decimal
from .models import (
    Client, Categorie, Fournisseur, Produit, LieuStockage,
    Stock, StockMovement, Facture, LigneFacture, Paiement
)

# Formulaire pour les Clients
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

# Formulaire pour les Catégories
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

# Formulaire pour les Fournisseurs
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

# Formulaire pour les Produits
class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'code_produit', 'description', 'prix_unitaire', 'categorie', 'fournisseur']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code_produit': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nom': 'Nom',
            'code_produit': 'Code Produit',
            'description': 'Description',
            'prix_unitaire': 'Prix Unitaire',
            'categorie': 'Catégorie',
            'fournisseur': 'Fournisseur',
        }


# Formulaire pour les Lieux de Stockage
class LieuStockageForm(forms.ModelForm):
    class Meta:
        model = LieuStockage
        fields = ['nom', 'adresse', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du lieu de stockage'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse du lieu de stockage'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du lieu de stockage'}),
        }
        labels = {
            'nom': 'Nom',
            'adresse': 'Adresse',
            'description': 'Description',
        }

# Formulaire pour les Stocks
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['produit', 'lieu_stockage', 'quantite']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'lieu_stockage': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'produit': 'Produit',
            'lieu_stockage': 'Lieu de Stockage',
            'quantite': 'Quantité',
        }

# Formulaire pour les Mouvements de Stock
class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['produit', 'lieu_stockage_source', 'lieu_stockage_destination', 'quantite', 'type_mouvement', 'description']
        widgets = {
            'date_mouvement': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# Formulaire pour les Factures
class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['client', 'date_facturation', 'notes'] # 'est_payee' et 'montant_total' sont calculés automatiquement
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control select2-client'}),
            'date_facturation': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes sur la facture'}),
        }
        labels = {
            'client': 'Client',
            'date_facturation': 'Date de facturation',
            'notes': 'Notes',
        }

# Formulaire pour les Lignes de Facture
class LigneFactureForm(forms.ModelForm):
    produit_nom = forms.CharField(
        label='Produit',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control product-search-input', 'placeholder': 'Rechercher un produit...'})
    )
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.all(),
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = LigneFacture
        fields = ['produit', 'quantite', 'prix_unitaire_negocie']
        widgets = {
            'quantite': forms.NumberInput(attrs={'class': 'form-control quantite-input', 'min': '0', 'step': 'any'}),
            'prix_unitaire_negocie': forms.NumberInput(attrs={'class': 'form-control prix-input', 'min': '0', 'step': 'any'}),
        }
        labels = {
            'produit': 'Produit', 
            'quantite': 'Quantité',
            'prix_unitaire_negocie': 'Prix Négocié',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        produit = cleaned_data.get('produit')
        quantite = cleaned_data.get('quantite')

        if produit and quantite and quantite > 0:
            stock = Stock.objects.filter(produit=produit).aggregate(total_quantite=Sum('quantite'))['total_quantite'] or Decimal('0.00')
            
            if self.instance and self.instance.pk:
                stock += self.instance.quantite

            if quantite > stock:
                self.add_error('quantite', f"Quantité insuffisante en stock. Disponible: {stock:.2f}")

        return cleaned_data

# Formset pour les Lignes de Facture
LigneFactureFormSet = inlineformset_factory(
    Facture, 
    LigneFacture, 
    form=LigneFactureForm, 
    extra=1, 
    can_delete=True,
    min_num=1,
    validate_min=True,
)

# Formulaire pour les Paiements
class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['montant_paye', 'date_paiement', 'methode_paiement', 'reference_paiement', 'notes']
        widgets = {
            'montant_paye': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date_paiement': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'methode_paiement': forms.Select(attrs={'class': 'form-control'}),
            'reference_paiement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Référence (ex: n° chèque, transaction ID)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes sur le paiement'}),
        }
        labels = {
            'montant_paye': 'Montant payé',
            'date_paiement': 'Date du paiement',
            'methode_paiement': 'Méthode de paiement',
            'reference_paiement': 'Référence du paiement',
            'notes': 'Notes',
        }