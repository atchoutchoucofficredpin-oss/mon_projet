# C:\MON PROJET\app_bureau.py
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox, QGroupBox)
import requests # Pour faire des requêtes HTTP à votre API Django

class StockMovementApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Application de Gestion de Stock')
        self.setGeometry(100, 100, 600, 400) # x, y, largeur, hauteur

        self.api_base_url = 'http://127.0.0.1:8000/api/' # L'URL de votre API Django

        self.products = {} # Dictionnaire pour stocker {ID: Nom_Produit}
        self.locations = {} # Dictionnaire pour stocker {ID: Nom_Lieu}

        self.init_ui()
        self.load_data_from_api()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Groupement pour l'ajout de mouvement de stock
        movement_group_box = QGroupBox("Enregistrer un Mouvement de Stock")
        movement_layout = QVBoxLayout()

        # Produit
        product_layout = QHBoxLayout()
        product_layout.addWidget(QLabel("Produit:"))
        # ATTENTION : CORRECTION ICI -> self.product_combo au lieu de self_product_combo
        self.product_combo = QComboBox(self)
        product_layout.addWidget(self.product_combo)
        movement_layout.addLayout(product_layout)

        # Lieu de Stockage
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Lieu de Stockage:"))
        self.location_combo = QComboBox(self)
        location_layout.addWidget(self.location_combo)
        movement_layout.addLayout(location_layout)

        # Quantité
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Quantité:"))
        self.quantity_input = QLineEdit(self)
        self.quantity_input.setPlaceholderText("Ex: 10")
        quantity_layout.addWidget(self.quantity_input)
        movement_layout.addLayout(quantity_layout)

        # Type de Mouvement
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type de Mouvement:"))
        self.type_combo = QComboBox(self)
        # Ces types doivent correspondre aux CHOICES définis dans votre modèle StockMovement
        # dans models.py (TYPE_MOUVEMENT_CHOICES)
        self.type_combo.addItems(['ENTREE_ACHAT', 'SORTIE_VENTE', 'TRANSFERT', 'AJUSTEMENT_POSITIF', 'AJUSTEMENT_NEGATIF'])
        type_layout.addWidget(self.type_combo)
        movement_layout.addLayout(type_layout)

        # Description (optionnel)
        description_layout = QHBoxLayout()
        description_layout.addWidget(QLabel("Description:"))
        self.description_input = QLineEdit(self)
        self.description_input.setPlaceholderText("Détails du mouvement")
        description_layout.addWidget(self.description_input)
        movement_layout.addLayout(description_layout)

        # Bouton Enregistrer
        self.record_button = QPushButton('Enregistrer Mouvement', self)
        self.record_button.clicked.connect(self.record_stock_movement)
        movement_layout.addWidget(self.record_button)

        movement_group_box.setLayout(movement_layout)
        main_layout.addWidget(movement_group_box)

        # Espace pour d'autres fonctionnalités futures (comme la vérification de stock)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def load_data_from_api(self):
        """Charge les produits et les lieux de stockage depuis l'API Django."""
        try:
            # Charger les produits
            products_response = requests.get(f"{self.api_base_url}produits/")
            products_response.raise_for_status()
            for product in products_response.json():
                self.products[product['id']] = product['nom']
                self.product_combo.addItem(product['nom'], product['id'])

            # Charger les lieux de stockage
            locations_response = requests.get(f"{self.api_base_url}lieux-stockage/")
            locations_response.raise_for_status()
            for location in locations_response.json():
                self.locations[location['id']] = location['nom']
                self.location_combo.addItem(location['nom'], location['id'])

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Erreur de chargement des données",
                                 f"Impossible de charger les données depuis l'API: {e}\n"
                                 "Veuillez vous assurer que le serveur Django est en cours d'exécution.")

    def record_stock_movement(self):
        """Enregistre un nouveau mouvement de stock via l'API."""
        selected_product_id = self.product_combo.currentData()
        selected_location_id = self.location_combo.currentData()
        quantity_str = self.quantity_input.text()
        movement_type = self.type_combo.currentText()
        description = self.description_input.text()

        if not selected_product_id or not selected_location_id:
            QMessageBox.warning(self, "Données Manquantes", "Veuillez sélectionner un produit et un lieu de stockage.")
            return

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                QMessageBox.warning(self, "Quantité Invalide", "La quantité doit être un nombre positif.")
                return
        except ValueError:
            QMessageBox.warning(self, "Quantité Invalide", "La quantité doit être un nombre entier valide.")
            return

        # Construire les données à envoyer à l'API
        data = {
            'produit_id': selected_product_id,
            'lieu_stockage_id': selected_location_id,
            'quantite': quantity,
            'type_mouvement': movement_type,
            'description': description
        }

        try:
            response = requests.post(f"{self.api_base_url}mouvements-stock/", json=data)
            response.raise_for_status() # Lève une exception pour les codes d'état d'erreur HTTP

            QMessageBox.information(self, "Succès", "Mouvement de stock enregistré avec succès!")
            # Optionnel: Réinitialiser les champs après un enregistrement réussi
            self.quantity_input.clear()
            self.description_input.clear()

        except requests.exceptions.RequestException as e:
            error_message = f"Erreur lors de l'enregistrement du mouvement: {e}"
            if response.status_code == 400: # Bad Request, souvent dû à des erreurs de validation
                try:
                    error_details = response.json()
                    error_message += f"\nDétails: {error_details}"
                except ValueError:
                    pass # Pas de JSON dans la réponse
            QMessageBox.critical(self, "Erreur API", error_message)
        except Exception as e:
            QMessageBox.critical(self, "Erreur Inattendue", f"Une erreur inattendue est survenue: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StockMovementApp()
    ex.show()
    sys.exit(app.exec_())
