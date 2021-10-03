"""
API python qui permet de récupérer plusieurs informations d'école directe 
au moyen de requêtes http à l'API interne du site.

Si vous avez besoin d'aide ou trouvé un bug, n'hésitez pas à me le faire savoir 

INFORMATIONS DISPONIBLES (quand faites) :
-------------------
    - emploi du temps (en cours)
    - devoirs (à faire)
    - contenus de séance (à faire)
    - notes (à faire)

FONCTIONNEMENT
-------------------
    - 1 : récupération du token par l'authentification à école directe avec l'identifiant et le mot de passe
        - par l'init de la classe EcoleDirecte(username, password)
"""

__version__ = "0.2"
__author__ = "Merlet Raphaël"

from getpass import getpass # input pour mot de passe sécurisé
import json
import requests as req # module pour requêtes HTTP
from rich import print # print permettant de mieux voir les réponses json (dictionnaires)
from datetime import date

def create_week_days():
    """
    retourne un tuple avec la date du lundi et du dimanche de cette semaine au format AAAA-MM-JJ
    """
    # nombre de jour par mois (année non bissextile, dans l'ordre de janvier à décembre)
    JMOIS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    CDATE = date.today()
    offset_from_monday = CDATE.weekday()
    # find important number of day in the month (actual month or precedent month)
    jour_dans_mois = JMOIS[CDATE.month-1] if offset_from_monday < CDATE.day else JMOIS[CDATE.month-2]
    # create week days list
    week = [
        '{2}-{1}-{0}'.format(
            (CDATE.day + i) % jour_dans_mois + 1,
            (CDATE.month + 
                ((CDATE.day + i) // jour_dans_mois)) % 12,
            CDATE.year + 
                ((CDATE.month + ((CDATE.day + i) // jour_dans_mois)) // 12))
        for i in range(-(offset_from_monday+1), 6-offset_from_monday)
    ]
    # fills zeroes for day and month
    week = [
        '{}-{}-{}'.format(*[
            part.zfill(2) for part in day.split('-')
        ])
        for day in week
    ]
    print(week)
    return week[0], week[-1]

class EcoleDirecte():
    """
    Interface API d'EcoleDirecte
    """
    def __init__(self, username: str, password: str) -> None:
        """
        Permet de se connecter à école directe afin de récupérer le token, nécessaire afin de récupérer les infos
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
        data = {
            "identifiant": username,
            "motdepasse": password,
            "acceptationCharte": True
        }
        payload = 'data=' + json.dumps(data)
        # essai de requête au login d'école directe
        try:
            self.response = req.post(
                "https://api.ecoledirecte.com/v3/login.awp", 
                data=payload)
            self.json = self.response.json()
            with open("login.json", "w+", encoding="UTF-8") as file:    
                json.dump(self.json, file)
            #print(self.response)
            self.token = self.json['token']
            self.id = self.json["data"]["accounts"][0]["id"]
            self.response.raise_for_status()
        except Exception as e:
            if type(e).__name__ == "ConnectionError":
                print("[reverse bold red]La connexion a échoué[/]")
                print("[red]Vérifiez votre connexion Internet.[/]")
            else:
                print(f"Une erreur inconnue est survenue (identifiant ou mot de passe incorrect ?) : {e}")
    
    def fetch_schedule(self):
        """
        Retourne l'emploi du temps de la semaine sous la forme d'un dictionnaire au format {jour: listeCours[Cours]}
        """
        monday, sunday = create_week_days()
        data = {
            "token": self.token,
            "dateDebut": monday,
            "dateFin": sunday,
            "avecTrous": False,
        }
        payload = 'data=' + json.dumps(data)
        response = req.post("https://api.ecoledirecte.com/v3/E/" +
                    str(self.id) + "/emploidutemps.awp?verbe=get&", data=payload)
        responseJson = response.json()
        #print(responseJson)

if __name__=='__main__': # test
    print("===============================================================")
    print(f"EcoleDirecte API v{__version__}")
    print(f"Made by {__author__}")
    print("Source : https://github.com/Ilade-s/EcoleDirecte_API-Interface")
    print("===============================================================")

    username = input("username/nom d'utilisateur : ")
    password = getpass("password/mot de passe : ", )
    interface = EcoleDirecte(username, password)

    print("Connecté à :", interface.json["data"]["accounts"][0]["identifiant"])

    print("fetching schedule...")

    interface.fetch_schedule()
