# EcoleDirecte_API-Interface
Une interface python permettant de récupérer simplement des informations de l'API (devoirs, notes,...)
(voir documentation et code pour plus d'informations)

# Info : n'ayant plus accès à mon compte école directe (changement d'établissement), ce projet va certainement rester tel quel, ainsi, d'éventuels mise à jour de l'api ne pourront probablement pas être pris en compte 

# Fonctionnement :
## Login :
Pour commencer, vous devrez vous connecter à votre compte en utilisant votre nom d'utilisateur ainsi que votre mot de passe.

Pour cela, vous devrez initialiser la classe EcoleDirecte comme ceci :
```py
<variable> = EcoleDirecte(username: str, password: str (, save_json: bool))
```
Si la connexion est aboutie, vous pouvez ensuite vérifier quelques informations de connexion telles que :
```py
TokenDeConnexion = <variable>.token
ReponseHTTPConnexion = <variable>.response
Username = <variable>.response["data"]["accounts"][0]["identifiant"]
```
## Méthodes disponibles :
```py
<variable>.fetch_schedule() -> dict[str, list[dict]] # l'emploi du temps de cette semaine
<variable>.fetch_work((raw_data: bool)) -> list[dict] # liste des devoirs à faire
<variable>.fetch_grades() -> dict[matiere: str, dict] # dictionnaire des notes par période et par matière
```

