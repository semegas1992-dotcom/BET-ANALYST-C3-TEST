# C3.5-D — Proxy sécurisé expérimental
Statut : **code candidat non déployé**, aucune clé et aucune collecte réelle.

## Architecture
- GitHub Pages reste statique ; le Worker est un serveur séparé.
- Clé `FOOTBALL_DATA_TOKEN` dans **Cloudflare Secret**, jamais dans GitHub, le navigateur ou les logs.
- `ALLOWED_ORIGIN` = origine exacte de l'application ; `ALLOWED_COMPETITIONS` = liste explicite de compétitions autorisées ; `PROVIDER_ENABLED=true` uniquement après vérification des droits, du quota et des tests.
- CORS n'est **pas une authentification** et ne bloque pas les appels directs non-navigateurs. Avant publication, ajouter une protection contre les abus et une limitation de débit côté serveur. Le jeton du fournisseur pourrait autrement être utilisé indirectement par des tiers.
- Aucune URL arbitraire, aucun proxy générique ; réponse limitée à des champs de calendrier et résultats.
- Données reçues = `RECEIVED_UNVERIFIED`, à vérifier avant analyse.
- Les statistiques avancées et les effectifs ne sont pas inventés.
- Pas de déploiement automatique : validation manuelle et revue de sécurité indispensables.

## Conditions de passage
1. Vérifier les droits de réutilisation du fournisseur.
2. Confirmer les limites du plan gratuit et les compétitions autorisées.
3. Tester sécurité, erreurs, quotas, origine, cache et fraîcheur.
4. Créer un compte Cloudflare seulement quand l'activation est réellement nécessaire.
5. Ne jamais partager de jeton API dans ChatGPT ou GitHub.

Références : https://developers.cloudflare.com/workers/platform/limits/ et https://developers.cloudflare.com/workers/configuration/secrets/
