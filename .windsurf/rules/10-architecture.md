---
description: Contraintes d'architecture pour harvis-windsurf-mvp
---

# 10 — Architecture

- **Langage** : Python ≥ 3.11. Annotations de types obligatoires partout.
- **Formatage** : Black. **Lint** : Ruff.
- **Tests** : pytest, sous `tests/` en miroir de `src/`.
- **Source** : sous `src/`. Pas de logique dans les scripts racine.
- **Dépendances** : gérées dans `pyproject.toml`. Pas de `pip install` ad hoc.
- **Scripts Bash** : idempotents, `set -euo pipefail` obligatoire, log horodaté.
- **Scripts Python** : `--dry-run` / `--apply` obligatoires pour toute action mutante.
- Pas d'imports circulaires. Pas d'état global mutable.
- Pas de `print()` de debug laissé en production — utiliser `logging`.
