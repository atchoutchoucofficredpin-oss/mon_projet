// mon_logiciel_gestion/frontend/src/components/TransfertStockPage.js

import React, { useState, useEffect } from 'react';

function TransfertStockPage() {
  const [produits, setProduits] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [lieuxStockage, setLieuxStockage] = useState([]); // Nouveau: pour stocker les lieux de stockage
  const [transferts, setTransferts] = useState([]);
  const [erreur, setErreur] = useState(null);
  const [messageSucces, setMessageSucces] = useState(null);
  const [chargement, setChargement] = useState(true);

  // États pour le formulaire de transfert
  const [selectedProduit, setSelectedProduit] = useState('');
  const [selectedStockSource, setSelectedStockSource] = useState('');
  const [selectedStockDestination, setSelectedStockDestination] = useState('');
  const [quantiteTransfert, setQuantiteTransfert] = useState('');
  const [descriptionTransfert, setDescriptionTransfert] = useState('');

  // Fonctions pour récupérer les données nécessaires
  const fetchData = async () => {
    setChargement(true);
    setErreur(null);
    try {
      // Récupérer les produits
      const produitsRes = await fetch('http://localhost:8000/api/produits/');
      if (!produitsRes.ok) throw new Error(`Erreur produits: ${produitsRes.status}`);
      const produitsData = await produitsRes.json();
      setProduits(produitsData);

      // Récupérer les lieux de stockage
      const lieuxRes = await fetch('http://localhost:8000/api/lieux_stockage/');
      if (!lieuxRes.ok) throw new Error(`Erreur lieux de stockage: ${lieuxRes.status}`);
      const lieuxData = await lieuxRes.json();
      setLieuxStockage(lieuxData); // Stocke les lieux

      // Récupérer les stocks (détails complets avec le nom du produit et du lieu de stockage)
      const stocksRes = await fetch('http://localhost:8000/api/stocks/');
      if (!stocksRes.ok) throw new Error(`Erreur stocks: ${stocksRes.status}`);
      const stocksData = await stocksRes.json();
      setStocks(stocksData);

      // Récupérer les transferts existants
      const transfertsRes = await fetch('http://localhost:8000/api/transferts/');
      if (!transfertsRes.ok) throw new Error(`Erreur transferts: ${transfertsRes.status}`);
      const transfertsData = await transfertsRes.json();
      setTransferts(transfertsData);

    } catch (error) {
      console.error("Erreur lors du chargement des données:", error);
      setErreur(`Impossible de charger les données : ${error.message}`);
    } finally {
      setChargement(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Filtrer les stocks de destination pour exclure le stock source et les stocks de produits différents
  const filteredStockDestinations = stocks.filter(
    stock => stock.id !== parseInt(selectedStockSource) &&
             (selectedProduit ? stock.produit.id === parseInt(selectedProduit) : false) // Le produit doit correspondre
  );

  // Filtrer les stocks sources pour afficher uniquement ceux qui ont le produit sélectionné
  const filteredStockSources = stocks.filter(
    stock => selectedProduit ? stock.produit.id === parseInt(selectedProduit) : false
  );

  const handleTransfertSubmit = async (e) => {
    e.preventDefault();
    setErreur(null);
    setMessageSucces(null);

    if (!selectedProduit || !selectedStockSource || !selectedStockDestination || !quantiteTransfert) {
      setErreur("Veuillez remplir tous les champs obligatoires (Produit, Source, Destination, Quantité).");
      return;
    }
    if (parseInt(selectedStockSource) === parseInt(selectedStockDestination)) {
      setErreur("Le stock source et le stock de destination ne peuvent pas être les mêmes.");
      return;
    }
    if (parseInt(quantiteTransfert) <= 0) {
      setErreur("La quantité de transfert doit être supérieure à zéro.");
      return;
    }

    const sourceStockObj = stocks.find(s => s.id === parseInt(selectedStockSource));
    if (sourceStockObj && parseInt(quantiteTransfert) > sourceStockObj.quantite) {
      setErreur(`Quantité insuffisante dans le stock source. Disponible: ${sourceStockObj.quantite}.`);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/transferts/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          produit_id: parseInt(selectedProduit), // Utilise produit_id
          stock_source_id: parseInt(selectedStockSource), // Utilise stock_source_id
          stock_destination_id: parseInt(selectedStockDestination), // Utilise stock_destination_id
          quantite: parseInt(quantiteTransfert),
          description: descriptionTransfert,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        let errorMessage = "Erreur lors de l'enregistrement du transfert.";
        if (errorData && typeof errorData === 'object') {
          errorMessage = Object.values(errorData).flat().join(' ; ');
        } else if (errorData) {
          errorMessage = errorData.toString();
        }
        throw new Error(errorMessage);
      }

      setMessageSucces("Transfert de stock enregistré avec succès !");
      setSelectedProduit('');
      setSelectedStockSource('');
      setSelectedStockDestination('');
      setQuantiteTransfert('');
      setDescriptionTransfert('');
      fetchData(); // Recharger les données
    } catch (error) {
      console.error("Erreur lors de la soumission du transfert:", error);
      setErreur(`Erreur : ${error.message || "Une erreur inconnue est survenue."}`);
    }
  };

  if (chargement) {
    return <p>Chargement des données de stock et produits...</p>;
  }

  return (
    <div className="transfert-stock-page">
      <h2>Transferts de Stock</h2>

      <form onSubmit={handleTransfertSubmit} className="form-transfert">
        <h4>Effectuer un nouveau transfert</h4>
        <label>
          Produit:
          <select
            value={selectedProduit}
            onChange={(e) => {
              setSelectedProduit(e.target.value);
              setSelectedStockSource('');
              setSelectedStockDestination('');
            }}
            required
          >
            <option value="">Sélectionnez un produit</option>
            {produits.map(produit => (
              <option key={produit.id} value={produit.id}>{produit.nom} (SKU: {produit.sku})</option>
            ))}
          </select>
        </label>

        <label>
          Stock Source:
          <select
            value={selectedStockSource}
            onChange={(e) => setSelectedStockSource(e.target.value)}
            required
            disabled={!selectedProduit}
          >
            <option value="">Sélectionnez un stock source</option>
            {filteredStockSources.length > 0 ? (
              filteredStockSources.map(stock => (
                <option key={stock.id} value={stock.id}>{stock.lieu_stockage.nom} (Quantité: {stock.quantite})</option>
              ))
            ) : (
              <option value="" disabled>Aucun stock disponible pour ce produit.</option>
            )}
          </select>
        </label>

        <label>
          Stock Destination:
          <select
            value={selectedStockDestination}
            onChange={(e) => setSelectedStockDestination(e.target.value)}
            required
            disabled={!selectedProduit || !selectedStockSource}
          >
            <option value="">Sélectionnez un stock destination</option>
            {filteredStockDestinations.length > 0 ? (
              filteredStockDestinations.map(stock => (
                <option key={stock.id} value={stock.id}>{stock.lieu_stockage.nom} (Quantité: {stock.quantite})</option>
              ))
            ) : (
              <option value="" disabled>Aucun autre stock disponible pour ce produit.</option>
            )}
          </select>
        </label>

        <label>
          Quantité:
          <input
            type="number"
            value={quantiteTransfert}
            onChange={(e) => setQuantiteTransfert(e.target.value)}
            min="1"
            required
          />
        </label>

        <label>
          Description (optionnel):
          <textarea
            value={descriptionTransfert}
            onChange={(e) => setDescriptionTransfert(e.target.value)}
            rows="3"
          ></textarea>
        </label>

        {erreur && <p className="erreur">{erreur}</p>}
        {messageSucces && <p className="message-succes">{messageSucces}</p>}

        <div className="form-actions">
          <button type="submit">Effectuer le Transfert</button>
        </div>
      </form>

      <hr />

      <h3>Historique des Transferts</h3>
      {transferts.length === 0 ? (
        <p>Aucun transfert de stock enregistré.</p>
      ) : (
        <div className="liste-elements">
          {transferts.map(t => (
            <div key={t.id} className="carte-element">
              <h4>{t.produit.nom} ({t.quantite} unités)</h4>
              <p>De: {t.stock_source.lieu_stockage.nom}</p> {/* Utilise le nom du lieu */}
              <p>À: {t.stock_destination.lieu_stockage.nom}</p> {/* Utilise le nom du lieu */}
              <p>Date: {new Date(t.date_transfert).toLocaleString()}</p>
              {t.description && <p>Description: {t.description}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TransfertStockPage;
