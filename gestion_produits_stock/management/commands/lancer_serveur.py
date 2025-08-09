# gestion_produits_stock/management/commands/lancer_serveur.py

from django.core.management.base import BaseCommand
from django.core.management.commands.runserver import Command as RunserverCommand
from io import StringIO
import sys

class Command(BaseCommand):
    help = "Lancement sécurisé du serveur en mode exécutable."

    def handle(self, *args, **options):
        # Création d'un flux de sortie temporaire pour éviter l'erreur de console
        stdout_temp = StringIO()
        
        # Redirection de la sortie standard
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        sys.stdout = stdout_temp
        sys.stderr = stdout_temp
        
        try:
            # Crée une instance de la commande runserver standard
            runserver_command = RunserverCommand(stdout=stdout_temp, stderr=stdout_temp)
            # Exécute la commande avec les options nécessaires
            runserver_command.run(addr='0.0.0.0', port='8000', use_reloader=False)
        finally:
            # Restauration de la sortie standard
            sys.stdout = original_stdout
            sys.stderr = original_stderr