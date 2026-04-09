---
description: Règles de test pour harvis-windsurf-mvp
---

# 20 — Testing

- Toute nouvelle fonction publique doit avoir au moins un test pytest.
- Les tests vivent dans `tests/` en miroir de la structure `src/`.
- Aucun test ne modifie l'état de production (pas d'écriture dans `.harvis/state/` en test).
- Utiliser des fixtures pytest, pas de chemins hardcodés.
- Exécuter `pytest tests/ -v` avant tout commit.
- Les tests de validation de schéma utilisent les fixtures de `.harvis/contracts/`.
- Un test qui passe avec un faux négatif est pire qu'un test absent — ne pas tester pour la forme.
