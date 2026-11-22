# C3.5-C — Sélection du premier fournisseur réel (22/11/2026)

## Candidat prioritaire : football-data.org (API v4)

Sources officielles :
- https://www.football-data.org/pricing
- https://docs.football-data.org/general/v4/policies.html
- https://www.football-data.org/documentation/api

La formule gratuite annoncée : 0 €/mois, 12 compétitions, rencontres/calendriers, résultats différés et classements, limite de 10 appels/minute. Vérifier la couverture réelle par compétition et la disponibilité de chaque champ au moment de l'intégration.

**Limite critique :** la formule gratuite ne couvre pas les statistiques avancées, compositions détaillées, tirs et autres données nécessaires à une analyse KRAFT exhaustive. Ces champs doivent rester MISSING, jamais déduits.

**Sécurité :** l'API utilise un jeton X-Auth-Token. Ne jamais l'inclure dans GitHub Pages, JavaScript public, URL, dépôt, logs ou fichier partagé. Un proxy/backend sécurisé ou un autre mécanisme sans exposition du jeton est nécessaire avant toute connexion effective. Ne pas demander au propriétaire de coller sa clé dans une conversation ou dans le dépôt.

**Statut :** candidat identifié et documentation officielle consultée. Aucune inscription, clé, connexion ni requête réelle effectuée. Les droits de réutilisation pour le cas d'usage doivent être confirmés avant activation.

## Alternative conditionnelle : football-data.co.uk

Politique officielle : https://football-data.co.uk/contact.php

Les téléchargements CSV sont autorisés pour recherche académique ou usage personnel, avec automatisation légère **au plus deux téléchargements par semaine**. Pas de collecte intensive, de scraping, ni de réutilisation pour projet commercial ou entraînement d'IA. Ne pas activer un connecteur automatique avant vérification que le projet personnel respecte ces conditions. Données principalement historiques, pas une source suffisante pour effectifs actuels et absences.

## Décision

1. Continuer les tests locaux sans secret et sans réseau.
2. Construire une interface de collecte avec statut explicite et sources par champ.
3. Ne connecter un fournisseur réel qu'après validation de la licence, de la couverture et d'une architecture protégeant les secrets.
4. Conserver C3.4 et versions précédentes intactes.
