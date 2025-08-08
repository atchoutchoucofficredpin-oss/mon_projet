# gestion_produits_stock/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Q, F
from django.db.models.functions import Coalesce

import traceback

from .models import (
    Facture, LigneFacture, Produit, Client, StockMovement,
    Stock, LieuStockage, Paiement, Categorie, Fournisseur
)
from .forms import (
    FactureForm, LigneFactureForm, ProduitForm, ClientForm,
    LieuStockageForm, StockForm, StockMovementForm, CategorieForm,
    FournisseurForm, PaiementForm
)

LigneFactureFormSet = inlineformset_factory(
    Facture, LigneFacture, form=LigneFactureForm, extra=1, can_delete=True
)


# --- Vue d'accueil (Home) ---
def home(request):
    """
    Vue pour la page d'accueil de l'application.
    """
    return render(request, 'gestion_produits_stock/home.html')


# --- Vues pour les Clients ---
def liste_clients(request):
    clients = Client.objects.all()
    return render(request, 'gestion_produits_stock/liste_clients.html', {'clients': clients})

def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Client ajouté avec succès!")
            return redirect('liste_clients')
    else:
        form = ClientForm()
    return render(request, 'gestion_produits_stock/ajouter_client.html', {'form': form})

def modifier_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client modifié avec succès!")
            return redirect('liste_clients')
    else:
        form = ClientForm(instance=client)
    return render(request, 'gestion_produits_stock/modifier_client.html', {'form': form, 'client': client})

def supprimer_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, "Client supprimé avec succès!")
        return redirect('liste_clients')
    return render(request, 'gestion_produits_stock/confirmer_suppression.html', {'objet': client, 'type': 'Client'})

def historique_client(request, pk):
    """
    Vue pour afficher l'historique des factures d'un client.
    """
    client = get_object_or_404(Client, pk=pk)
    factures = Facture.objects.filter(client=client).order_by('-date_facturation')
    
    context = {
        'client': client,
        'factures': factures,
    }
    return render(request, 'gestion_produits_stock/historique_client.html', context)

def banque_caisse_client(request, pk):
    """
    Vue pour l'interface "Banque et Caisse" d'un client.
    Affiche les factures, le solde et l'historique des paiements.
    Permet de faire un paiement partiel.
    """
    client = get_object_or_404(Client, pk=pk)
    factures = Facture.objects.filter(client=client).order_by('-date_facturation')
    
    # Calcul du montant total dû et du solde total
    total_factures = factures.aggregate(
        total_du=Coalesce(Sum('montant_total'), Decimal('0.00'))
    )['total_du']

    total_paiements = Paiement.objects.filter(
        facture__client=client
    ).aggregate(
        total_paye=Coalesce(Sum('montant_paye'), Decimal('0.00'))
    )['total_paye']
    
    solde_total = total_factures - total_paiements

    # Préparation des factures avec leur solde individuel
    factures_avec_solde = []
    for facture in factures:
        total_paye_facture = Paiement.objects.filter(
            facture=facture
        ).aggregate(
            total_paye=Coalesce(Sum('montant_paye'), Decimal('0.00'))
        )['total_paye']
        facture.solde_restant = facture.montant_total - total_paye_facture
        factures_avec_solde.append(facture)

    # Historique des paiements du client
    historique_paiements = Paiement.objects.filter(
        facture__client=client
    ).order_by('-date_paiement')
    
    # Gérer le formulaire de paiement
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            montant_paye = form.cleaned_data['montant_paye']
            methode_paiement = form.cleaned_data['methode_paiement']
            
            # Vérifier si le paiement est supérieur au solde total
            if montant_paye > solde_total:
                messages.error(request, f"Le montant du paiement ({montant_paye} FCFA) dépasse le solde total dû ({solde_total} FCFA).")
            else:
                # Appliquer le paiement aux factures non payées les plus anciennes
                montant_restant_a_imputer = montant_paye
                factures_non_payees = Facture.objects.filter(
                    client=client, est_payee=False
                ).order_by('date_facturation')

                for facture_a_payer in factures_non_payees:
                    total_paye_facture = Paiement.objects.filter(
                        facture=facture_a_payer
                    ).aggregate(
                        total_paye=Coalesce(Sum('montant_paye'), Decimal('0.00'))
                    )['total_paye']
                    
                    solde_facture = facture_a_payer.montant_total - total_paye_facture
                    
                    if montant_restant_a_imputer > Decimal('0.00'):
                        montant_impute = min(montant_restant_a_imputer, solde_facture)
                        
                        # Créer le paiement
                        Paiement.objects.create(
                            facture=facture_a_payer,
                            montant_paye=montant_impute,
                            methode_paiement=methode_paiement
                        )
                        
                        montant_restant_a_imputer -= montant_impute
                        
                        # Mettre à jour le statut de la facture si elle est entièrement payée
                        if solde_facture - montant_impute <= Decimal('0.00'):
                            facture_a_payer.est_payee = True
                            facture_a_payer.save()

                messages.success(request, f"Paiement de {montant_paye} FCFA enregistré avec succès.")
            
            return redirect('banque_caisse_client', pk=client.pk)
    else:
        form = PaiementForm()

    context = {
        'client': client,
        'factures': factures_avec_solde,
        'total_factures': total_factures,
        'total_paiements': total_paiements,
        'solde_total': solde_total,
        'historique_paiements': historique_paiements,
        'form': form,
    }
    return render(request, 'gestion_produits_stock/banque_caisse_client.html', context)


