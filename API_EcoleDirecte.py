"""
API python qui permet de récupérer plusieurs informations d'école directe 
au moyen de requêtes http à l'API interne du site.

Si vous avez besoin d'aide ou trouvé un bug, n'hésitez pas à me le faire savoir 

INFORMATIONS DISPONIBLES :
-------------------
    - emploi du temps
    - devoirs
    - notes (en cours)
    - contenus de séance (à faire)

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
from datetime import date # pour créer dates formatées
# modules pour décodage base64 en string
import base64
import html
import re
import io

def create_week_list() -> list[str]:
    """
    retourne une liste des jour de la semaine actuelle au format AAAA-MM-JJ
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
            ((CDATE.month + 
                ((CDATE.day + i) // jour_dans_mois)) % 12 
                    if (CDATE.month + ((CDATE.day + i) // jour_dans_mois)) != 12 else 12),
            CDATE.year + 
                (((CDATE.month + ((CDATE.day + i) // jour_dans_mois)) // 12 
                    if (CDATE.month + ((CDATE.day + i) // jour_dans_mois)) != 12 else 0)))
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
    return week

class EcoleDirecte():
    """
    Interface API d'EcoleDirecte
    """
    def __init__(self, username: str, password: str, save_json=False) -> None:
        """
        Permet de se connecter à école directe afin de récupérer le token, nécessaire afin de récupérer les infos de l'API
        ----------

        Envoie une requête HTTP à école directe afin de s'authentifier et récupérer le token.

        PARAMETRES : 
        ----------
            - username : str
                - nom d'utilisateur/de compte école directe
            - password : str
                - mot de passe
            - save_json : bool
                - si True, sauvegardera la réponse du login dans login.json (non nécessaire)
                - default = False
        
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
            print('response : ', self.json)
            if save_json:
                with io.open("login.json", "w+", encoding="UTF-8") as file:    
                    json.dump(self.json, file)

            self.response.raise_for_status()
            self.token = self.json['token']
            self.id = self.json["data"]["accounts"][0]["id"]
        except Exception as e:
            if type(e).__name__ == "ConnectionError":
                print("[reverse bold red]La connexion a échoué[/]")
                print("[red]Vérifiez votre connexion Internet.[/]")
            else:
                print(f"Une erreur inconnue est survenue (identifiant ou mot de passe incorrect ?) : {e}")
            exit()
    
    def fetch_schedule(self) -> dict[str, list[dict]]:
        """
        Retourne l'emploi du temps de la semaine sous la forme d'un dictionnaire au format {jour: listeCours[Cours]}
        pour chaque jour, la liste des cours sera triée dans l'ordre (du plus tôt au plus tard)

        PARAMETRES :
        ----------
            Aucun
        
        SORTIE :
        ----------
            - schedule : dict[str, list[dict]]
                - dictionnaire des jours de la semaine, avec la liste des cours de chaque jour dans l'ordre
        """
        week = create_week_list()
        data = { # payload for request
            "dateDebut": week[0], # monday
            "dateFin": week[-1], # sunday
            "avecTrous": False,
        }
        payload = 'data=' + json.dumps(data)
        response = req.post("https://api.ecoledirecte.com/v3/E/" +
                    str(self.id) + "/emploidutemps.awp?verbe=get&", data=payload, headers=self.header)
        responseJson = response.json()
        self.token = responseJson["token"]
        coursList = responseJson['data']
        # create schedule dictionnary
        def get_key(course):
            hour, minutes = course['start_date'].split(' ')[1].split(':')
            value = int(hour) * 60 + int(minutes)
            return value

        schedule = {day: sorted([course for course in coursList if day in course['start_date']], key=get_key)
            for day in week 
        }

        return schedule
    
    def fetch_work(self, raw_data=False) -> list[dict]:
        """
        Retourne la liste des devoirs donnés, sous la forme de dictionnaires formatés/simplifiés ou non.

        Peut prendre quelques secondes à s'exécuter (décodage de base64 assez long)

        PARAMETRES :
        ----------
            - raw_data : bool
                - si vrai, les dictionnaires des devoirs continendront toutes les informations reçues par la réponse de l'API + la description
                - sinon, les devoirs seront simplifiés : 'matiere', 'effectue', 'date' et 'description' uniquement
        
        SORTIE :
        ----------
            - work : list[dict[str, str]]
                - liste des devoirs à faire

        """
        def format_data(data):
            """Format the tasks and adds it their description
            task format : raw if raw_data flag is set else dict[matiere, effectue, date; description]"""
            tasks = []
            for date in data.keys(): # each date, which is the key for the works for each day
                # send a request for the day to get the description for each work
                rtask = req.post("https://api.ecoledirecte.com/v3/Eleves/" +
                    str(self.id) + f"/cahierdetexte/{date}.awp?verbe=get&", data=payload, headers=self.header).json()
                devoirs = rtask["data"]["matieres"]
                # Sort the response to keep only the work and nothing else
                devoirs = [task for task in devoirs if "aFaire" in task.keys()]
                for task in devoirs: # each work of the day
                    # get the description
                    a = base64.b64decode(task["aFaire"]["contenu"])
                    descriptionHTML = a.decode("UTF-8")
                    description = html.unescape(descriptionHTML)
                    # Conversion Regex en string normale
                    desc = re.sub(r"<\/?[a-z]+>|\n", "", description)
                    # add the task to the list
                    if raw_data:
                        tasks.append({
                            **task, 
                            'description': desc
                            })
                    else:
                        tasks.append({
                            'matiere': task['matiere'], 
                            'effectue': task['aFaire']['effectue'],
                            'date': date,
                            'description': desc,
                            })
                    
            return tasks

        payload = 'data={}'
        rep = req.post("https://api.ecoledirecte.com/v3/Eleves/" +
                    str(self.id) + "/cahierdetexte.awp?verbe=get&", data=payload, headers=self.header)
        response = rep.json()
        self.token = response["token"]
        return format_data(response["data"])
    
    def fetch_grades(self, raw_data=False) -> dict[str]:
        """
        Renvoie un dictionnaire des notes, triées par période (semestre...), puis par matière (+ moyenne générale par période et par matière)
        
        PARAMETRE :
            - raw_data : bool
                - si vrai, renverra la réponse entière pour chaque note, sinon chaque objet-note contiendra uniquement :
                    - le nom
                    - la note obtenue et son coefficient
                    - la moyenne et la note minimale et maximale de la classe
                - default = False
        
        SORTIE :
            - Notes :
                - dict
                    - Période(str) : Matiere[
                        - average: float
                        - class_avg : float
                        - class_max : float
                        - class_min : float
                        - codeMatiere : dict
                            - sousMatiere:
                                - notes: list[dict[raw_dict ou
                                    - name: str, 
                                    - grade: float,
                                    - coef: float,
                                    - class_avg: float,
                                    - class_min: float,
                                    - class_max: float
        """
        payload = 'data={}'
        rep = req.post(f"https://api.ecoledirecte.com/v3/Eleves/" +
                    str(self.id) + "/notes.awp?verbe=get", data=payload, headers=self.header)
        response = rep.json()
        self.token = response["token"]
        data = response['data']

        code_mats = list(set([g['codeMatiere'] for g in data['notes']])) 
        matieres = {
            code: [
                    g['libelleMatiere'] 
                    for g in data['notes']
                    if g['codeMatiere'] == code
                    ] 
                for code in code_mats
            }


        def format_grade(grade: dict) -> dict:
            """to format grade if asked to do so, with name, grade, coef, and class avg/min/max"""
            return grade if raw_data else {
                'name': grade['devoir'],
                'grade': grade['valeur'],
                'coef': grade['coef'],
                'class_avg': grade['moyenneClasse'],
                'class_min': grade['minClasse'],
                'class_max': grade['maxClasse']
            } 

        notes = {}
        for p in data['periodes']:
            namep = p['periode']
            notes[namep] = {}
            for code, names in matieres.items():
                notes[namep][code] = {
                    matiere: [
                        format_grade(grade)
                        for grade in data['notes']
                        if grade['codePeriode'] == p['codePeriode']
                        and grade['codeMatiere'] == code
                        and grade['libelleMatiere'] == matiere
                        ]
                    for matiere in names
                }
            notes[namep]['average'] = p['ensembleMatieres']['moyenneGenerale']
            notes[namep]['class_avg'] = p['ensembleMatieres']['moyenneClasse']
            notes[namep]['class_max'] = p['ensembleMatieres']['moyenneMax']
            notes[namep]['class_min'] = p['ensembleMatieres']['moyenneMin']

        return notes
    
    @property
    def header(self):
        return {'X-Token': self.token}

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
    """
    print("fetching schedule...")

    schedule = interface.fetch_schedule()

    print(schedule)

    print('fetching work...')

    work = interface.fetch_work()

    print(work)
    """
    notes = interface.fetch_grades()

    print(notes)
