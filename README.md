# EcoleDirecte_API-Interface
Une interface python permettant de récupérer simplement des informations de l'API (devoirs, notes,...)

# Fonctionnement :
## Login :
Pour commencer, vous devrez vous connecter à votre compte en utilisant votre nom d'utilisateur ainsi que votre mot de passe.

Pour cela, vous devrez initialiser la classe Login comme-ceci :
```py
<variable> = Login(username: str, password: str)
```
Si la connexion est aboutie, vous pouvez ensuite vérifier quelques informations de connexion telles que :
```py
TokenDeConnexion = <variable>.token
ReponseHTTPConnexion = <variable>.response
Username = <variable>.token["data"]["accounts"][0]["identifiant"]
```
