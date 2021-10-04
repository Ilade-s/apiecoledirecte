# EcoleDirecte_API-Interface
Une interface python permettant de récupérer simplement des informations de l'API (devoirs, notes,...)

# Fonctionnement :
## Login :
Pour commencer, vous devrez vous connecter à votre compte en utilisant votre nom d'utilisateur ainsi que votre mot de passe.

Pour cela, vous devrez initialiser la classe EcoleDirecte comme ceci :
```py
<variable> = EcoleDirecte(username: str, password: str)
```
Si la connexion est aboutie, vous pouvez ensuite vérifier quelques informations de connexion telles que :
```py
TokenDeConnexion = <variable>.token
ReponseHTTPConnexion = <variable>.response
Username = <variable>.response["data"]["accounts"][0]["identifiant"]
```
## Récupérer emploi du temps :
Pour récupérer l'emploi du temps de cette semaine, il vous suffit d'appeller fetch_schedule comme ceci :
```py
<variable>.fetch_schedule() -> dict[str, list[dict]]
```
(voir documentation et code pour plus d'informations)
