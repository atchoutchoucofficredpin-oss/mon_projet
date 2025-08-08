from django.shortcuts import render

# C:\MON PROJET\interface_vente\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from decimal import Decimal

# Importez vos modèles depuis l'application gestion_produits_stock
from gestion_produits_stock.models import Produit, Client, Facture, LigneFacture, Stock

def creer_vente(request):
    if request.method == 'POST':
        # Logique pour traiter le formulaire de vente (création de facture et lignes)
        client_id = request.POST.get('client')
        produits_data = []
        # Récupérer les données de produits depuis le formulaire
        # Les noms des champs seront comme 'produit_id_0', 'quantite_0', 'prix_0', etc.
        i = 0
        while True:
            produit_id = request.POST.get(f'produit_id_{i}')
            quantite = request.POST.get(f'quantite_{i}')
            prix_unitaire_vendu = request.POST.get(f'prix_unitaire_vendu_{i}')

            if not produit_id: # Si plus de produit_id, on a fini
                break

            try:
                produits_data.append({
                    'produit_id': int(produit_id),
                    'quantite': int(quantite),
                    'prix_unitaire_vendu': Decimal(prix_unitaire_vendu)
                })
            except (ValueError, TypeError):
                # Gérer les erreurs de conversion si les données ne sont pas valides
                return render(request, 'interface_vente/creer_vente.html', {
                    'clients': Client.objects.all(),
                    'produits': Produit.objects.all(),
                    'error_message': "Données de produit invalides. Veuillez vérifier les quantités et les prix."
                })
            i += 1

        if not client_id:
            return render(request, 'interface_vente/creer_vente.html', {
                'clients': Client.objects.all(),
                'produits': Produit.objects.all(),
                'error_message': "Veuillez sélectionner un client."
            })

        try:
            with transaction.atomic(): # Assure que toutes les opérations réussissent ou échouent ensemble
                client = get_object_or_404(Client, id=client_id)
                facture = Facture.objects.create(client=client)

                for item_data in produits_data:
                    produit = get_object_or_404(Produit, id=item_data['produit_id'])
                    LigneFacture.objects.create(
                        facture=facture,
                        produit=produit,
                        quantite=item_data['quantite'],
                        prix_unitaire_vendu=item_data['prix_unitaire_vendu']
                    )
                # Les signaux post_save mettront à jour total_ht, total_ttc, etc.

            return redirect('detail_facture', facture_id=facture.id) # Redirige vers la page de détail de la facture
        except Exception as e:
            # Gérer les erreurs (ex: stock insuffisant via ValidationError de LigneFacture.save())
            error_message = str(e)
            if "Stock total insuffisant" in error_message:
                error_message = error_message.split("ValidationError: ")[-1] # Nettoyer le message
            return render(request, 'interface_vente/creer_vente.html', {
                'clients': Client.objects.all(),
                'produits': Produit.objects.all(),
                'error_message': error_message
            })

    # Si c'est une requête GET, afficher le formulaire vide
    clients = Client.objects.all()
    produits = Produit.objects.all()
    return render(request, 'interface_vente/creer_vente.html', {
        'clients': clients,
        'produits': produits
    })

def detail_facture(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    return render(request, 'interface_vente/detail_facture.html', {'facture': facture})

