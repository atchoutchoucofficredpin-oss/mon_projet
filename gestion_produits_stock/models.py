# gestion_produits_stock/models.py

from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError

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

# Modèle : Catégorie (AJOUTÉ)
class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la Catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['nom']

# Modèle : Fournisseur (AJOUTÉ)
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
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # --- CHAMPS AJOUTÉS ---
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Prix d'achat")
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Prix de vente")
    # ----------------------
    
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix Unitaire")
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits', verbose_name="Catégorie")
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits_fournis', verbose_name="Fournisseur")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['nom']

# Modèle : LieuStockage (AJOUTÉ)
class LieuStockage(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom du Lieu de Stockage")
    adresse = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Lieu de Stockage"
        verbose_name_plural = "Lieux de Stockage"
        ordering = ['nom']

# Modèle : Stock (AJOUTÉ)
class Stock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='stocks', verbose_name="Produit")
    lieu_stockage = models.ForeignKey(LieuStockage, on_delete=models.CASCADE, related_name='stocks', verbose_name="Lieu de Stockage")
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Quantité en Stock")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")

    def __str__(self):
        return f"{self.produit.nom} ({self.quantite}) à {self.lieu_stockage.nom}"

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        unique_together = ('produit', 'lieu_stockage')
        ordering = ['produit', 'lieu_stockage']

# Modèle : StockMovement (AJOUTÉ)
class StockMovement(models.Model):
    TYPES_MOUVEMENT = [
        ('ENTREE_ACHAT', 'Entrée (Achat)'),
        ('SORTIE_VENTE', 'Sortie (Vente)'),
        ('TRANSFERT', 'Transfert'),
        ('AJUSTEMENT_POSITIF', 'Ajustement Positif'),
        ('AJUSTEMENT_NEGATIF', 'Ajustement Négatif'),
        ('RETOUR_FOURNISSEUR', 'Retour Fournisseur'),
        ('RETOUR_CLIENT', 'Retour Client'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, verbose_name="Produit")
    lieu_stockage_source = models.ForeignKey(LieuStockage, on_delete=models.SET_NULL, null=True, blank=True, related_name='mouvements_source', verbose_name="Lieu Source")
    lieu_stockage_destination = models.ForeignKey(LieuStockage, on_delete=models.SET_NULL, null=True, blank=True, related_name='mouvements_destination', verbose_name="Lieu Destination")
    quantite = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité")
    type_mouvement = models.CharField(max_length=50, choices=TYPES_MOUVEMENT, verbose_name="Type de Mouvement")
    date_mouvement = models.DateTimeField(default=timezone.now, verbose_name="Date du Mouvement")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    facture = models.ForeignKey('Facture', on_delete=models.SET_NULL, null=True, blank=True, related_name='mouvements_stock', verbose_name="Facture Liée")

    def __str__(self):
        return f"Mouvement de {self.quantite} de {self.produit.nom} ({self.type_mouvement})"

    class Meta:
        verbose_name = "Mouvement de Stock"
        verbose_name_plural = "Mouvements de Stock"
        ordering = ['-date_mouvement', 'produit']

# Modèle : Facture (AJOUTÉ)
class Facture(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='factures', verbose_name="Client")
    date_facturation = models.DateTimeField(default=timezone.now, verbose_name="Date de Facturation")
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Montant Total")
    est_payee = models.BooleanField(default=False, verbose_name="Est Payée")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")

    def __str__(self):
        return f"Facture #{self.pk} - {self.client.nom if self.client else 'N/A'} - {self.date_facturation.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date_facturation']

# Modèle : LigneFacture (AJOUTÉ)
class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes_facture', verbose_name="Facture")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, verbose_name="Produit")
    quantite = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité")
    prix_unitaire_negocie = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix Unitaire Négocié")
    total_ligne = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Total Ligne")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")

    def __str__(self):
        return f"Ligne Facture #{self.facture.pk} - {self.produit.nom} ({self.quantite}x)"

    class Meta:
        verbose_name = "Ligne de Facture"
        verbose_name_plural = "Lignes de Facture"
        ordering = ['facture', 'produit']

# Modèle : Paiement (AJOUTÉ)
class Paiement(models.Model):
    METHODES_PAIEMENT = [
        ('ESPECES', 'Espèces'),
        ('CARTE_BANCAIRE', 'Carte Bancaire'),
        ('VIREMENT', 'Virement Bancaire'),
        ('CHEQUE', 'Chèque'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('AUTRE', 'Autre'),
    ]

    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='paiements', verbose_name="Facture")
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant Payé")
    date_paiement = models.DateTimeField(default=timezone.now, verbose_name="Date du Paiement")
    methode_paiement = models.CharField(max_length=50, choices=METHODES_PAIEMENT, verbose_name="Méthode de Paiement")
    reference_paiement = models.CharField(max_length=100, blank=True, null=True, verbose_name="Référence du Paiement")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Mise à Jour")

    def __str__(self):
        return f"Paiement de {self.montant_paye} pour Facture #{self.facture.pk}"

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']