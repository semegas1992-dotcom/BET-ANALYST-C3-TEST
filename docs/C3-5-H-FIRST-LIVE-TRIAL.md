# C3.5-H — Premier essai de collecte réelle : protocole contrôlé
Date : 22 novembre 2026
Statut : PRÉPARATION SEULEMENT — aucune activation

## Préconditions obligatoires
- Vérifier auprès du fournisseur les conditions d'utilisation pour l'application personnelle et la disponibilité de la compétition choisie.
- Vérifier la compatibilité de la configuration Cloudflare Workers, de son rate limiter et de son cache KV sur l'offre retenue.
- Ne jamais inscrire la clé `FOOTBALL_DATA_TOKEN` dans GitHub, dans l'interface Android, dans une URL ou dans une conversation.
- Déployer un Worker de test isolé, avec `PROVIDER_ENABLED=false` par défaut.
- Fixer `ALLOWED_ORIGIN` à l'origine exacte du site et `ALLOWED_COMPETITIONS` à une liste minimale.
- Confirmer une protection anti-abus indépendante de CORS ; CORS ne constitue pas un contrôle d'accès.
- Ne pas supposer que le rate limiter natif garantit à lui seul un quota global strict entre régions : vérifier et renforcer si nécessaire.
- Le cache de cinq minutes réduit les appels répétés, mais ne garantit pas l'absence d'appels simultanés (cache stampede).
- Confirmer que le fournisseur autorise la conservation temporaire des réponses.

## Déroulement prévu (à effectuer uniquement après validation)
1. Vérifier `/health` : il doit répondre `provider_connected:false`, même avant activation.
2. Vérifier les réponses de blocage sans clé, sans limiteur et sans cache.
3. Configurer les bindings, l'origine, la liste de compétitions et le secret via l'interface privée Cloudflare.
4. Activer temporairement le fournisseur pour **une seule compétition** et effectuer une requête manuelle contrôlée.
5. Contrôler la structure des rencontres, la date de récupération, le statut `RECEIVED_UNVERIFIED` et la non-divulgation du secret.
6. Répéter une demande pour vérifier `cache:HIT` et l'absence de nouvel appel externe.
7. Désactiver de nouveau le fournisseur après l'essai, analyser les erreurs et les limites de couverture.

## Critères de réussite
- Aucun secret exposé.
- Aucune donnée présentée comme vérifiée sans preuve indépendante.
- Aucun marché sportif, probabilité, composition ou absence inventés.
- Quota et coûts surveillés ; les appels doivent être bloqués si les protections sont indisponibles.
- Les données ne suffisant pas à KRAFT V3.0 restent explicitement manquantes.

## Limites connues
Le Worker ne récupère actuellement que les rencontres et leurs champs basiques. Il limite la réponse à 100 rencontres et ne gère pas la pagination ; une réponse tronquée ne doit jamais être présentée comme exhaustive. La couche d'authentification et l'anti-abus public restent à concevoir. Aucun déploiement n'est autorisé par ce document.

## Décision
Continuer les essais hors ligne et la revue de sécurité. Ne pas demander d'action Android ni d'inscription fournisseur avant que la configuration minimale soit réellement prête.
