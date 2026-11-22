# C3.5-K — Configuration Cloudflare : préparation sans activation
Date : 22 novembre 2026
Statut : CANDIDAT NON DÉPLOYÉ

## Architecture envisagée
GitHub Pages (interface publique) → Cloudflare Worker (proxy) → football-data.org.
La clé API ne doit jamais parvenir à GitHub Pages ou à l'appareil du visiteur.

## Variables et bindings nécessaires
| Nom | Nature | Exemple / règle |
|---|---|---|
| PROVIDER_ENABLED | variable | false par défaut |
| ALLOWED_ORIGIN | variable | https://semegas1992-dotcom.github.io (origine, sans chemin) |
| ALLOWED_COMPETITIONS | variable | PL (exemple, sous réserve des droits du fournisseur) |
| FOOTBALL_DATA_TOKEN | **secret** | configurer uniquement dans le gestionnaire de secrets Cloudflare, jamais dans GitHub |
| MATCH_CACHE | binding KV | espace de noms à créer après validation du plan et de la politique de conservation |
| RATE_LIMITER | binding de limitation | clé unique `football-data:global` ; valider configuration et portée effectives |

## Blocages de sécurité avant activation
1. Le Worker est public s'il est déployé tel quel. CORS **ne protège pas** les appels effectués hors navigateur. Il faut un mécanisme anti-abus réel et une politique d'accès adaptée au service public.
2. Le rate limiter Cloudflare ne doit pas être présumé strictement global entre régions ; le quota fournisseur exige une stratégie robuste. Un cache KV n'est pas un verrou distribué et des requêtes simultanées peuvent traverser le cache.
3. La durée de conservation de 300 secondes doit être compatible avec la licence du fournisseur.
4. Le Worker utilise `/v1/football/matches` ; il ne vérifie ni les données de jeu avancées ni les effectifs, et limite la liste à 100 rencontres avec `truncated:true` au-delà.
5. Confirmer la disponibilité et les limites gratuites de Cloudflare Workers, KV et rate limiting au moment de la création ; ne pas déclarer le coût garanti à 0 € sans vérification.
6. Valider les tests CI du dernier commit avant tout déploiement.
7. Préparer des alertes d'erreur et une désactivation rapide.

## Ordre de mise en place (plus tard, avec l'utilisateur)
1. Vérifier les conditions et les quotas officiels des services.
2. Choisir la protection anti-abus et le mécanisme de quota global.
3. Créer les ressources Cloudflare requises dans le compte de l'utilisateur.
4. Déployer en mode `PROVIDER_ENABLED=false` ; tester `/health` et les erreurs de configuration.
5. Installer le secret en privé, sans le transmettre dans la conversation.
6. Activer temporairement une compétition pour un test réel contrôlé, puis désactiver.

## Décision C3.5-K
Ne pas créer de compte, de secret ou de ressource payante automatiquement. Ne pas modifier la version stable C3.4. Ce document n'autorise pas la mise en production.
