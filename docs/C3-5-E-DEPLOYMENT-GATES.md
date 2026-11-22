# C3.5-E — Préparation du déploiement (NON ACTIVÉ)
Date : 22/11/2026

## Décision de sécurité
Le quota du fournisseur s'applique à la clé API **toutes compétitions confondues**. Le Worker utilise donc une clé de limitation globale `football-data:global`, plutôt qu'une limite distincte par compétition.

## Configuration prévue
- `FOOTBALL_DATA_TOKEN` : secret Cloudflare, jamais dans le dépôt.
- `ALLOWED_ORIGIN` : origine exacte de l'application GitHub Pages.
- `ALLOWED_COMPETITIONS` : liste explicite des compétitions réellement autorisées.
- `PROVIDER_ENABLED` : `false` jusqu'à validation finale.
- `RATE_LIMITER` : binding de limitation côté Cloudflare, global pour l'ensemble des compétitions.
- `/health` : répond sans appeler le fournisseur.
- `/v1/football/matches?competition=PL` : endpoint expérimental ; désactivé en l'absence de clé ou de limiteur.

## Vérifications indispensables avant publication
1. Tester le Worker hors ligne et confirmer les résultats GitHub Actions.
2. Confirmer dans la documentation Cloudflare le comportement réel et la granularité du rate-limit binding sur le plan gratuit ; ne pas supposer une garantie de quota strict. Prévoir une marge conservatrice, et si nécessaire un verrou/compteur plus strict.
3. Ajouter une protection contre l'usage public abusif, indépendamment de CORS ; CORS n'est pas une authentification.
4. Prévoir cache serveur et réponse conditionnelle pour limiter les appels répétés.
5. Vérifier les droits du fournisseur et les champs accessibles sur le plan gratuit.
6. Effectuer une revue de sécurité et un déploiement manuel contrôlé seulement après accord.

## État actuel
Code candidat enregistré ; aucune clé, aucun compte Cloudflare, aucun déploiement, aucune donnée sportive réelle collectée. Ne pas annoncer de test réussi sans résultat de CI confirmé.
