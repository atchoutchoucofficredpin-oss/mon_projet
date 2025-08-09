# gestion_produits_stock/models.py

from django.db import models
from django.db.models import Sum
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce # NOUVEAU

# Modèle pour les Catégories de produits
class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la Catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")
    
    class Meta:
        verbose_name_plural = "Catégories"
        ordering = ['nom']

    def __str__(self):
        return self.nom

# Modèle pour les Fournisseurs
class Fournisseur(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom du Fournisseur")
    contact = models.CharField(max_length=255, blank=True, null=True, verbose_name="Contact")
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    adresse = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nom']

# Modèle pour les Produits
class Produit(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom du Produit")
    code_produit = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Code Produit (ex: SKU)")
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Prix d'Achat Unitaire")
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Prix de Vente Unitaire")
    seuil_alerte = models.IntegerField(default=10, verbose_name="Seuil d'alerte", help_text="Quantité minimale avant qu'une alerte soit déclenchée.") # NOUVEAU
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")
    
    def __str__(self):
        return self.nom
    
    def get_stock_total(self):
        return self.stock_set.aggregate(
            total_quantite=Coalesce(models.Sum('quantite'), Decimal('0.00'))
        )['total_quantite']
    
    def get_stock_principal(self):
        try:
            return self.stock_set.get(lieu_stockage__nom="Principal").quantite
        except Stock.DoesNotExist:
            return Decimal('0.00')

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['nom']

# Modèle pour les Clients
class Client(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom du Client")
    adresse = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse")
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['nom']
        
# Modèle pour les Lieux de Stockage
class LieuStockage(models.Model):
    nom = models.CharField(max_length=200, unique=True, verbose_name="Nom du Lieu")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")
    
    class Meta:
        verbose_name = "Lieu de Stockage"
        verbose_name_plural = "Lieux de Stockage"

    def __str__(self):
        return self.nom
        
# Modèle pour le Stock
class Stock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    lieu_stockage = models.ForeignKey(LieuStockage, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        unique_together = ('produit', 'lieu_stockage')
        verbose_name = "Stock par Lieu"
        verbose_name_plural = "Stocks par Lieux"

    def __str__(self):
        return f"{self.produit.nom} ({self.quantite}) dans {self.lieu_stockage.nom}"

# Modèle pour les Mouvements de Stock
class StockMovement(models.Model):
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
        ('TRANSFERT', 'Transfert'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date_mouvement = models.DateTimeField(auto_now_add=True)
    lieu_stockage_source = models.ForeignKey(
        LieuStockage, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='mouvements_sortants'
    )
    lieu_stockage_destination = models.ForeignKey(
        LieuStockage, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='mouvements_entrants'
    )
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Mouvements de Stock"

    def __str__(self):
        return f"{self.type_mouvement} de {self.produit.nom} - {self.quantite}"

# Modèle pour les Factures
class Facture(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_facturation = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    est_payee = models.BooleanField(default=False)
    date_echeance = models.DateField(default=timezone.now, help_text="Date limite de paiement de la facture.") # NOUVEAU

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def __str__(self):
        return f"Facture #{self.id} pour {self.client.nom}"

    def get_solde_restant(self):
        total_paye = self.paiement_set.aggregate(
            total_paye=Coalesce(Sum('montant_paye'), Decimal('0.00'))
        )['total_paye']
        return self.montant_total - total_paye

    def clean(self):
        if self.get_solde_restant() < Decimal('0.00'):
            raise ValidationError("Le solde restant ne peut pas être négatif.")

# Modèle pour les Lignes de Facture
class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes_facture')
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    prix_unitaire_negocie = models.DecimalField(max_digits=10, decimal_places=2)
    total_ligne = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite} sur Facture #{self.facture.id}"

# Modèle pour les Paiements reçus
class Paiement(models.Model):
    METHODE_PAIEMENT_CHOICES = [
        ('ESPECES', 'Espèces'),
        ('VIREMENT', 'Virement bancaire'),
        ('CHEQUE', 'Chèque'),
        ('MOBILE_MONEY', 'Mobile Money'),
    ]
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    methode_paiement = models.CharField(max_length=20, choices=METHODE_PAIEMENT_CHOICES, default='ESPECES')

    def __str__(self):
        return f"Paiement de {self.montant_paye} pour la Facture #{self.facture.id}"