"""
API python qui permet de récupérer plusieurs informations d'école directe 
au moyen de requêtes http à l'API interne du site.

Si vous avez besoin d'aide ou trouvé un bug, n'hésitez pas à me le faire savoir 

INFORMATIONS DISPONIBLES :
-------------------
    - devoirs
    - contenu de séance
    - notes

FONCTIONNEMENT
-------------------
    - 1 : récupération du token par l'authentification à école directe avec l'identifiant et le mot de passe
        - par la classe Login(username, password)
"""

__version__ = "0.1"
__author__ = "Merlet Raphaël"

from getpass import getpass # input pour mot de passe sécurisé
#import requests # module pour requêtes HTTP
from requests import request as req # fonction de requête
from rich import print # print permettant de mieux voir les réponses json (dictionnaires)
from urllib.parse import quote_plus # permet des quotes dans le mot de passe

class Login():
    """
    Permet de se connecter à école directe afin de récupérer le token, nécèssaire afin de récupérer les infos
    """
    def __init__(self, username: str, password: str) -> None:
        """
        A UTILISER EN PARAMETRE DES AUTRES FONCTIONS
        ----------

        Envoie une requête HTTP à école directe afin de s'authentifier et récupérer le token.
        L'objet ainsi obtenu devra ensuite être donné en paramètre dans les fonctions de récupération.

        PARAMETRES : 
        ----------
            - username : str
                - nom d'utilisateur/de compte école directe
            - password : str
                - mot de passe
        
        SORTIE :
        ----------
            - Aucune
        """
        # Création payload
        payload = 'data={ "identifiant": "' + username + \
                '", "motdepasse": "' + password + '", "acceptationCharte": true }'
        # essai de requête au login d'école directe
        try:
            self.response = req(
                "POST", "https://api.ecoledirecte.com/v3/login.awp", 
                data=quote_plus(payload)).json()
            #print(self.response)
            self.token = self.response['token']
            if not self.token: # Vérif si token est vide = échec login (mdp ou id incorrect)
                raise(Exception)
            if self.response["code"] != 200: # Vérif si échec login dû à autre chose
                raise(Exception)
        except Exception as exception:
            if type(exception).__name__ == "ConnectionError":
                print("[reverse bold red]La connexion a échoué[/]")
                print("[red]Vérifiez votre connexion Internet.[/]")
            else:
                print("Une erreur inconnue est survenue (identifiant ou mot de passe incorrect ?)")

if __name__=='__main__': # test
    print("===============================================================")
    print(f"Productivity App v{__version__}")
    print(f"Made by {__author__}")
    print("Source : https://github.com/Ilade-s/EcoleDirecte_API-Interface")
    print("===============================================================")

    username = input("username/nom d'utilisateur : ")
    password = getpass("password/mot de passe : ", )
    tokenObj = Login(username, password)

    print("Connecté à :",tokenObj.response["data"]["accounts"][0]["identifiant"])
