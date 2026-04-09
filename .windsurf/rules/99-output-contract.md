---
description: Contrat de sortie — ce que chaque agent doit obligatoirement produire
---

# 99 — Output Contract

## Validation en mode --task (ordre d'exécution)

1. Task packet YAML validé contre `task-packet.schema.json` (fail-fast — arrêt si invalide)
2. Result packet JSON validé contre `result-packet.schema.json`
3. Contrôles croisés task/result (task_id, scope, required_outputs, cohérence statut)

## Champs du result packet (tous obligatoires par le schéma)

- `task_id` — identique au task packet d'entrée
- `status` — parmi `completed | completed_with_risks | blocked | failed | needs_clarification | out_of_scope`
- `summary` — résumé lisible non vide
- `changed_files` — liste de chemins relatifs (peut être vide selon statut)
- `checks` — liste de vérifications `{name, status, detail?}` (non vide si `completed*`)
- `assumptions` — liste (vide autorisé)
- `risks` — liste (non vide selon statut)
- `blockers` — liste (non vide selon statut)
- `needs_human_approval` — booléen
- `next_step` — chaîne non vide

## required_outputs : présence vs non-vide

`required_outputs` dans le task packet = champs qui doivent être **présents (non null)**.
Le caractère non-vide est imposé par les règles de statut ci-dessous, pas par `required_outputs`.

## Règles de cohérence enforced par le validateur

| status                  | changed_files | checks   | blockers      | risks         |
|-------------------------|---------------|----------|---------------|---------------|
| `completed`             | non vide      | non vide | doit être vide | —            |
| `completed_with_risks`  | non vide      | non vide | —             | non vide      |
| `blocked`               | —             | —        | non vide      | —             |
| `failed`                | —             | —        | non vide ou risks non vide  ||
| `out_of_scope`          | —             | —        | non vide ou risks non vide  ||
| `needs_clarification`   | —             | —        | —             | —             |

## Dépôt et validation

- Fichier : `.harvis/results/<task_id>-result.json`
- Validation : `python scripts/validate_task_result.py --task <task_id>`
- **Absence de result packet valide = échec critique de l'agent.**
