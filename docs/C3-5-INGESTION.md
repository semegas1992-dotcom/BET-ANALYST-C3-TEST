# C3.5 — Collecte et traçabilité (candidat expérimental)

Objectif final : collecte automatique de données sportives pour FOOTBALL, TENNIS et NBA, sans saisie systématique.

## Portée de ce jalon

- Module local de normalisation de dossiers entrants et traçabilité des faits.
- États explicites : VERIFIED (déclaré par l'entrée avec référence et horodatage, non certifié), DECLARED, MISSING, CONFLICT, STALE.
- Détection des références et horodatages absents, doublons de clés, URLs non HTTPS.
- Aucune collecte réseau, aucune source intégrée, aucune analyse ou probabilité sportive automatique à ce stade.

## Avant intégration de sources

Évaluer chaque fournisseur pour : droits de réutilisation, licence et quotas, couverture des trois sports, fraîcheur, données d'effectifs et calendrier, accès navigateur (CORS), authentification et maintien à 0 €. Les sources non confirmées restent candidates, jamais présumées disponibles.

## Critères de passage à la collecte réelle

1. Source autorisée et testée pour un sport.
2. Connecteur séparé et tests d'erreur (absence, timeout, quota, conflit).
3. Traçabilité par champ et horodatage de collecte.
4. Revue humaine des informations manquantes avant toute conclusion sportive.
5. Aucun changement des versions C3.4 et précédentes.