# --- Vues pour les Catégories ---
def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'gestion_produits_stock/liste_categories.html', {'categories': categories})

def ajouter_categorie(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée avec succès!")
            return redirect('liste_categories')
    else:
        form = CategorieForm()
    return render(request, 'gestion_produits_stock/ajouter_categorie.html', {'form': form})

def modifier_categorie(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie modifiée avec succès!")
            return redirect('liste_categories')
    else:
        form = CategorieForm(instance=categorie)
    return render(request, 'gestion_produits_stock/modifier_categorie.html', {'form': form, 'categorie': categorie})

def supprimer_categorie(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        categorie.delete()
        messages.success(request, "Catégorie supprimée avec succès!")
        return redirect('liste_categories')
    return render(request, 'gestion_produits_stock/confirmer_suppression.html', {'objet': categorie, 'type': 'Catégorie'})


# --- Vues pour les Fournisseurs ---
def liste_fournisseurs(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'gestion_produits_stock/liste_fournisseurs.html', {'fournisseurs': fournisseurs})

def ajouter_fournisseur(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur ajouté avec succès!")
            return redirect('liste_fournisseurs')
    else:
        form = FournisseurForm()
    return render(request, 'gestion_produits_stock/ajouter_fournisseur.html', {'form': form})

def modifier_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur modifié avec succès!")
            return redirect('liste_fournisseurs')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'gestion_produits_stock/modifier_fournisseur.html', {'form': form, 'fournisseur': fournisseur})

def supprimer_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        messages.success(request, "Fournisseur supprimé avec succès!")
        return redirect('liste_fournisseurs')
    return render(request, 'gestion_produits_stock/confirmer_suppression.html', {'objet': fournisseur, 'type': 'Fournisseur'})


# --- Vues pour les Produits ---
def liste_produits(request):
    produits = Produit.objects.all()
    return render(request, 'gestion_produits_stock/liste_produits.html', {'produits': produits})

def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit ajouté avec succès!")
            return redirect('liste_produits')
    else:
        form = ProduitForm()
    return render(request, 'gestion_produits_stock/ajouter_produit.html', {'form': form})

def modifier_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès!")
            return redirect('liste_produits')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'gestion_produits_stock/modifier_produit.html', {'form': form, 'produit': produit})

def supprimer_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        messages.success(request, "Produit supprimé avec succès!")
        return redirect('liste_produits')
    return render(request, 'gestion_produits_stock/confirmer_suppression.html', {'objet': produit, 'type': 'Produit'})


# --- Vues pour les Lieux de Stockage ---
def liste_lieux_stockage(request):
    lieux_stockage = LieuStockage.objects.all()
    return render(request, 'gestion_produits_stock/liste_lieux_stockage.html', {'lieux_stockage': lieux_stockage})

def ajouter_lieu_stockage(request):
    if request.method == 'POST':
        form = LieuStockageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lieu de stockage ajouté avec succès!")
            return redirect('liste_lieux_stockage')
    else:
        form = LieuStockageForm()
    return render(request, 'gestion_produits_stock/ajouter_lieu_stockage.html', {'form': form})

def modifier_lieu_stockage(request, pk):
    lieu_stockage = get_object_or_404(LieuStockage, pk=pk)
    if request.method == 'POST':
        form = LieuStockageForm(request.POST, instance=lieu_stockage)
        if form.is_valid():
            form.save()
            messages.success(request, "Lieu de stockage modifié avec succès!")
            return redirect('liste_lieux_stockage')
    else:
        form = LieuStockageForm(instance=lieu_stockage)
    return render(request, 'gestion_produits_stock/modifier_lieu_stockage.html', {'form': form, 'lieu_stockage': lieu_stockage})

def supprimer_lieu_stockage(request, pk):
    lieu_stockage = get_object_or_404(LieuStockage, pk=pk)
    if request.method == 'POST':
        lieu_stockage.delete()
        messages.success(request, "Lieu de stockage supprimé avec succès!")
        return redirect('liste_lieux_stockage')
    return render(request, 'gestion_produits_stock/confirmer_suppression.html', {'objet': lieu_stockage, 'type': 'Lieu de Stockage'})


# --- Vues pour les Stocks ---
def liste_stocks(request):
    stocks = Stock.objects.all()
    return render(request, 'gestion_produits_stock/liste_stocks.html', {'stocks': stocks})

def detail_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    return render(request, 'gestion_produits_stock/detail_stock.html', {'stock': stock})

def entree_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            
            # Créer un mouvement de stock
            StockMovement.objects.create(
                produit=stock.produit,
                lieu_stockage_destination=stock.lieu_stockage,
                quantite=stock.quantite,
                type_mouvement='ENTREE',
                description=f"Entrée de stock via le formulaire."
            )
            
            # Mettre à jour le stock existant ou en créer un nouveau
            existing_stock, created = Stock.objects.get_or_create(
                produit=stock.produit, 
                lieu_stockage=stock.lieu_stockage,
                defaults={'quantite': 0}
            )
            existing_stock.quantite += stock.quantite
            existing_stock.save()

            messages.success(request, "Entrée de stock enregistrée avec succès.")
            return redirect('liste_stocks')
    else:
        form = StockForm()
    return render(request, 'gestion_produits_stock/entree_stock.html', {'form': form})

def liste_mouvements_stock(request):
    mouvements = StockMovement.objects.all().order_by('-date_mouvement')
    return render(request, 'gestion_produits_stock/liste_mouvements_stock.html', {'mouvements': mouvements})


# --- Vues pour les Factures et Paiements ---
def liste_factures(request):
    client_id = request.GET.get('client')
    if client_id:
        factures = Facture.objects.filter(client__id=client_id).order_by('-date_facturation')
        client_selectionne = get_object_or_404(Client, pk=client_id)
    else:
        factures = Facture.objects.all().order_by('-date_facturation')
        client_selectionne = None
        
    clients = Client.objects.all().order_by('nom')
    
    context = {
        'factures': factures,
        'clients': clients,
        'client_selectionne': client_selectionne,
    }
    return render(request, 'gestion_produits_stock/liste_factures.html', context)


def detail_facture(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    lignes_facture = LigneFacture.objects.filter(facture=facture)
    paiements = Paiement.objects.filter(facture=facture).order_by('date_paiement')

    total_paye = paiements.aggregate(Sum('montant_paye'))['montant_paye__sum'] or Decimal('0.00')
    solde_du = facture.montant_total - total_paye
    
    context = {
        'facture': facture,
        'lignes_facture': lignes_facture,
        'paiements': paiements,
        'solde_du': solde_du,
    }
    return render(request, 'gestion_produits_stock/detail_facture.html', context)

def generer_facture_pdf(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    lignes_facture = LigneFacture.objects.filter(facture=facture)
    paiements = Paiement.objects.filter(facture=facture)

    # Calcul du total payé et du solde dû
    total_paye = sum(p.montant_paye for p in paiements)
    solde_du = facture.montant_total - total_paye
    
    # Création du document PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Style personnalisé pour l'en-tête
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        alignment=1 # Centre
    )

    # En-tête du document
    story.append(Paragraph(f"Facture # {facture.id}", header_style))
    story.append(Paragraph(f"Date: {facture.date_facturation.strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # Informations client
    story.append(Paragraph(f"Client: {facture.client.nom}", styles['Normal']))
    story.append(Paragraph(f"Adresse: {facture.client.adresse or 'N/A'}", styles['Normal']))
    story.append(Paragraph(f"Téléphone: {facture.client.telephone or 'N/A'}", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Tableau des produits
    data = [['Produit', 'Quantité', 'Prix Unitaire', 'Total']]
    for ligne in lignes_facture:
        # Correction ici : Utilisation de 'total_ligne' au lieu de 'total'
        data.append([
            ligne.produit.nom,
            str(ligne.quantite),
            f"{ligne.prix_unitaire_negocie} FCFA",
            f"{ligne.total_ligne} FCFA"
        ])

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ])

    # Ajouter le total à la table
    data.append(['', '', 'Montant Total:', f"{facture.montant_total} FCFA"])
    table_style.add('SPAN', (0, -1), (1, -1))
    table_style.add('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold')

    table = Table(data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
    table.setStyle(table_style)
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # Paiements
    story.append(Paragraph("<b>Historique des paiements :</b>", styles['Normal']))
    for paiement in paiements:
        story.append(Paragraph(
            f"- {paiement.date_paiement.strftime('%d/%m/%Y')} : {paiement.montant_paye} FCFA ({paiement.get_methode_paiement_display()})",
            styles['Normal']
        ))
    
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"<b>Total Payé :</b> {total_paye} FCFA", styles['Normal']))
    story.append(Paragraph(f"<b>Solde Dû :</b> {solde_du} FCFA", styles['Normal']))
    
    # Génération du PDF
    doc.build(story)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{facture.id}.pdf"'
    response.write(pdf)
    return response

def ajouter_paiement(request, facture_pk):
    facture = get_object_or_404(Facture, pk=facture_pk)
    
    total_paye = Paiement.objects.filter(facture=facture).aggregate(Sum('montant_paye'))['montant_paye__sum'] or Decimal('0.00')
    solde_restant = facture.montant_total - total_paye

    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            nouveau_paiement = form.save(commit=False)
            nouveau_paiement.facture = facture
            
            # Validation pour s'assurer que le paiement ne dépasse pas le solde
            if nouveau_paiement.montant_paye > solde_restant:
                messages.error(request, f"Le montant du paiement ({nouveau_paiement.montant_paye} FCFA) dépasse le solde restant ({solde_restant} FCFA).")
            else:
                nouveau_paiement.save()
                messages.success(request, "Paiement enregistré avec succès!")
                
                # Mise à jour du statut de la facture
                total_paye_apres = Paiement.objects.filter(facture=facture).aggregate(Sum('montant_paye'))['montant_paye__sum'] or Decimal('0.00')
                if total_paye_apres >= facture.montant_total:
                    facture.est_payee = True
                    facture.save()
                    
                return redirect('detail_facture', pk=facture.pk)
    else:
        form = PaiementForm()

    context = {
        'form': form,
        'facture': facture,
        'solde_restant': solde_restant,
    }
    return render(request, 'gestion_produits_stock/ajouter_paiement.html', context)


# --- Vues pour l'interface de vente ---
def interface_vente(request):
    if request.method == 'POST':
        facture_form = FactureForm(request.POST, prefix='facture')
        formset = LigneFactureFormSet(request.POST, prefix='lignes')

        try:
            with transaction.atomic():
                if facture_form.is_valid() and formset.is_valid():
                    facture = facture_form.save(commit=False)
                    
                    # Calculer le montant total de la facture
                    total_facture = Decimal('0.00')
                    
                    # Vérifier le stock avant de sauvegarder
                    for form in formset:
                        if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                            produit = form.cleaned_data.get('produit')
                            quantite = form.cleaned_data.get('quantite')
                            prix_unitaire_negocie = form.cleaned_data.get('prix_unitaire_negocie')
                            
                            stock_principal = Stock.objects.filter(produit=produit, lieu_stockage__nom="Principal").first()
                            
                            if not stock_principal or stock_principal.quantite < quantite:
                                messages.error(request, f"Quantité insuffisante pour le produit {produit.nom}. Stock disponible : {stock_principal.quantite if stock_principal else 0}.")
                                raise ValidationError("Stock insuffisant.")
                            
                            # Calculer le total de la ligne ici
                            total_ligne = quantite * prix_unitaire_negocie
                            total_facture += total_ligne
                    
                    facture.montant_total = total_facture
                    facture.save()
                    
                    for form in formset:
                        if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                            ligne_facture = form.save(commit=False)
                            ligne_facture.facture = facture
                            
                            # Mettre à jour le total_ligne avant de sauvegarder
                            ligne_facture.total_ligne = ligne_facture.quantite * ligne_facture.prix_unitaire_negocie
                            ligne_facture.save()
                            
                            # Décrémenter le stock
                            stock_principal = Stock.objects.get(produit=ligne_facture.produit, lieu_stockage__nom="Principal")
                            stock_principal.quantite -= ligne_facture.quantite
                            stock_principal.save()
                            
                            # Créer un mouvement de stock de sortie
                            StockMovement.objects.create(
                                produit=ligne_facture.produit,
                                lieu_stockage_source=stock_principal.lieu_stockage,
                                quantite=ligne_facture.quantite,
                                type_mouvement='SORTIE',
                                description=f"Vente (Facture #{facture.id})"
                            )

                    messages.success(request, "Facture enregistrée avec succès!")
                    return redirect('detail_facture', pk=facture.pk)
                else:
                    messages.error(request, "Erreur dans le formulaire. Veuillez vérifier les informations.")
                    # Log des erreurs du formulaire et du formset pour le débogage
                    print("Erreurs FactureForm:", facture_form.errors)
                    print("Erreurs Formset:", formset.errors)
        except ValidationError as e:
            # L'erreur de stock est déjà gérée par les messages
            print(f"Validation Error: {e}")
        except Exception as e:
            messages.error(request, "Une erreur inattendue est survenue lors de l'enregistrement de la facture.")
            traceback.print_exc()

    else:
        facture_form = FactureForm(prefix='facture', initial={'date_facturation': timezone.now()})
        formset = LigneFactureFormSet(prefix='lignes')

    context = {
        'facture_form': facture_form,
        'formset': formset,
    }
    return render(request, 'gestion_produits_stock/interface_vente.html', context)


def modifier_vente(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    
    if request.method == 'POST':
        facture_form = FactureForm(request.POST, instance=facture, prefix='facture')
        formset = LigneFactureFormSet(request.POST, instance=facture, prefix='lignes')
        
        try:
            with transaction.atomic():
                if facture_form.is_valid() and formset.is_valid():
                    facture_form.save()
                    
                    # Récupérer les lignes de facture existantes pour annuler les mouvements de stock
                    lignes_existantes = {ligne.pk: ligne for ligne in facture.lignes_facture.all()}
                    
                    # Préparer la liste des lignes de facture non supprimées
                    lignes_a_conserver = []

                    for form in formset:
                        if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                            lignes_a_conserver.append(form.cleaned_data)

                    # Restaurer le stock pour les lignes existantes et vérifier le stock pour les nouvelles lignes
                    for ligne_existante_pk, ligne_existante in lignes_existantes.items():
                        # Si la ligne n'est pas dans les données du formset (soit elle a été supprimée, soit son contenu a changé), on restaure le stock
                        stock_principal = Stock.objects.get(produit=ligne_existante.produit, lieu_stockage__nom="Principal")
                        stock_principal.quantite += ligne_existante.quantite
                        stock_principal.save()

                    # Supprimer les mouvements de stock précédents pour cette facture
                    StockMovement.objects.filter(
                        description=f"Vente (Facture #{facture.id})",
                        type_mouvement='SORTIE'
                    ).delete()

                    # Sauvegarder les nouvelles lignes, mettre à jour le stock et créer les nouveaux mouvements
                    montant_total = Decimal('0.00')
                    for form in formset:
                        if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                            ligne_facture = form.save(commit=False)
                            ligne_facture.facture = facture
                            
                            produit = ligne_facture.produit
                            quantite = ligne_facture.quantite
                            
                            # Vérifier le stock après restauration
                            stock_principal = Stock.objects.get(produit=produit, lieu_stockage__nom="Principal")
                            if stock_principal.quantite < quantite:
                                messages.error(request, f"Quantité insuffisante pour le produit {produit.nom}. Stock disponible : {stock_principal.quantite}.")
                                raise ValidationError("Stock insuffisant.")
                            
                            stock_principal.quantite -= quantite
                            stock_principal.save()

                            # Calculer le total_ligne avant de sauvegarder
                            ligne_facture.total_ligne = quantite * ligne_facture.prix_unitaire_negocie
                            ligne_facture.save()
                            
                            StockMovement.objects.create(
                                produit=produit,
                                lieu_stockage_source=stock_principal.lieu_stockage,
                                quantite=quantite,
                                type_mouvement='SORTIE',
                                description=f"Vente (Facture #{facture.id})"
                            )
                            
                            montant_total += ligne_facture.total_ligne

                    formset.save()
                    facture.montant_total = montant_total
                    facture.save()

                    messages.success(request, "Facture modifiée avec succès!")
                    return redirect('detail_facture', pk=facture.pk)
                else:
                    messages.error(request, "Erreur dans le formulaire. Veuillez vérifier les informations.")
                    print("Erreurs FactureForm:", facture_form.errors)
                    print("Erreurs Formset:", formset.errors)
        except ValidationError as e:
            print(f"Validation Error: {e}")
        except Exception as e:
            messages.error(request, "Une erreur inattendue est survenue lors de la modification de la facture.")
            traceback.print_exc()

    else:
        facture_form = FactureForm(instance=facture, prefix='facture')
        formset = LigneFactureFormSet(instance=facture, prefix='lignes')

    context = {
        'facture_form': facture_form,
        'formset': formset,
        'facture': facture,
    }
    return render(request, 'gestion_produits_stock/modifier_vente.html', context)


# --- API AJAX ---
def recherche_produit_ajax(request):
    query = request.GET.get('term', '')
    if query:
        produits = Produit.objects.filter(
            Q(nom__icontains=query) | Q(code_produit__icontains=query)
        )[:10]
        
        results = []
        for produit in produits:
            # Assurer que si aucun stock n'existe, la quantité soit 0
            stock_quantite = Stock.objects.filter(
                produit=produit, 
                lieu_stockage__nom="Principal"
            ).aggregate(qte=Coalesce(Sum('quantite'), Decimal('0.00')))['qte']
            
            results.append({
                'id': produit.id,
                'label': f"{produit.nom} ({produit.code_produit or 'N/A'}) - Stock: {stock_quantite}",
                'value': produit.nom,
                'prix_unitaire': float(produit.prix_unitaire),
                'stock_quantite': float(stock_quantite)
            })
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)

def get_product_stock_ajax(request):
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            produit = Produit.objects.get(pk=product_id)
            stock_quantite = Stock.objects.filter(
                produit=produit,
                lieu_stockage__nom="Principal"
            ).aggregate(qte=Coalesce(Sum('quantite'), Decimal('0.00')))['qte']
            
            return JsonResponse({'stock_quantite': float(stock_quantite)}, safe=False)
        except Produit.DoesNotExist:
            return JsonResponse({'error': 'Produit non trouvé'}, status=404)
    return JsonResponse({'error': 'ID de produit manquant'}, status=400)