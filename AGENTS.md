# AGENTS.md — Harvis Windsurf MVP

Ce dépôt est piloté par **Harvis**. Tout agent opérant ici doit respecter ce contrat sans exception.

## Règles fondamentales

1. **Task Packet obligatoire** — Toute tâche entrante doit être conforme au schéma `harvis:task-packet:v2`. Toute tâche non conforme est rejetée avant exécution.

2. **Scope strict** — Un agent ne touche que les chemins listés dans `scope.allowed_paths`. Toute modification d'un chemin dans `scope.forbidden_paths` est une violation critique. En cas de doute sur le scope, l'agent s'arrête et remonte `status: needs_clarification`.

3. **Result Packet obligatoire** — Toute sortie d'agent doit être conforme au schéma `harvis:result-packet:v2`. Absence de result packet valide = échec critique. Cela vaut aussi en cas d'erreur interne : produire `status: failed` avec `blockers` renseignés.

4. **Pas de "done" sans preuve** — Un résultat `completed` ou `completed_with_risks` exige : `changed_files` non vide, `checks` non vide, `next_step` renseigné. Le validateur `scripts/validate_task_result.py` fait autorité.

5. **Outputs requis déclarés dans la tâche** — Le champ `required_outputs` du task packet est contraignant. Tout champ listé doit être **présent (non null)** dans le result packet. Le caractère non-vide est imposé par les règles de cohérence de statut (voir règle 4 et `99-output-contract.md`).

6. **Pas de merge direct sur `main`** — Tout changement passe par une pull request. Aucune exception.

7. **Escalade obligatoire** — Si une condition `execution_policy.escalate_if` est rencontrée, l'agent s'arrête, produit `status: blocked` ou `needs_clarification`, et renseigne `needs_human_approval: true`.

## Agents enregistrés

Voir `.harvis/state/registry.json` pour la liste des agents actifs et leurs capacités.

## Routage et modèles

Voir `.harvis/state/routing-policy.yaml` et `.harvis/state/model-policy.yaml`.
