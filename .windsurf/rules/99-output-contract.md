---
description: Contrat de sortie — ce que chaque agent doit obligatoirement produire
---

# 99 — Output Contract

Toute exécution d'agent DOIT produire un result packet JSON valide conforme à `harvis:result-packet:v2`.

## Champs obligatoires (toujours)

- `task_id` — identique au task packet d'entrée
- `status` — parmi `completed | completed_with_risks | blocked | failed | needs_clarification | out_of_scope`
- `summary` — résumé lisible non vide
- `changed_files` — liste (peut être vide pour `blocked`, `needs_clarification`, `out_of_scope`)
- `checks` — liste (non vide si `completed` ou `completed_with_risks`)
- `assumptions` — liste (peut être vide)
- `risks` — liste (peut être vide)
- `blockers` — liste (peut être vide)
- `needs_human_approval` — booléen
- `next_step` — chaîne non vide

## Règles de cohérence enforced par le validateur

| status                  | changed_files | checks   | blockers | risks    |
|-------------------------|---------------|----------|----------|----------|
| `completed`             | non vide      | non vide | vide     | —        |
| `completed_with_risks`  | non vide      | non vide | —        | non vide |
| `blocked`               | —             | —        | non vide | —        |
| `failed`                | —             | —        | ou risks non vides      |
| `out_of_scope`          | —             | —        | ou risks non vides      |

## Dépôt et validation

- Fichier : `.harvis/results/<task_id>-result.json`
- Validation : `python scripts/validate_task_result.py --task <task_id>`
- **Absence de result packet valide = échec critique de l'agent.**
