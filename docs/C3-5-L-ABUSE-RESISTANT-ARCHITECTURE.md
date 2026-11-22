# C3.5-L — Décision d'architecture pour limiter les abus
Date : 22/11/2026
Statut : proposition expérimentale ; aucune activation

## Problème confirmé par revue du code
Le Worker expérimental accepte des requêtes GET sur `/v1/football/matches`. La vérification `Origin` / CORS n'est pas une authentification : un client hors navigateur peut omettre ou forger cet en-tête. La limitation de débit et le cache réduisent les appels mais ne prouvent pas que le quota du fournisseur sera respecté globalement.

## Choix recommandé pour V1 gratuite
**Collecte planifiée côté serveur, lecture publique d'un instantané statique.**
- Une tâche serveur contrôlée interroge le fournisseur selon une fréquence explicitement autorisée.
- Elle conserve un instantané JSON limité aux champs permis, horodaté, avec `provider`, `source_endpoint`, `coverage`, `truncated` et `status:RECEIVED_UNVERIFIED`.
- L'interface Android lit seulement cet instantané ; elle ne peut pas déclencher directement un appel à l'API payante ou limitée.
- En cas d'échec de collecte, afficher la date du dernier instantané et un avertissement de fraîcheur, sans inventer de rencontres.
- La tâche d'actualisation est désactivée par défaut et doit être validée selon les droits du fournisseur.

## Pourquoi ce choix
- Supprime le risque de consommation illimitée déclenchée par des visiteurs de l'application.
- Permet de contrôler le nombre de collectes et d'inspecter les données avant publication.
- Ne prétend pas garantir 0 € : les quotas, les licences, les éventuelles écritures KV et le déclencheur planifié doivent être vérifiés.
- La fréquence de rafraîchissement doit être adaptée aux droits d'utilisation et au besoin : un calendrier n'est pas du temps réel.

## Conséquences techniques
1. Conserver le Worker GET actuel comme prototype interne **non déployé**.
2. Ne pas exposer son endpoint fournisseur à l'application publique.
3. Concevoir un producteur d'instantanés, un stockage/serving statique et un contrat JSON versionné.
4. Tester hors ligne les cas : source indisponible, instantané ancien, réponse tronquée, absence de source, erreur de structure.
5. Vérifier les conditions de republication et de conservation de football-data.org avant toute publication publique.
6. Réserver une future API à la demande à une version ultérieure avec authentification et limitation robuste.

## Critères de passage à l'essai réel
- Accord sur l'architecture et vérification des licences/quotas gratuits.
- CI au vert sur le dernier commit.
- Aucune clé exposée dans le dépôt ni dans les instantanés.
- Aucun appel fournisseur depuis l'interface publique.
- Mode désactivé par défaut, possibilité d'arrêt immédiat.

**Décision :** privilégier un modèle `collecte planifiée → instantané → lecture seule` pour la première version gratuite. Ne pas déployer automatiquement.
