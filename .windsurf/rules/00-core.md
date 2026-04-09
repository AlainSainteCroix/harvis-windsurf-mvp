---
description: Règles fondamentales — s'appliquent à tous les agents et modèles du repo
---

# 00 — Core Rules

- Ce repo est gouverné par Harvis. Toujours respecter les contrats définis dans `.harvis/`.
- Ne jamais effectuer d'action en dehors du scope du task packet actif.
- Toujours produire un result packet conforme à `.harvis/contracts/result-packet.schema.json`.
- Ne jamais committer directement sur `main`. Toujours utiliser une branche feature + PR.
- Toute décision non triviale doit être tracée dans le champ `trace` du result packet.
- En cas de doute sur le scope, s'arrêter et remonter `status: skipped` avec explication.
