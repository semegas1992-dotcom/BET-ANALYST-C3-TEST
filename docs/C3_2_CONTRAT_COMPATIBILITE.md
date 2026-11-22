# BET ANALYST V3 — C3.2 — Contrat de compatibilité (candidat)

Statut : expérimental, non publié sur GitHub Pages. KRAFT V3.0 et les archives du LABORATOIRE restent inchangés.

## Invariants
- Schéma racine : `BET_ANALYST_CONSOLIDATION_V1`.
- Champs de marché C2 conservés : `id`, `label`, `period`, `threshold`, `evidence`, `status`.
- Les fiches sans extension doivent rester lisibles.
- Une catégorie inconnue reste `NON_RENSEIGNE`; ne jamais inférer une preuve vérifiée depuis un texte libre.
- Aucun marché ne devient automatiquement recommandé.

## Extension facultative de chaque marché
```json
{
  "c3_metadata": {
    "category": "NON_RENSEIGNE",
    "verified_evidence": [],
    "hypotheses": [],
    "missing_information": [],
    "review_status": "A_VERIFIER"
  }
}
```

Catégories : `COLLECTIF`, `INDIVIDUEL`, `NON_RENSEIGNE`.
Statuts de revue : `A_VERIFIER`, `DOCUMENTE`, `INCOMPLET`. `DOCUMENTE` ne constitue pas une certification sportive automatique.

## Critères d'acceptation
1. Import/export : les extensions doivent survivre à un aller-retour JSON.
2. Historique : sauvegarde/restauration sans perte des métadonnées.
3. Lecture seule : distinguer données déclarées, hypothèses, lacunes et catégorie inconnue.
4. Sécurité : aucune migration automatique ni effacement de données C2/C3.1.
5. Tests : fiche C2 sans extension, fiche C3.2 enrichie, champs invalides, marchés multiples, abstention.

## Point de vigilance
Le code C3.1 actuel reconstruit les marchés à l'import, à la validation et à la restauration ; ces chemins devront être adaptés ensemble avant toute activation de l'extension.
