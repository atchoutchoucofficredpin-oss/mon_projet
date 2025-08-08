# C:\MON PROJET\gestion_produits_stock\templatetags\gestion_extras.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Permet d'accéder à un élément de dictionnaire par sa clé dans un template Django.
    Exemple: {{ my_dict|get_item:my_key }}
    """
    return dictionary.get(key)

