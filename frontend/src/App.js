// mon_logiciel_gestion/frontend/src/App.js

import React, { useState, useEffect } from 'react'; // <-- Assure-toi qu'il n'y a qu'une seule ligne d'import React
import './App.css';
import FacturesPage from './components/FacturesPage';
import TransfertStockPage from './components/TransfertStockPage'; // <-- NOUVEAU : Importe la page de Transfert de Stock

function App() { // <-- Assure-toi que la fonction App() n'est définie qu'une seule fois
  const nomEntreprise = "Ma Grande Entreprise de Gestion";

  const [produits, setProduits] = useState([]);
  const [clients, setClients] = useState([]);
  const [erreur, setErreur] = useState(null);
  const [vueActuelle, setVueActuelle] = useState('produits'); // État pour gérer la vue (produits, clients, factures)

  // Effet pour récupérer les produits
  useEffect(() => {
    const fetchProduits = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/produits/');
        if (!response.ok) {
          throw new Error(`Erreur HTTP: ${response.status}`);
        }
        const data = await response.json();
        setProduits(data);
      } catch (error) {
        console.error("Erreur lors de la récupération des produits:", error);
        setErreur("Impossible de charger les produits. Veuillez réessayer plus tard.");
      }
    };
    fetchProduits();
  }, []); // S'exécute une seule fois au montage

  // Effet pour récupérer les clients
  useEffect(() => {
    const fetchClients = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/clients/');
        if (!response.ok) {
          throw new Error(`Erreur HTTP: ${response.status}`);
        }
        const data = await response.json();
        setClients(data);
      } catch (error) {
        console.error("Erreur lors de la récupération des clients:", error);
        setErreur("Impossible de charger les clients. Veuillez réessayer plus tard.");
      }
    };
    fetchClients();
  }, []); // S'exécute une seule fois au montage

  return ( // <-- Assure-toi que ce return est bien à l'intérieur de la fonction App()
    <div className="App">
      <header className="App-header">
        <h1>{nomEntreprise}</h1>
        <p>Logiciel de Gestion Intégrée</p>
        <nav>
          <button onClick={() => setVueActuelle('produits')}>Produits</button>
          <button onClick={() => setVueActuelle('clients')}>Clients</button>
          <button onClick={() => setVueActuelle('factures')}>Factures</button>
          <button onClick={() => setVueActuelle('transferts')}>Transferts de Stock</button> {/* NOUVEAU BOUTON */}
        </nav>
      </header>

      <main className="App-main">
        {erreur && <p className="erreur">{erreur}</p>}

        {/* Affichage conditionnel basé sur la vueActuelle */}
        {vueActuelle === 'produits' && (
          <>
            <h2>Nos Produits</h2>
            {!erreur && produits.length === 0 && <p>Chargement des produits ou aucun produit disponible...</p>}
            {produits.length > 0 && (
              <div className="liste-elements">
                {produits.map(produit => (
                  <div key={produit.id} className="carte-element">
                    <h3>{produit.nom} (SKU: {produit.sku})</h3>
                    <p>{produit.description}</p>
                    <p>Prix de vente: {produit.prix_vente} €</p>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {vueActuelle === 'clients' && (
          <>
            <h2>Nos Clients</h2>
            {!erreur && clients.length === 0 && <p>Chargement des clients ou aucun client disponible...</p>}
            {clients.length > 0 && (
              <div className="liste-elements">
                {clients.map(client => (
                  <div key={client.id} className="carte-element">
                    <h3>{client.nom_complet}</h3>
                    <p>Email: {client.email}</p>
                    <p>Téléphone: {client.telephone}</p>
                    <p>Adresse: {client.adresse}</p>
                    {client.num_fiscal && <p>Numéro Fiscal: {client.num_fiscal}</p>}
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {vueActuelle === 'factures' && <FacturesPage />}
        {vueActuelle === 'transferts' && <TransfertStockPage />} {/* NOUVEAU COMPOSANT DE PAGE */}
      </main>

      <footer className="App-footer">
        <p>&copy; 2025 {nomEntreprise}. Tous droits réservés.</p>
      </footer>
    </div>
  );
}

export default App;
