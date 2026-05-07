# harvis-windsurf-mvp

Socle de gouvernance de tâches pour l'architecture **Harvis ↔ WindSurf**.

Le projet formalise une façon propre de faire travailler Harvis/OpenClaw et WindSurf ensemble :

- **Harvis/OpenClaw** prépare, cadre, route et vérifie les tâches.
- **WindSurf** exécute dans un workspace de code avec des règles explicites.
- **Git, tests et artefacts** servent de couche de preuve.

Toute tâche est définie par un **task packet** (contrat d'entrée, YAML) et produit un **result packet** (preuve d'exécution, JSON). Le validateur croise les deux et garantit la cohérence du protocole.

---

## Finalité

L'objectif n'est pas une simple intégration IDE. Le MVP sert à construire un modèle durable :

```text
intention Harvis
  → task packet borné
  → exécution WindSurf
  → result packet vérifiable
  → tests / diff / artefacts
  → consolidation Harvis
```

Ce cadre permet de garder :

- un scope clair ;
- des chemins autorisés/interdits ;
- des critères d'acceptation explicites ;
- une preuve de validation après exécution ;
- une continuité exploitable entre sessions.

---

## Workflow opératoire

1. **Créer ou choisir une tâche**
   - Définir un objectif court.
   - Fixer les chemins autorisés/interdits.
   - Définir les outputs attendus.

2. **Générer le task packet**

   ```bash
   python scripts/new_task.py \
     --task-id T-0003-my-task \
     --title "Mon titre" \
     --objective "Ce que l'agent doit accomplir."
   ```

3. **Exécuter dans WindSurf**
   - Ouvrir le workspace prévu.
   - Donner à WindSurf le contexte/ticket.
   - Laisser WindSurf produire les changements et preuves.

4. **Produire ou collecter le result packet**
   - Fichiers modifiés.
   - Checks exécutés.
   - Statut.
   - Risques ou limites.

5. **Valider**

   ```bash
   python scripts/validate_task_result.py --task T-0001-example
   ```

6. **Consolider**
   - Relire le diff.
   - Lancer les tests.
   - Committer seulement si le résultat est propre.

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
# Installer les dépendances de dev dans un venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Lancer les tests
pytest tests/ -v
```

Alternative rapide si l'environnement est déjà prêt :

```bash
pytest -q
```

---

## CI GitHub

La CI exécute sur Python 3.11 et 3.12 :

1. installation éditable avec extras dev ;
2. build `sdist` + `wheel` ;
3. tests `pytest`.

Workflow : `.github/workflows/ci.yml`

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

```text
.harvis/
  contracts/    — schémas JSON (task-packet, result-packet)
  tasks/        — task packets YAML
  results/      — result packets JSON
  state/        — registry, routing-policy, model-policy
.github/
  workflows/    — CI GitHub Actions
scripts/
  validate_task_result.py   — validateur CLI
  new_task.py               — scaffolder de task packets
tests/
  test_validate_task_result.py
  fixtures/     — cas invalides pour les tests
pyproject.toml
```

---

## Posture de sécurité

- Ne pas élargir le scope d'une tâche sans nouveau task packet.
- Ne pas considérer un résultat comme valide sans checks explicites.
- Préférer des commits petits, lisibles et vérifiables.
- Garder Harvis comme orchestrateur/consolidateur, pas comme simple passe-plat.
