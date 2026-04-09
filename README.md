# harvis-windsurf-mvp

Socle de gouvernance de tâches pour l'architecture **Harvis/WindSurf**.

Toute tâche est définie par un **task packet** (contrat d'entrée, YAML) et produit un **result packet** (preuve d'exécution, JSON). Le validateur croise les deux et garantit la cohérence du protocole.

---

## Contrats

| Fichier | Rôle |
|---|---|
| `.harvis/contracts/task-packet.schema.json` | Scope autorisé, critères d'acceptation, outputs requis |
| `.harvis/contracts/result-packet.schema.json` | Fichiers modifiés, checks effectués, statut, risques |

Gouvernance : `AGENTS.md` · Règles WindSurf : `.windsurf/rules/`

---

## Lancer la validation

```bash
# Validation complète : task packet + result packet + contrôles croisés
python scripts/validate_task_result.py --task T-0001-example

# Schéma result seul
python scripts/validate_task_result.py --file .harvis/results/T-0001-example-result.json
```

Exit codes : `0` valide · `1` erreurs · `2` erreur système

---

## Lancer les tests

```bash
# Installer les dépendances (dans un venv ou avec --break-system-packages)
pip install jsonschema pyyaml pytest

# Lancer les tests
pytest tests/ -v
```

Sur Kali (environnement géré) :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Scaffolder une nouvelle tâche

```bash
python scripts/new_task.py \
  --task-id T-0003-my-task \
  --title "Mon titre" \
  --objective "Ce que l'agent doit accomplir."
```

Options utiles :

| Option | Rôle | Défaut |
|---|---|---|
| `--task-id` | ID de tâche (format `T-NNNN-slug`) | requis |
| `--title` | Titre court | requis |
| `--objective` | Objectif de la tâche | requis |
| `--allowed-path` | Pattern glob autorisé (répétable) | `scripts/**` |
| `--forbidden-path` | Pattern glob interdit (répétable) | liste standard |
| `--branch-name` | Branche git | `harvis/<task_id>` |
| `--dry-run` | Affiche le YAML sans écrire | — |
| `--force` | Écrase si le fichier existe déjà | — |

Le YAML généré est validé contre `task-packet.schema.json` avant écriture.

---

## Dépendances

| Paquet | Usage |
|---|---|
| `jsonschema >= 4.0` | Validation JSON Schema (task + result packets) |
| `pyyaml >= 6.0` | Chargement des task packets YAML |
| `pytest >= 7.0` | Tests automatiques (dev uniquement) |

Python >= 3.11 requis.

---

## Structure

```
.harvis/
  contracts/    — schémas JSON (task-packet, result-packet)
  tasks/        — task packets YAML
  results/      — result packets JSON
  state/        — registry, routing-policy, model-policy
scripts/
  validate_task_result.py   — validateur CLI
  new_task.py               — scaffolder de task packets
tests/
  test_validate_task_result.py
  fixtures/     — cas invalides pour les tests
pyproject.toml
```
